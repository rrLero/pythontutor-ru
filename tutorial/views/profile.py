from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.conf import settings

from social_login import sociallogin_callback

from tutorial.forms import UserCreationForm
from tutorial.models import Submission, UserProfile


@sociallogin_callback('register')
def register_callback(user):
    user_profile = UserProfile(user=user)
    user_profile.save()


def profile(request, username):
    user = User.objects.get(username=username)
    submissions = Submission.objects.filter(user=user)
    return render(request, 'profile.html', locals())


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username):
                error = 'Пользователь с таким логином уже существует'
                return render(request, 'register.html', locals())

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            
            user = User.objects.create_user(username, email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            user_profile = UserProfile(user=user)
            user_profile.save()

            return redirect(settings.SERVER_PREFIX + 'accounts/login/')

    form = UserCreationForm()
    return render(request, 'register.html', locals())
