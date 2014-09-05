from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest

from tutorial.models import Course, Lesson
from tutorial.views import DEFAULT_COURSE

from evaldontevil import execute_python


def visualizer(request):
    return render(request, 'visualizer.html', locals())


def visualizer_for_lesson(request, lesson_name):
    course = Course.objects.get(urlname=DEFAULT_COURSE)
    lesson = Lesson.objects.get(urlname=lesson_name)
    navigation = dict(course=course, lesson=lesson)
    return render(request, 'visualizer.html', locals())


def execute(request):
    # AJAX request
    # method: POST
    # params: user_script, input_data
    post = request.POST
    if 'user_script' in post and 'input_data' in post:
        user_script = post['user_script']
        input_data = post['input_data']

        res = execute_python(user_script, stdin=input_data)
        json_data = res.stdout
        print(res.stderr)

        return HttpResponse(json_data, content_type='text/plain')

    else:
        return HttpResponseBadRequest()
