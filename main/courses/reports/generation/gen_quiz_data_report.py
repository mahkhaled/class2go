from c2g.models import *
import json
from courses.reports.generation.C2GReportWriter import *
from courses.reports.generation.get_quiz_data import *

def gen_quiz_data_report(ready_course, ready_quiz, save_to_s3=False):
    dt = datetime.now()
    course_prefix = ready_course.handle.split('--')[0]
    course_suffix = ready_course.handle.split('--')[1]
    is_video = isinstance(ready_quiz, Video)
    is_summative = (not is_video) and (ready_quiz.assessment_type == 'assessive')
    
    report_name = "%02d_%02d_%02d__%02d_%02d_%02d-%s.csv" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, ready_quiz.slug)
    if is_video:
        s3_filepath = "%s/%s/reports/videos/%s" % (course_prefix, course_suffix, report_name)
    else:
        s3_filepath = "%s/%s/reports/problemsets/%s" % (course_prefix, course_suffix, report_name)
    
    rw = C2GReportWriter(save_to_s3, s3_filepath)
    rw.write(["Activity for %s \"%s\" in %s (%s %d)" % ('Video' if is_video else 'Problem Set', ready_quiz.title, ready_course.title, ready_course.term.title(), ready_course.year)], nl = 1) 

    data = get_quiz_data(ready_quiz)
    
    # Sort students by username
    sorted_usernames = sorted(data.keys())
    
    # If not activity, do not type anything unneeded.
    if len(sorted_usernames) == 0:
        rw.write(content=["No activity yet for this %s" % ('video' if is_video else 'problem set')], indent=1)
        report_content = rw.writeout()
        return {'name': report_name, 'path': s3_filepath, 'content': report_content}
        
    header1 = ["", ""]
    header2 = ["", ""]
    
    if is_video:
        header1.extend(["", "", "Num video visits", "Visits date/times"])
        header2.extend(["", "", "", ""])
        
    for rln in rlns:
        header1.extend(["", "", rln.exercise.get_slug(), "", "", ""])
        header2.extend(["", "", "Completed", "Attempts", "Median attempt time", "Score"])
        if is_summative:
            header1.append("")
            header2.append("Score after Late Penalty")
        
    header1.extend(["", "Total score / %d"  % len(rlns)])
    if is_summative: header1.append("Total score after late penalty")
    
    rw.write(header1)
    rw.write(header2)
    
    for u in sorted_usernames:
        r = data[u]
        stud_score = 0
        stud_score_after_late_penalty = 0
        
        content = [u, r['name']]
        if is_video:
            visit_dt_string = ""
            for vvi in range(len(data[u]['visits'])):
                if vvi > 0: visit_dt_string += ', '
                visit_dt_string += data[u]['visits'][vvi]
                
            content.extend(["", "", len(data[u]['visits']), visit_dt_string])
        
        for ex_id in ex_ids:
            if ex_id in r: ex_res = r[ex_id]
            else: ex_res = {'completed': '', 'attempts': '', 'median_attempt_time': '', 'score': '', 'score_after_late_penalty': ''}
            
            content.extend(["", "", ex_res['completed'], ex_res['attempts'], ex_res['median_attempt_time'], ex_res['score']])
            if is_summative: content.append(ex_res['score_after_late_penalty'])
            
            stud_score += (ex_res['score'] if isinstance(ex_res['score'], float) else 0)
            if is_summative: stud_score_after_late_penalty += (ex_res['score_after_late_penalty'] if isinstance(ex_res['score_after_late_penalty'], float) else 0)

        content.extend(["", stud_score])
        if is_summative: content.append(stud_score_after_late_penalty)
            
        rw.write(content)
        
    report_content = rw.writeout()
    return {'name': report_name, 'content': report_content, 'path': s3_filepath}
    