import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from tutorial.models import Course, Lesson, Problem, Submission
from tutorial.lessons import get_sorted_lessons
from tutorial.problems import load_problem
from tutorial.views import DEFAULT_COURSE, need_login


def get_best_saved_code(user, problem_urlname):
    problem = Problem.objects.get(urlname=problem_urlname)

    submissions = Submission.objects.filter(user=user, problem=problem).order_by('-time')
    submission = None
    for s in submissions:
        if s.get_status_display() == 'ok':
            submission = s
            break

    if not submission and len(submissions) > 0:
        submission = submissions[0]

    return submission.code if submission else ''


@need_login
def problem_in_lesson(request, lesson_name, problem_name):
    course = Course.objects.get(urlname=DEFAULT_COURSE)
    lessons = course.lessonincourse_set.all()

    lesson = Lesson.objects.get(urlname=lesson_name)
    lesson_in_course = lesson.lessonincourse_set.get(course=course)

    problem_db = Problem.objects.get(urlname=problem_name)
    problem = load_problem(problem_db)

    saved_code = get_best_saved_code(request.user, problem_name)

    tests_examples = []
    for test_input, test_output in zip(problem['tests'], problem['answers']):
        tests_examples.append({'input': test_input, 'output': test_output})

    return render(request, 'problem.html', locals())
