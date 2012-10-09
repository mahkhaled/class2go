from c2g.models import *
from courses.reports.generation.C2GReportWriter import *
import math

mean = lambda k: sum(k)/len(k)

def gen_course_quizzes_report(ready_course, save_to_s3=False):
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d-%s-Course-Quizzes.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix)
    s3_filepath = "%s/%s/reports/course_quizzes/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    
    # Title
    rw.write(content = ["Course Quizzes for %s (%s %d)" % (ready_course.title, ready_course.term.title(), ready_course.year)], nl = 1)
    
    # Get a list of Quizzes (Problem sets and videos with exercises)
    quizzes = []
    problemsets = ProblemSet.objects.getByCourse(course=ready_course)
    for ps in problemsets:
        quizzes.append(ps)
        
    videos = Video.objects.getByCourse(course=ready_course)
    for vd in videos:
        quizzes.append(vd)
        
    quizzes = sorted(quizzes, key=lambda k:k.live_datetime, reverse=True)
    
    for q in quizzes:
        WriteQuizSummaryReportContent(q, rw, full=False)

    report_content = rw.writeout()
    return {'name': "%02d_%02d_%02d__%02d_%02d_%02d-%s-Quizzes.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, course_prefix+'_'+course_suffix), 'content': report_content, 'path': s3_filepath}
        
def WriteQuizSummaryReportContent(q, rw, full=False):
    assessment_type = 'formative'
    
    if isinstance(q, Video):
        type = 'Video'
    else:
        if q.assessment_type == 'assessive':
            type = 'Summative problem set'
            assessment_type = 'summative'
        elif q.assessment_type == 'survey':
            type = 'Survey'
            assessment_type = 'survey'
        else:
            type = 'Formative problem set'
    
    rw.write(["%s (%s)" % (q.title, type)])
     
    qs = GetQuizSummary(q)
    
    if len(qs['exercise_summaries']) == 0:
        rw.write(content = ["No exercises have been added yet."], indent = 1, nl = 1)
        return
    
    if assessment_type == 'summative':
        if len(qs['quiz_scores']) > 0:
            rw.write(["Mean score", mean(qs['quiz_scores']), "Max score", max(qs['quiz_scores']), "", "Mean score after late penalty", mean(qs['quiz_scores_after_late_penalty']), "Max score after late penalty", max(qs['quiz_scores_after_late_penalty'])], indent = 1, nl = 1)
        
    
    content = ["Exercise"]
    if assessment_type == 'summative': content.extend(["Mean score", "Max score"])
    content.extend(["Total attempts", "Students who have attempted", "Avg. attempts per student", "Correct attempts", "Correct 1st attempts", "Correct 2nd attempts", "Correct 3rd attempts", "Median attempt time"])
    rw.write(content, indent = 1)
    
    for e_data in e_data_list:
        content = [e_data['exercise'].get_slug()]
        if assessment_type == 'summative': content.extend([mean(e_data['scores']), max(e_data['scores'])])
        content.extend([e_data['num_attempts'], e_data['num_attempting_students'], e_data['num_attempts_per_student'], e_data['num_correct_attempts'], e_data['num_correct_first_attempts'], e_data['num_correct_second_attempts'], e_data['num_correct_third_attempts'], median(e_data['attempt_times']) if len(e_data['attempt_times']) > 0 else ""])
        rw.write(content, indent = 1)
        
    rw.write([""])

def GetQuizSummary(q):
    (student_quiz_data, exercise_summaries) = get_quiz_data(q)
    
    return {
        'exercise_summaries': exercise_summaries,
        'quiz_total_scores': [student_quiz_data[username]['total_score'] for username in student_quiz_data],
        'quiz_total_scores_after_late_penalty': [student_quiz_data[username]['total_score_after_late_penalty'] for username in student_quiz_data],
    }


def median(l):
    if len(l) == 0: return None
    
    l = sorted(l)
    if (len(l)%2) == 0: return (l[len(l)/2] + l[(len(l)-1)/2]) / 2.0
    else: return l[(len(l)-1)/2]