from collections import defaultdict

from django.shortcuts import render

from tutorial.lessons import get_sorted_lessons
from tutorial.models import Course, Lesson, Submission, UserProfile
from tutorial.problems import get_sorted_problems
from tutorial.utils import get_submission_color, sign_by_status, color_by_status
from tutorial.views import DEFAULT_COURSE, need_admin


def standings_for_lesson(request, lesson_urlname):
    course = Course.objects.get(urlname=DEFAULT_COURSE)
    lesson = Lesson.objects.get(urlname=lesson_urlname)
    navigation = dict(course=course, lesson=lesson)
    return standings_for_lessons(request, [lesson], navigation)


def standings_for_course(request):
    course = Course.objects.get(urlname=DEFAULT_COURSE)
    lessons = get_sorted_lessons(course)
    navigation = dict(course=course)
    return standings_for_lessons(request, lessons, navigation)


def get_users_and_best_submissions_for_problems(problems_loaded):
    course = Course.objects.get(urlname=DEFAULT_COURSE)
    users = {user_profile.user for user_profile in course.userprofile_set.select_related().all()}
    submissions = {} # key: (user, problem)
    problems_db_objects = {problem['db_object'] for problem in problems_loaded}
    for submission in Submission.objects.select_related().all().order_by('time'):
        # # we assume there are only two submission statuses: 'error' and 'ok'.
        # # for every (user, problem) we find chronologically first 'ok' submit.
        # # if absent, we find chronologically last 'error' submit.
        # if submission.problem in problems_db_objects and submission.user in users:
        #     problem = submission.problem
        #     user = submission.user
        #     if (user, problem) in submissions:
        #         prev_submission = submissions[(user, problem)]
        #         if prev_submission.get_status_display() == 'error':  
        #             submissions[(user, problem)] = submission
        #     else:
        #         submissions[(user, problem)] = submission

        # we assume there are following submission statuses: 'ok', 'error', 'accepted',
        # 'coding_style_violation', 'ignored'.
        # for every (user, problem) we find chronologically first 'ok' submit.
        # if absent, we find chronologically last 'accepted' submit.
        # if absent, we find chronologically last 'error', 'coding_style_violation' 
        #                                                  or 'ignored' submit.
        if submission.problem in problems_db_objects and submission.user in users:
            problem = submission.problem
            user = submission.user
            if (user, problem) in submissions:
                prev_submission = submissions[(user, problem)]
                if (prev_submission.get_status_display() not in ['ok', 'accepted']
                        or (prev_submission.get_status_display() == 'accepted' 
                        and submission.get_status_display() in ['accepted', 'ok'])):
                    submissions[(user, problem)] = submission
            else:
                submissions[(user, problem)] = submission                
    return users, submissions


def standings_for_lessons(request, lessons, navigation):
    problems = []

    for lesson in lessons:
        problems.extend(get_sorted_problems(lesson))

    users, submissions = get_users_and_best_submissions_for_problems(problems)

    user_scores = {user: [0, 0, 0] for user in users}  # [num_solved, rating, num_attempted]

    problems_num_solved = defaultdict(int)
    for (user, problem_db_object), submission in list(submissions.items()):
        if submission.get_status_display() == 'ok':
            problems_num_solved[problem_db_object] += 1

    for (user, problem_db_object), submission in list(submissions.items()):
        if submission.get_status_display() == 'ok':
            user_scores[user][0] += 1
            user_scores[user][1] += len(users) - problems_num_solved[problem_db_object] + 1
        else:
            user_scores[user][2] += 1

    users = list(users)
    users.sort(key=lambda x: ([-y for y in user_scores[x]], x.last_name, x.first_name))
    standings = {}
    for user in users:
        standings[user] = []
        for problem in problems:
            submission = submissions.get((user, problem['db_object']), None)
            if submission:                                               
                color = color_by_status[submission.get_status_display()]
                sign = sign_by_status[submission.get_status_display()]
                standings[user].append((color, get_submission_color(color), sign, problem, submission))
            else:
                standings[user].append(('white', '#ffffff', '', problem, None))
    users = [(user, standings[user], user_scores[user][0], user_scores[user][1]) for user in users if user_scores[user][0] > 0]
    return render(request, 'standings.html', locals())


@need_admin
def submissions_for_course(request):
    course = Course.objects.get(urlname=course_urlname)
    lessons = get_sorted_lessons(course)
    return redirect(settings.SERVER_PREFIX + 'teacher_statistics/submissions/for_lessons/' 
            + ','.join(lesson.urlname for lesson in lessons))


@need_admin
def submissions_for_lessons(request, lessons_comma_separated_list):
    return render(request, 'submissions.html', locals())


@need_admin
def get_new_submissions(request):
    # AJAX request
    # method: GET
    # params: lesson_urlname, last_retrieved_submission
    get = request.GET
    if "lesson" in get and "last_retrieved_submission" in get:
        pass
    else:
        return HttpResponseBadRequest()
