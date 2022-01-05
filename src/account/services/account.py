from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib import messages
from account.forms import AccountCreateForm
from django.db.models import Q
from account.models import Account
from account.captcha import validate_captcha


def create(request) -> tuple[AccountCreateForm, bool]:
    '''
    Если данные подходящие создаёт аккаут
    Возвращает форму и True если аккаунт создан успешно
    '''
    form = AccountCreateForm(request.POST)

    is_created = False
    if not validate_captcha(request):
        messages.error(request, "Пройдите капчу")
        return form, is_created

    if form.is_valid():
        if Account.objects.filter(
            Q(username__iexact=request.POST['username'])
            | Q(email__iexact=request.POST['email'])
        ):
            messages.error(request, "Аккаунт с таким ником или почтой уже существует")
            print('nope')
        else:
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            auth_login(request, user)
            is_created = True
    return form, is_created


def login(request) -> bool:
    '''Если есть аккаут с такими данными, логин и True'''
    if not validate_captcha(request):
        messages.error(request, "Пройдите капчу")
        return

    email = request.POST['username']
    raw_password = request.POST['password']
    user = authenticate(email=email, password=raw_password)
    if user is not None:
        auth_login(request, user)
        return True
    else:
        messages.error(request, "Неправильный логин или пароль")
