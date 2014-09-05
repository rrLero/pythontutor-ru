from django.http import HttpResponse, HttpResponseBadRequest

from tutorial.models import Course, Lesson, Problem, Submission
from tutorial.views import DEFAULT_COURSE

from visualizer.web_run_test import run_script_on_test_input


def run_test(request):
    # AJAX request
    # method: POST
    # params: user_script, test_input, test_answer
    post = request.POST
    if ('user_script' in post 
            and 'test_input' in post 
            and 'test_answer' in post):
        user_script = post['user_script']
        test_input = post['test_input']
        test_answer = post['test_answer']

        json = run_script_on_test_input(user_script, test_input, test_answer)

        return HttpResponse(json, content_type='text/plain')
    else:
        return HttpResponseBadRequest()

def post_grading_result(request):
    # AJAX request
    # method: POST
    # params: problem, code, result
    post = request.POST
    if ('problem' in post and 'code' in post and 'result' in post
            and request.user.is_authenticated()):
        problem_urlname = post['problem']
        problem = Problem.objects.get(urlname=problem_urlname)
        code = post['code']
        status = post['result']
        user = request.user

    if user.get_profile().course and user.get_profile().course.get_ok_ac_policy_display() == 'use_accepted_instead_of_ok':
        if status == 'ok':
            status = 'accepted'

        submission = Submission(problem=problem, code=code, user=user, 
                                status={v: k for k, v in Submission.STATUS_CHOICES}[status])

        submission.save()

        return HttpResponse(json, content_type='text/plain')                
    else:
        return HttpResponseBadRequest()
