from json import dumps

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

from tutorial.models import Course, Lesson, Problem, Submission
from tutorial.problems import load_problem
from tutorial.tester import run_test
from tutorial.views import DEFAULT_COURSE


def tester_submit(request):
    post = request.POST

    if 'user_code' not in post or 'problem' not in post:
        return HttpResponseBadRequest()

    problem_db = Problem.objects.get(urlname=post['problem'])
    if problem_db is None:
        return HttpResponseNotFound()

    problem = load_problem(problem_db)

    result = {
        'status': 'ok',
        'tests': [],
    }

    test_id = 0
    for test_input, test_answer in zip(problem['tests'], problem['answers']):
        test_result = run_test(post['user_code'], test_input, test_answer)
        test_status = test_result.verdict_status()

        if test_status != 'ok' and result['status'] == 'ok':
            result['status'] = 'error'
            result['fail_test'] = test_id

        result['tests'].append(test_status)

        test_id += 1

    if request.user.get_profile().course and request.user.get_profile().course.get_ok_ac_policy_display() == 'use_accepted_instead_of_ok':
        if result['status'] == 'ok':
            status = 'accepted'

    submission = Submission(
        problem = problem_db,
        code = post['user_code'],
        user = request.user, 
        status = {v: k for k, v in Submission.STATUS_CHOICES}[result['status']]
    )
    submission.save()

    return HttpResponse(dumps(result), content_type='application/json')
