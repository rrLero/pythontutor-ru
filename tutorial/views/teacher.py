from operator import attrgetter

from django.shortcuts import render

from tutorial.models import Course, UserProfile
from tutorial.views import DEFAULT_COURSE, need_admin


@need_admin
def teacher(request):
    main_course = Course.objects.get(urlname=DEFAULT_COURSE)
    lessons = [lic for lic in sorted(main_course.lessonincourse_set.all(), key=attrgetter('order'))]
    courses = Course.objects.all()
    return render(request, 'teacher.html', locals())
