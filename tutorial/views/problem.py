import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from tutorial.models import Course, Lesson, Problem, Submission
from tutorial.problems import load_raw_problem
from tutorial.views import DEFAULT_COURSE, need_login


def get_best_saved_code(user, problem_urlname):
    problem = Problem.objects.get(urlname=problem_urlname)
    submissions = Submission.objects.filter(user=user, problem=problem).order_by("-time")
    submission = None
    for s in submissions:
        if s.get_status_display() == 'ok':
            submission = s
            break
    if not submission and len(submissions) > 0:
        submission = submissions[0]
    if submission:
        return submission.code
    else:
        return ""


@need_login
def problem_in_lesson(request, lesson_name, problem_name):
    course = Course.objects.get(urlname=DEFAULT_COURSE)
    lesson = Lesson.objects.get(urlname=lesson_name)
    navigation = dict(course=course, lesson=lesson)
    
    # actually it's unused so far as problem loads dynamically by AJAX
    # problem = load_problem(Problem.objects.get(urlname=problem_name))

    return render(request, 'problem.html', locals())
    

def send_problem_to_frontend(request):
    # AJAX request
    # method: GET            
    # params: problem_urlname
    get = request.GET
    if 'problem_urlname' in get:
        problem_urlname = get['problem_urlname']

        problem = load_raw_problem(Problem.objects.get(urlname=problem_urlname))

        # we should fill this field by last submit, if any
        problem['savedCode'] = get_best_saved_code(request.user, problem['urlname'])

        output_json = json.dumps(problem)
        
        return HttpResponse(output_json, content_type='text/plain')                
    else:
        return HttpResponseBadRequest()
