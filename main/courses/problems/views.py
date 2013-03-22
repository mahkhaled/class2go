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
   
@auth_view_wrapper
def submit(request, course_prefix, course_suffix, assignment_id, problem_id):
   try:
      common_page_data = get_common_page_data(request, course_prefix, course_suffix)
   except:
      raise Http404
   if request.method == 'POST':
      submission_file = request.FILES['submission']
      submission_code = submission_file.read()

      assignment = Assignment.objects.get(pk=assignment_id)
      problem = assignment.contest.problem_set.get(pk=problem_id)
      user = request.user
      team = Team.objects.getByUser(user)
      submissions = problem.submission_set.getByTeam(team)

      langid = submission_file.name.split('.')[1]
      
      submission = Submission(problem=problem, contest=assignment.contest, team=team[0], langid=langid)
      submission.save()
      submission_file = SubmissionFile(submission=submission, source_code=submission_code, file_name=submission_file, rank=0)
      submission_file.save()


   return render_to_response('problems/view.html', {'common_page_data':common_page_data, 'assignment':assignment, 'problem':problem, 'team': team, 'submissions': submissions, 'request': request}, context_instance=RequestContext(request))

@auth_view_wrapper
def submission_run(request, course_prefix, course_suffix, assignment_id, problem_id, submission_id):
   try:
      common_page_data = get_common_page_data(request, course_prefix, course_suffix)
   except:
      raise Http404

   assignment = Assignment.objects.get(pk=assignment_id)
   problem = assignment.contest.problem_set.get(pk=problem_id)
   user = request.user
   team = Team.objects.getByUser(user)
   submissions = problem.submission_set.getByTeam(team)
   print submission_id
   submission = submissions.get(pk=submission_id)

   response = HttpResponse(content_type='text')
   response['Content-Disposition'] = 'attachment; filename="run.txt"'

   response.write(submission.judging.judgingrun.output_run)
   return response

@auth_view_wrapper
def submission_diff(request, course_prefix, course_suffix, assignment_id, problem_id, submission_id):
   try:
      common_page_data = get_common_page_data(request, course_prefix, course_suffix)
   except:
      raise Http404
   assignment = Assignment.objects.get(pk=assignment_id)
   problem = assignment.contest.problem_set.get(pk=problem_id)
   user = request.user
   team = Team.objects.getByUser(user)
   submissions = problem.submission_set.getByTeam(team)
   print submission_id
   submission = submissions.get(pk=submission_id)

   response = HttpResponse(content_type='text')
   response['Content-Disposition'] = 'attachment; filename="diff.txt"'

   response.write(submission.judging.judgingrun.output_diff)
   return response