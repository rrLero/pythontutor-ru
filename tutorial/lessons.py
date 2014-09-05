from operator import attrgetter

from django import template
from django.conf import settings


ABSOLUTE_PATH_TO_LESSONS = settings.ABSOLUTE_PREFIX + 'lessons/'


def get_sorted_lessons(course):
    return [lic.lesson for lic in sorted(course.lessonincourse_set.all(), 
                                         key=attrgetter('order'))]


def parse_file(filename):
    raw_lesson_content = open(filename, 'r', encoding='utf-8').read()

    lesson_content = '{% load tags %}\n{% lesson %}\n' + raw_lesson_content + '{% endlesson %}'
    t = template.Template(lesson_content)

    return t.render(template.Context())

def load_lesson(lesson):
    return parse_file(ABSOLUTE_PATH_TO_LESSONS + lesson.filename)
