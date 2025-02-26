import re
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from account.models import Account


def change_password(request) -> tuple[PasswordChangeForm, bool]:
    '''Возвращает форму смены пароля и True если изменение успешно'''
    form = PasswordChangeForm(request.user, request.POST)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return form, True
    else:
        PasswordChangeForm(request.user)
    return form, False


def change_url(request) -> bool:
    '''Изменяет url пользователя, при попытке возвращает True'''
    if request.method == 'POST':
        if request.POST["action"] == 'change_url':
            url = request.POST["url"]
            if request.user.url == url:
                raise ValueError('URL совпадает с вашим текущим')
            if Account.objects.filter(Q(username=url) & ~Q(pk=request.user.id)):
                raise ValueError('URL совпадает и username\'ом существующего пользователя')
            if Account.objects.filter(url=url):
                raise ValueError('URL уже занят')
            if not re.fullmatch(r'[a-zA-Z]\w{3,19}', url):
                raise ValueError('URL должен начинаться с буквы и должен состоять\
                        из латинских буков, цифр и подчеркиваний (4-20) символов')
            request.user.url = url
            request.user.save()
            return True

def change_feed_position(request) -> bool:
    '''Изменяет позицию ленты пользователя, при попытке возвращает True'''
    if request.method == 'POST':
        if request.POST["action"] == 'change_feed_position':
            feed_position = request.POST["feed_position"]
            if feed_position not in ['w', 'l', 'c', 'r']:
                raise ValueError('Такая позиция ленты невозможна')
            request.user.feed_position = feed_position
            request.user.save()
            return True
