from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.template import RequestContext
from c2g.models import *
from courses.common_page_data import get_common_page_data
from courses.actions import auth_view_wrapper, auth_is_course_admin_view_wrapper

@auth_view_wrapper
def view(request, course_prefix, course_suffix, assignment_id, problem_id):
   try:
      common_page_data = get_common_page_data(request, course_prefix, course_suffix)
   except:
      raise Http404
   assignment = Assignment.objects.get(pk=assignment_id)
   problem = assignment.contest.problem_set.get(pk=problem_id)
   user = request.user
   team = Team.objects.getByUser(user)
   submissions = problem.submission_set.getByTeam(team)
   return render_to_response('problems/view.html', {'common_page_data':common_page_data, 'assignment':assignment, 'problem':problem, 'team': team, 'submissions': submissions, 'request': request}, context_instance=RequestContext(request))
   
