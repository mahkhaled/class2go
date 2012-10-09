from c2g.models import *
import json

def get_quiz_data(ready_quiz, get_video_visits = False):
    students_ = ready_course.student_group.user_set.all().values_list('id', 'username', 'first_name', 'last_name')
    students = {}
    for s in students_: students[s[0]] = {"username": s[1], "name": "%s %s" % (s[2], s[3])}
    
    mean = lambda k: sum(k)/len(k)
    
    is_video = isinstance(ready_quiz, Video)
    is_summative = (not is_video) and (ready_quiz.assessment_type == 'assessive')
    is_formative = (is_video) or (ready_quiz.assessment_type == 'formative')
    is_survey = (ready_quiz.assessment_type == 'survey')
    
    if is_summative:
        submissions_permitted = ready_quiz.submissions_permitted
        if submissions_permitted == 0: submissions_permitted = 100000
        resubmission_penalty = ready_quiz.resubmission_penalty/100.0
        grace_deadline = ready_quiz.grace_period
        if not grace_deadline: grace_deadline = ready_quiz.due_date
        partial_credit_deadline = ready_quiz.partial_credit_deadline
        late_penalty = ready_quiz.late_penalty / 100.0
        
    data = {}
    exercise_summaries = {}
    incorrect_response_freqs = {}
    
    if is_video: rlns = VideoToExercise.objects.filter(video=ready_quiz, is_deleted=0).order_by('video_time')
    else: rlns = ProblemSetToExercise.objects.filter(problemSet=ready_quiz, is_deleted=0).order_by('number')
    
    if is_video and get_video_visits:
        video_visits = PageVisitLog.objects.filter(page_type='video', object_id = str(ready_quiz.id)).order_by('user', 'time_created')
        for vv in video_visits:
            if not vv.user.username in data:
                stud_username = vv.user.username
                stud_fullname = vv.user.first_name + " " + vv.user.last_name
                data[vv.user.username] = {'username': stud_username, 'name': stud_fullname, 'visits':[], 'exercise_activity': {} 'total_score': 0, 'total_score_with_late_penalty': 0}
            data[vv.user.username]['visits'].append("%s-%s-%s at %s:%s" % (vv.time_created.year, vv.time_created.month, vv.time_created.day, vv.time_created.hour, vv.time_created.minute))

    ex_ids = []
    for rln in rlns:
        ex = rln.exercise
        ex_ids.append(ex.id)
        
        incorrect_response_freqs[ex.id] = {}
        
        if is_video:
            atts = ProblemActivity.objects.select_related('video', 'exercise').filter(video_to_exercise__exercise__fileName=ex.fileName, video_to_exercise__video=ready_quiz).order_by('student', 'time_created').values_list('student_id', 'complete', 'time_taken', 'attempt_content', 'time_created')
        else:
            atts = ProblemActivity.objects.select_related('problemSet', 'exercise').filter(problemset_to_exercise__exercise__fileName=ex.fileName, problemset_to_exercise__problemSet=ready_quiz).order_by('student', 'time_created').values_list('student_id', 'complete', 'time_taken', 'attempt_content', 'time_created')
        
        submitters = [item[0] for item in atts]
        completes = [item[1] for item in atts]
        times_taken = [item[2] for item in atts]
        attempts_content = [item[3] for item in atts]
        times_created = [item[4] for item in atts]
        
        num_counted_attempts = 0 # We will not count any attempts after a student's first correct one
        num_counted_correct_attempts = 0
        num_submitting_students = 0
        
        ex_scores = []
        correct_attempt_numbers = []
        
        for i in range(0, len(atts)):
            if not (submitters[i] in students): continue # Do not include attempts by non-students in the report
            
            is_student_first_attempt = (i == 0) or (submitters[i] != submitters[i-1])
            if is_student_first_attempt:
                stud_username = students[submitters[i]]['username']
                if not stud_username in data:
                    stud_fullname = students[submitters[i]]['name']
                    data[stud_username] = {'username': stud_username, 'name': stud_fullname, 'visits':[], 'total_score': 0, 'total_score_with_late_penalty': 0}
                
                num_submitting_students += 1
                is_completed = False
                score = 0
                score_after_late_penalty = 0
                attempt_number = 0
                completed = False
                attempt_times = []
                attempts = []
                num_incorrect_attempts = 0
                first_correct_attempt_number = 0
            
            if is_completed:
                continue # Skip all attempts after a first correct attempt has been found for the student
            
            attempt_number += 1
            attempt_times.append(times_taken[i])
            attempts.append(attempts_content[i].replace("\r", "").replace("\n", ";"))
            
            if completes[i] == 1:
                is_completed = True
                num_incorrect_attempts = attempt_number - 1
                first_correct_attempt_time_created = times_created[i]
                first_correct_attempt_number = attempt_number
                correct_attempt_numbers.append(attempt_number)
                num_counted_correct_attempts += 1
                if is_summative:
                    (score, score_after_late_penalty) = ComputeScoreSummative(first_correct_attempt_number, first_correct_attempt_time_created, resubmission_penalty, submissions_permitted, grace_deadline, partial_credit_deadline, late_penalty)
                if is_formative:
                    score = 1.0
                
            else:
                if not attempts_content[i] in incorrect_response_freqs[ex.id]:
                    incorrect_response_freqs[ex.id][attempts_content[i]] = 1
                else:
                    incorrect_response_freqs[ex.id][attempts_content[i]] += 1

            is_student_last_attempt = (i == len(atts)-1) or (submitters[i] != submitters[i+1])
            if is_completed or is_student_last_attempt:
                num_counted_attempts += attempt_number
                data[stud_username]['exercise_activity'][ex.id] = {'completed': 'y' if is_completed else 'n', 'attempts': json.dumps(attempts), 'median_attempt_time': median(attempt_times), 'first_correct_attempt_number': first_correct_attempt_number, 'score': score, 'score_after_late_penalty': score_after_late_penalty}
                ex_scores.append(score)
                ex_scores_after_late_penalty.apppend(total_score_with_late_penalty)
                data[stud_username]['total_score'] += score
                data[stud_username]['total_score_after_late_penalty'] += total_score_with_late_penalty
                
            # End of loop on exercise attempts
        
        exercise_summaries[ex.id] = {
            'exercise':ex,
            'mean_score': mean(ex_scores),
            'max_score': max(ex_scores),
            'mean_score_after_late_penalty': mean(ex_scores_after_late_penalty),
            'max_score_after_late_penalty': max(ex_scores_after_late_penalty),
            'num_attempts': num_counted_attempts,
            'num_attempting_students': num_counted_attempts/num_submitting_students,
            'num_attempts_per_student': 1.0*len(submitters)/len(unique_submitters),
            'num_correct_attempts': num_counted_correct_attempts,
            'attempt_times': attempt_times,
            'num_correct_first_attempts':correct_attempt_numbers.count(1),
            'num_correct_second_attempts':correct_attempt_numbers.count(2),
            'num_correct_third_attempts':correct_attempt_numbers.count(3),
        }
    
        # End of loop on quiz exercises
    
    return (data, exercise_summaries)

def ComputeScoreSummative(first_correct_attempt_number, first_correct_attempt_time_created, resubmission_penalty, submissions_permitted, grace_deadline, partial_credit_deadline, late_penalty):
    if (first_correct_attempt_number > submissions_permitted):
        return (0.0, 0.0)
        
    score = 1.0 - (first_correct_attempt_number - 1) * resubmission_penalty
    if score < 0:
        score = 0.0
    
    score_after_late_penalty = score
    # Apply late penalty if necessary
    if first_correct_attempt_time_created > partial_credit_deadline:
        if partial_credit_deadline: score_after_late_penalty = 0
    elif first_correct_attempt_time_created > grace_deadline:
        if grace_deadline: score_after_late_penalty = score * (1-late_penalty)
    
    return (score, score_after_late_penalty)
    
def median(l):
    if len(l) == 0: return None
    
    l = sorted(l)
    if (len(l)%2) == 0: return (l[len(l)/2] + l[(len(l)-1)/2]) / 2.0
    else:
        return l[(len(l)-1)/2]