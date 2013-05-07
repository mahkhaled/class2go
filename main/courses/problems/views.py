from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template import Context, loader
from django.template import RequestContext
from django.contrib import messages
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
   problem = assignment.problem_set.get(pk=problem_id)
   user = request.user
   team = Team.objects.getByUser(user)
   submissions = problem.submission_set.getByTeam(team)
   for submission in submissions:
      submission.judigng_to_show = submission.last_judging()
      submission.run_to_show = submission.last_judging().first_error_run()
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
      problem = assignment.problem_set.get(pk=problem_id)
      user = request.user
      team = Team.objects.getByUser(user)
      submissions = problem.submission_set.getByTeam(team)

      langid = submission_file.name.split('.')[1]

      try:
         Language.objects.get(langid=langid)
         submission = Submission(problem=problem, contest=assignment.contest, team=team[0], langid=langid)
         submission.save()
         submission_file = SubmissionFile(submission=submission, source_code=submission_code, file_name=submission_file, rank=0)
         submission_file.save()
         messages.add_message(request,messages.SUCCESS, 'Your submission was saved and will be graded shortly.')
      except Language.DoesNotExist:
         messages.add_message(request,messages.ERROR, 'You submitted a file with invalid extension.')
         return redirect(reverse('courses.assignments.views.view', args=[course_prefix, course_suffix, assignment.id]))

   return redirect(reverse('courses.problems.views.view', args=[course_prefix, course_suffix, assignment_id, problem_id]))

@auth_view_wrapper
def submission_run(request, course_prefix, course_suffix, assignment_id, problem_id, submission_id):
   try:
      common_page_data = get_common_page_data(request, course_prefix, course_suffix)
   except:
      raise Http404

   assignment = Assignment.objects.get(pk=assignment_id)
   problem = assignment.problem_set.get(pk=problem_id)
   user = request.user
   team = Team.objects.getByUser(user)
   submissions = problem.submission_set.getByTeam(team)
   submission = submissions.get(pk=submission_id)

   
   try:
      response = HttpResponse(content_type='text')
      response.write(submission.last_judging().first_wrong_run().output_run)
      response['Content-Disposition'] = 'attachment; filename="run.txt"'
      return response

   except Judging.DoesNotExist:
      messages.add_message(request,messages.WARNING, 'The run output that you asked for is not available yet, try again shortly.')
      return render_to_response('problems/view.html', {'common_page_data':common_page_data, 'assignment':assignment, 'problem':problem, 'team': team, 'submissions': submissions, 'request': request}, context_instance=RequestContext(request))

@auth_view_wrapper
def submission_diff(request, course_prefix, course_suffix, assignment_id, problem_id, submission_id):
   try:
      common_page_data = get_common_page_data(request, course_prefix, course_suffix)
   except:
      raise Http404
   assignment = Assignment.objects.get(pk=assignment_id)
   problem = assignment.problem_set.get(pk=problem_id)
   user = request.user
   team = Team.objects.getByUser(user)
   submissions = problem.submission_set.getByTeam(team)
   submission = submissions.get(pk=submission_id)

   response = HttpResponse(content_type='text')
   response['Content-Disposition'] = 'attachment; filename="diff.txt"'

   try:
      response = HttpResponse(content_type='text')
      response.write(submission.last_judging().first_wrong_run().output_diff)
      response['Content-Disposition'] = 'attachment; filename="diff.txt"'
      return response

   except Judging.DoesNotExist:
      messages.add_message(request,messages.WARNING, 'The diff output that you asked for is not available yet, try again shortly.')
      return render_to_response('problems/view.html', {'common_page_data':common_page_data, 'assignment':assignment, 'problem':problem, 'team': team, 'submissions': submissions, 'request': request}, context_instance=RequestContext(request))

@auth_view_wrapper
def submission_input(request, course_prefix, course_suffix, assignment_id, problem_id, submission_id):
   try:
      common_page_data = get_common_page_data(request, course_prefix, course_suffix)
   except:
      raise Http404
   assignment = Assignment.objects.get(pk=assignment_id)
   problem = assignment.problem_set.get(pk=problem_id)
   user = request.user
   team = Team.objects.getByUser(user)
   submissions = problem.submission_set.getByTeam(team)
   submission = submissions.get(pk=submission_id)

   response = HttpResponse(content_type='text')
   response['Content-Disposition'] = 'attachment; filename="diff.txt"'

   try:
      response = HttpResponse(content_type='text')
      response.write(submission.last_judging().first_wrong_run().testcase.input_result)
      response['Content-Disposition'] = 'attachment; filename="input.txt"'
      return response

   except Judging.DoesNotExist:
      messages.add_message(request,messages.WARNING, 'The diff output that you asked for is not available yet, try again shortly.')
      return render_to_response('problems/view.html', {'common_page_data':common_page_data, 'assignment':assignment, 'problem':problem, 'team': team, 'submissions': submissions, 'request': request}, context_instance=RequestContext(request))

