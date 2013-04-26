from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import *
from courses.common_page_data import get_common_page_data
from courses.actions import auth_view_wrapper, auth_is_course_admin_view_wrapper

@auth_view_wrapper
def list(request, course_prefix, course_suffix):
   try:
      common_page_data = get_common_page_data(request, course_prefix, course_suffix)
   except:
      raise Http404
   assignments = Assignment.objects.getByCourse(common_page_data['course']).order_by('-id')
   total_full_mark = 0
   total_grade_obtained = 0
   for assignment in assignments:
      assignment.calculated_grade = assignment.grade(request.user)
      total_grade_obtained += assignment.calculated_grade
      total_full_mark += assignment.full_mark
   return render_to_response('assignments/list.html', {'common_page_data':common_page_data, 'assignments':assignments, 'total_grade_obtained':total_grade_obtained, 'total_full_mark':total_full_mark}, context_instance=RequestContext(request))
    
# def admin(request, course_prefix, course_suffix):
#     return render_to_response('assignments/admin.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'request': request}, context_instance=RequestContext(request))

@auth_view_wrapper
def view(request, course_prefix, course_suffix, assignment_id):
   try:
      common_page_data = get_common_page_data(request, course_prefix, course_suffix)
   except:
      raise Http404
   assignment = Assignment.objects.get(pk=assignment_id)
   problems = assignment.problem_set.all()

   grade = assignment.grade(request.user)
   for problem in problems:
      problem.correct_submissions = problem.submission_set.getByTeam(Team.objects.getByUser(request.user)).filter(judging__result="correct").count()
      problem.total_submissions = problem.submission_set.getByTeam(Team.objects.getByUser(request.user)).count()

   return render_to_response('assignments/view.html', {'common_page_data':common_page_data, 'assignment':assignment, 'problems':problems, 'grade': grade, 'request': request}, context_instance=RequestContext(request))
    
# def edit(request, course_prefix, course_suffix, assignment_id):
#     return render_to_response('assignments/edit.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'assignment_id':assignment_id, 'request': request}, context_instance=RequestContext(request))
    
# def grade(request, course_prefix, course_suffix, assignment_id):
#     return render_to_response('assignments/grade.html', {'course_prefix': course_prefix, 'course_suffix': course_suffix, 'assignment_id':assignment_id, 'request': request}, context_instance=RequestContext(request))
