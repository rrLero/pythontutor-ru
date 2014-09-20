from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin, auth
from django.contrib.auth.views import login, logout

from tutorial.views import dummy
from tutorial.views.course import course_success
from tutorial.views.home import home
from tutorial.views.lesson import lesson_in_course
from tutorial.views.problem import problem_in_lesson
from tutorial.views.profile import profile, register_user
from tutorial.views.statistics import statistics
from tutorial.views.tester import tester_submit
from tutorial.views.visualizer import execute, visualizer


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', home, name="home"),

    url(r'^visualizer/execute/', execute, name='visualizer_execute'),

    url(r'^visualizer/', visualizer, name='visualizer'),

    url(r'^lessons/([^/]+)/$', lesson_in_course, name="lesson_in_course"),

    url(r'^lessons/([^/]+)/problems/([^/]+)/$', problem_in_lesson, name="problem_in_lesson"),

    url(r'^tester/submit/$', tester_submit, name='tester_submit'),

    url(r'^accounts/login/$', login, {'template_name': 'login.html'}, name='login'),

    url(r'^accounts/logout/$', logout, {'next_page': settings.LOGIN_REDIRECT_URL}, name="logout"),

    url(r'^accounts/register/$', register_user, name='register'),

    url(r'^accounts/profile/$', profile, name='profile'),

    url(r'^teacher_statistics/course_success/([^/]+)/$', course_success, name='course_success'),

    url(r'^statistics/$', statistics, name='statistics'),
)
