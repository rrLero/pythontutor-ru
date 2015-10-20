from collections import defaultdict

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.shortcuts import render

from tutorial.models import Course, Submission
from tutorial.views import need_admin


@need_admin
def success_roadmap(request, course_index):
    course = Course.objects.get(id=int(course_index))
    users = User.objects.filter(userprofile__course=course)
    users_list = list(users)
    submissions = Submission.objects.filter(user__in=users).prefetch_related('problem').order_by('time')

    data = defaultdict(lambda: defaultdict(lambda: [[] for i in range(len(users))]))
    for submission in submissions:
        lesson_name = submission.problem.lesson_set.all()[0].title
        lesson_number = submission.problem.lesson_set.all()[0].lessonincourse_set.all()[0].order
        lesson_key = '{}. {}'.format(lesson_number, lesson_name)

        problem_name = submission.problem.urlname
        problem_number = submission.problem.probleminlesson_set.all()[0].order
        problem_key = '{}. {}'.format(problem_number, problem_name)

        submission_user = submission.user
        user_order = users_list.index(submission_user)

        data[lesson_key][problem_key][user_order].append(submission)

    # Convert defaultdicts to dicts because you cannot loop through
    # defaultdicts in Django templates:
    # http://stackoverflow.com/a/12842716
    datas = [(k1, [(k2, v2) for k2, v2 in sorted(v1.items())]) for k1, v1 in sorted(data.items())]

    return render(request, 'success_roadmap.html', {'data': datas})
