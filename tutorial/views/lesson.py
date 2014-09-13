from django import template
from django.shortcuts import render

from tutorial.lessons import load_lesson
from tutorial.models import Course, Lesson, UserProfile
from tutorial.problems import get_sorted_problems
from tutorial.views import DEFAULT_COURSE, need_admin


def lesson_in_course(request, lesson_name):
    course = Course.objects.get(urlname=DEFAULT_COURSE)
    lesson_db = Lesson.objects.get(urlname=lesson_name)

    lessons = course.lessonincourse_set.all()
    lesson_in_course = lesson_db.lessonincourse_set.get(course=course)

    problems = get_sorted_problems(lesson=lesson_db)

    lesson = load_lesson(lesson_db)

    return render(request, 'lesson.html', locals())
