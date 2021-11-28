from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import AccountCreateForm, AccountLoginForm
from .services import account, profile, dms, friends, search
from .decorators import unauth_user


@unauth_user
def register_view(request):
    form = AccountCreateForm()
    if request.method == 'POST':
        form, is_created = account.create(request)
        if is_created:
            return redirect('home')

    context = {'form': form}
    return render(request, 'register.html', context)


@unauth_user
def login_view(request):
    form = AccountLoginForm()
    if request.method == 'POST' and account.login(request):
        return redirect('home')
    context = {'form': form}
    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home_view(request):
    return render(request, "home.html")


def profile_view(request, id):
    profile_user = profile.get_user(id)
    if not profile_user:
        return HttpResponse('<h3>404</h3>')

    accepted = profile.offer(request, profile_user)
    fr, k = friends.get_random_accepted(profile_user, k=3)

    context = {'profile_user': profile_user,
               'offer_accepted_users': accepted,
               'friends': fr,
               'friends_count': k}
    return render(request, 'profile.html', context)


@login_required(login_url='login')
def myprofile_view(request):
    return profile_view(request, request.user.id)


@login_required(login_url='login')
def myfriends_view(request):
    return friends_view(request, request.user.id)


def search_view(request):
    users = search.find_all(request)

    context = {'users': users}
    return render(request, 'search.html', context)


@login_required(login_url='login')
def message_view(request, id):
    profile_user = profile.get_user(id)
    if not profile_user:
        return HttpResponse('<h3>404</h3>')

    if request.user == profile_user:  # написать самому себе нельзя
        return redirect('dms')

    context = {
        'messages': None,
        'dm_user': profile_user
    }
    return render(request, 'dm.html', context)


def friends_view(request, id):
    profile_user = profile.get_user(id)
    if not profile_user:
        return HttpResponse('<h3>404</h3>')

    is_my_friends = request.user == profile_user
    users = friends.get(profile_user, not is_my_friends)  # Если профиль мой - кроме друзей показать заявки в друзья
    context = {'users': users, 'my': is_my_friends, 'profile_user': profile_user}
    return render(request, 'friends.html', context)


@login_required(login_url='login')
def dms_view(request):
    dm = dms.get_with_message(request.user)

    return render(request, 'dms.html', {'dms': dm})
