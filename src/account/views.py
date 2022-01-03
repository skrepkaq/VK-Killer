from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import AccountCreateForm, AccountLoginForm
from .services import account, profile, dms, friends, search, posts, account_settings, avatar, online
from .decorators import unauth_user
from .captcha import FormWithCaptcha


@unauth_user
def register_view(request):
    form = AccountCreateForm()
    if request.method == 'POST':
        form, is_created = account.create(request)
        if is_created:
            return redirect('home')

    context = {'form': form, 'captcha': FormWithCaptcha}
    return render(request, 'register.html', context)


@unauth_user
def login_view(request):
    form = AccountLoginForm()
    if request.method == 'POST' and account.login(request):
        return redirect('home')
    context = {'form': form, 'captcha': FormWithCaptcha}
    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home_view(request):
    return feed_view(request)


def profile_view(request, slug):
    profile_user = profile.get_user(slug)
    if not profile_user:
        return HttpResponse('<h3>404</h3>')

    is_post_created = posts.create(request)

    if is_post_created:
        # если добавлен пост - перезагрузит страницу что бы сбросить post запрос
        return HttpResponseRedirect(f'/profile/{slug}')

    accepted = profile.offer(request, profile_user)
    fr, k = friends.get_random_accepted(profile_user, k=3)
    last_seen = online.get_last_seen_info(request.user, profile_user)

    context = {'profile_user': profile_user,
               'offer_accepted_users': accepted,
               'friends': fr,
               'friends_count': k,
               'last_seen': last_seen,
               'posts_info': {'id': profile_user.id, 'type': 'profile'}}
    return render(request, 'profile.html', context)


@login_required(login_url='login')
def myprofile_view(request):
    return profile_view(request, str(request.user.id))


@login_required(login_url='login')
def myfriends_view(request):
    return friends_view(request, str(request.user.id))


def search_view(request):
    users = search.find_all(request)

    context = {'users': users}
    return render(request, 'search.html', context)


@login_required(login_url='login')
def message_view(request, slug):
    profile_user = profile.get_user(slug)
    if not profile_user:
        return HttpResponse('<h3>404</h3>')

    if request.user == profile_user:  # написать самому себе нельзя
        return redirect('dms')

    context = {
        'messages': None,
        'dm_user': profile_user
    }
    return render(request, 'dm.html', context)


def friends_view(request, slug):
    profile_user = profile.get_user(slug)
    if not profile_user:
        return HttpResponse('<h3>404</h3>')

    is_my_friends = request.user == profile_user
    users = friends.get(profile_user, not is_my_friends)  # Если профиль мой - кроме друзей показать заявки в друзья
    users.sort(key=lambda x: x["is_accepted"], reverse=True)  # Заявки в друзья выше - друзья ниже
    context = {'users': users, 'my': is_my_friends, 'profile_user': profile_user}
    return render(request, 'friends.html', context)


@login_required(login_url='login')
def dms_view(request):
    dm = dms.get_with_message(request.user)
    dm.sort(key=lambda x: x["message"]["id"], reverse=True)  # сортировать переписки по последнему сообщению

    return render(request, 'dms.html', {'dms': dm})


@login_required(login_url='login')
def settings_view(request):
    password_form, is_password_changed = account_settings.change_password(request)
    is_avatar_updated = avatar.update(request)

    url_change_error = None
    try:
        is_url_changed = account_settings.change_url(request)
    except ValueError as e:
        is_url_changed = False
        url_change_error = e

    if is_password_changed or is_avatar_updated or is_url_changed:
        return redirect('settings')

    context = {'password_form': password_form if request.method == 'POST'
               and request.POST["action"] == 'change_password' else None,
               'url_change_error': url_change_error}
    return render(request, 'settings.html', context)


def post_view(request, id):
    is_comment_send = posts.send_comment(request, id)

    if is_comment_send:
        # если отправлен комментарий - перезагрузит страницу что бы сбросить post запрос
        return HttpResponseRedirect(f'/post/{id}')
    context = {'posts_info': {'id': id, 'type': 'post'}}
    return render(request, 'post.html', context)


@login_required(login_url='login')
def feed_view(request):
    context = {'posts_info': {'id': request.user.id, 'type': 'feed', 'mode': 0}}
    return render(request, 'feed.html', context)
