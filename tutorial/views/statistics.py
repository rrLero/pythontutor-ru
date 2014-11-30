from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render

import datetime
from datetime import timedelta
from tutorial.models import Submission


def statistics(request):
    day_before = datetime.datetime.now() - timedelta(days=1)
    week_before = datetime.datetime.now() - timedelta(weeks=1)
    month_before = datetime.datetime.now() - timedelta(days=30)

    new_users_in_last_day = User.objects.filter(date_joined__gte=day_before).count()
    new_users_in_last_week = User.objects.filter(date_joined__gte=week_before).count()
    new_users_in_last_month = User.objects.filter(date_joined__gte=month_before).count()

    submissions_in_last_day = Submission.objects.filter(time__gte=day_before).count()
    submissions_in_last_week = Submission.objects.filter(time__gte=week_before).count()
    submissions_in_last_month = Submission.objects.filter(time__gte=month_before).count()

    ok_submissions_in_last_day = Submission.objects.filter(time__gte=day_before, status=1).count()
    ok_submissions_in_last_week = Submission.objects.filter(time__gte=week_before, status=1).count()
    ok_submissions_in_last_month = Submission.objects.filter(time__gte=month_before, status=1).count()

    active_users_in_last_day = (Submission.objects.filter(time__gte=day_before, status=1)
            .values('user').annotate(user_count=Count('user', distinct=True)).count())
    active_users_in_last_week = (Submission.objects.filter(time__gte=week_before, status=1)
            .values('user').annotate(user_count=Count('user', distinct=True)).count())
    active_users_in_last_month = (Submission.objects.filter(time__gte=month_before, status=1)
            .values('user').annotate(user_count=Count('user', distinct=True)).count())

    return render(request, 'statistics.html', locals())
