from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.conf import settings

from tutorial.forms import UserCreationForm, UserProfileForm
from tutorial.models import UserProfile
from tutorial.views import need_login


@need_login
def profile(request):
    errors = []
    messages = []
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data['new_password']:
                if data['new_password'] != data['new_password_repeated']:
                    errors.append('Новый пароль повторен неправильно')
                else:
                    request.user.set_password(data['new_password'])
                    messages.append('Пароль успешно изменен')
            if data['first_name'] and data['last_name']:
                request.user.first_name = data['first_name']
                request.user.last_name = data['last_name']
            else:
                errors.append('Имя и фамилия не могут быть пустыми')
            request.user.save()
    else:
        form = UserProfileForm(dict(first_name=request.user.first_name, last_name=request.user.last_name))
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
                return direct_to_template(request, 'register.html', locals())

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
