from django.db.models import Count
from account.models import Account, Friend


def get_user(id: int) -> Account:
    '''Возвращает аккаунт владельца страницы если существует'''
    try:
        user = Account.objects.get(pk=id)
    except Account.DoesNotExist:
        user = None
    return user


def offer(request, profile_user: Account) -> list[Account]:
    '''Обрабатывает запрос в друзья. Возвращает список принявших заявку'''
    if not request.user.is_authenticated: return None  # если пользователь не авторизован - заявок быть не может
    offer = _get_offer(request.user, profile_user)

    if request.method == 'POST':
        if request.POST['action'] == "add_friend":
            offer = _create_or_accept_offer(offer, request.user, profile_user)
        elif request.POST['action'] == "remove_friend":
            offer = _get_offer(request.user, profile_user)
            if offer:
                if len(offer.users_accepted.all()) == 1:
                    offer.delete()
                    offer = None
                else:
                    offer.users_accepted.remove(request.user)

    if offer:
        return offer.users_accepted.all()
    else:
        return None


def _get_offer(user: Account, profile_user: Account) -> Friend:
    '''Возвращет заявку в друзья, если существует'''
    offer = Friend.objects.filter(users__in=[user, profile_user])\
                          .annotate(num_users=Count('users')).filter(num_users=2)
    if len(offer) == 0: return None

    return offer[0]


def _create_or_accept_offer(offer: Friend, user: Account, profile_user: Account) -> Friend:
    '''
    Принимает или создаёт заявку в друзья, если её нет.
    Возвращает заявку
    '''
    if not offer:
        # Создать заявку с юзерами
        offer = Friend.objects.create()
        offer.users.add(user, profile_user)

    if user not in offer.users_accepted.all():
        # Принять заявку (необходимо даже сразу после ей создания)
        offer.users_accepted.add(user)

    return offer
