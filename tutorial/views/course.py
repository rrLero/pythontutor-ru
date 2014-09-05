from tutorial.lessons import get_sorted_lessons
from tutorial.models import Course, Lesson, UserProfile
from tutorial.views import DEFAULT_COURSE


def course_success(request):
    # step #1. retrieve list of all lessons and number of problems in them
    # step #2. retrieve all submissions and for every pair 
    course = Course.objects.all(urlname=DEFAULT_COURSE)
    lessons = get_sorted_lessons(course)
    pass
