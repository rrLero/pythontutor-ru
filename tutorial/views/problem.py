import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from tutorial.models import Course, Lesson, Problem, Submission
from tutorial.lessons import get_sorted_lessons, load_lesson
from tutorial.problems import get_sorted_problems, load_problem
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
    lesson_db = Lesson.objects.get(urlname=lesson_name)

    lessons = course.lessonincourse_set.all()
    lesson = load_lesson(lesson_db)
    lesson_in_course = lesson_db.lessonincourse_set.get(course=course)

    problems = get_sorted_problems(lesson=lesson_db)
    for problem in problems:
        if request.user.is_authenticated():
            statuses = [submission.get_status_display() for submission 
                    in Submission.objects.filter(user=request.user, problem=problem['db_object'])]
        else:
            statuses = []

        if 'ok' in statuses:
            problem['status'] = 'solved'
        elif 'accepted' in statuses:
            problem['status'] = 'accepted'
        elif 'error' in statuses:
            problem['status'] = 'unsolved'
        else:
            problem['status'] = ''

    problem_db = Problem.objects.get(urlname=problem_name)
    problem = load_problem(problem_db)

    saved_code = get_best_saved_code(request.user, problem_name)

    tests_examples = []
    for test_input, test_output in zip(problem['tests'], problem['answers']):
        tests_examples.append({'input': test_input, 'output': test_output})

    return render(request, 'problem.html', locals())
