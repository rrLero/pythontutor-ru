from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin, auth
from django.contrib.auth.views import login, logout

from tutorial.views import dummy
from tutorial.views.course import course_success
from tutorial.views.home import home
from tutorial.views.lesson import lesson_in_course
from tutorial.views.problem import problem_in_lesson, send_problem_to_frontend
from tutorial.views.profile import profile, register_user
from tutorial.views.standings import (standings_for_course, standings_for_lesson,
                                      submissions_for_course, submissions_for_lessons)
from tutorial.views.tests import run_test, post_grading_result
from tutorial.views.visualizer import execute, visualizer, visualizer_for_lesson


admin.autodiscover()


urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', home, name="home"),
    
    url(r'^visualizer/for_lesson/([^/]+)/', visualizer_for_lesson, name='visualizer_for_lesson'),

    url(r'^visualizer/', visualizer, name='visualizer'),

    url(r'^execute/', execute),

    url(r'^lessons/([^/]+)/$', lesson_in_course, name="lesson_in_course"),

    url(r'^lessons/([^/]+)/problems/([^/]+)/$', problem_in_lesson, name="problem_in_lesson"),

    url(r'^lessons/([^/]+)/standings/$', standings_for_lesson),    

    url(r'^standings/$', standings_for_course),

    url(r'^load_problem/$', send_problem_to_frontend),

    url(r'^run_test/$', run_test),

    url(r'^accounts/login/$', login, {'template_name': 'login.html'}, name='login'),

    url(r'^accounts/logout/$', logout, {'next_page': settings.LOGIN_REDIRECT_URL}, name="logout"),

    url(r'^accounts/register/$', register_user, name='register'),

    url(r'^accounts/profile/$', profile, name='profile'),

    url(r'^tutorial/post_grading_result/$', post_grading_result),

    url(r'^teacher_statistics/course_success/([^/]+)/$', course_success, name='course_success'),

    url(r'^teacher_statistics/submissions/for_lessons/([^/]+)/$', submissions_for_lessons, name='submissions_for_lessons'),  

    url(r'^teacher_statistics/submissions/for_course/([^/]+)/$', submissions_for_course, name='submissions_for_course'),
    # example of use:
    # teacher_statistics/submissions/for_lessons/ifelse,for_loop/
)
