from django.contrib.auth.models import User
from django.shortcuts import render

import datetime
from datetime import timedelta
from tutorial.models import Submission


def statistics(request):
    week_before = datetime.datetime.now() - timedelta(weeks=1)
    month_before = datetime.datetime.now() - timedelta(days=30)
    new_users_in_last_week = User.objects.filter(date_joined__gte=week_before).count()
    new_users_in_last_month = User.objects.filter(date_joined__gte=month_before).count()
    submissions_in_last_week = Submission.objects.filter(time__gte=week_before).count()
    submissions_in_last_month = Submission.objects.filter(time__gte=month_before).count()
    return render(request, 'statistics.html', locals())
