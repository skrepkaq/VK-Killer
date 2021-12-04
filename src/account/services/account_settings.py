from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


def change_password(request) -> tuple[PasswordChangeForm, bool]:
    '''Возвращает форму смены пароля и True если изменение успешно'''
    form = PasswordChangeForm(request.user, request.POST)
    if request.method == 'POST':
        print('post')
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return form, True
    else:
        PasswordChangeForm(request.user)
    return form, False
