from operator import attrgetter

from django.shortcuts import render

from tutorial.models import Course, UserProfile
from tutorial.views import DEFAULT_COURSE


def home(request):
    raw_courses = [Course.objects.get(urlname=DEFAULT_COURSE)]
    user_course = None
    try:
        if request.user.is_authenticated():
            user_course = request.user.get_profile().course
    except UserProfile.DoesNotExist:
        pass
    lessons = {course: [lic for lic in sorted(course.lessonincourse_set.all(), 
                        key=attrgetter('order'))]
                        for course in raw_courses}
    # lessons = {course: [lic.lesson for lic in sorted(course.lessonincourse_set.all(), 
    #                     key=attrgetter('order'))]
    #                     for course in raw_courses}                        
    courses = sorted(list(lessons.items()), key=lambda x: x[0] != user_course)
    return render(request, 'index.html', locals())
