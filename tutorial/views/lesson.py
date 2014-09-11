from django import template
from django.shortcuts import render

from tutorial.lessons import load_lesson
from tutorial.models import Course, Lesson, UserProfile
from tutorial.problems import get_sorted_problems
from tutorial.views import DEFAULT_COURSE, need_admin


def lesson_in_course(request, lesson_name):
    course = Course.objects.get(urlname=DEFAULT_COURSE)
    lesson = Lesson.objects.get(urlname=lesson_name)

    lessons = course.lessonincourse_set.all()

    lesson_in_course = lesson.lessonincourse_set.get(course=course)
    navigation = dict(course=course, lesson=lesson)

    problems = get_sorted_problems(lesson=lesson)

    lesson_content = load_lesson(lesson)

    return render(request, 'lesson.html', locals())


@need_admin
def init_lessons_info(request):
    # AJAX request
    # method: GET
    # params: lessons_comma_separated_list
    get = request.GET
    if "lessons_comma_separated_list" in get:
        lessons = [Lesson.objects.get(urlname=s) for s in get["lessons_comma_separated_list"].split('%2C')]
        dict_lessons = [dict(urlname=lesson.urlname, title=lesson.title) for lesson in lessons]
        output_json = json.dumps(dict_lessons)
        return HttpResponse(output_json, content_type='text/plain') 
    else:
        return HttpResponseBadRequest()
