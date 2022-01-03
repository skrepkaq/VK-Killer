from django.db.models import Count, Q, When, Case, Value
from account.models import Friend, Account


def get(user: Account, only_accepted: bool) -> list[Account]:
    '''
    Возвращает список заявок в друзья
    Если only_accepted == True - только принятных
    '''
    offers = (
        user.friend_offers
        .alias(num_users=Count('users_accepted'))
        .annotate(is_accepted=Case(When(num_users=2, then=Value(True)), default=Value(False)))
        .filter(Q(is_accepted=True) | ~Q(users_accepted=user) & ~Q(Value(only_accepted)))
        .order_by('is_accepted')
        .reverse()
    )
    return [{'user': _get_other_from_offer(user, offer), 'is_accepted': offer.is_accepted} for offer in offers]


def get_my_offers(user: Account) -> list[Account]:
    '''Возвращает список друзей и пользователей на которых подписан user'''
    return [_get_other_from_offer(user, fr) for fr in user.friends.all()]


def get_random_accepted(user: Account, k: int) -> list[Account]:
    '''Возвращает k случайных принятых заявок в друзья и общее количество друзей'''
    users = user.friend_offers.alias(num_users=Count('users_accepted')).filter(num_users=2).order_by('?')
    num = len(users)
    return [_get_other_from_offer(user, users[i]) for i in range(k if num > k else num)], num


def _get_other_from_offer(user: Account, offer: Friend) -> Account:
    '''Возвращает второго пользователя из заявки в друзья'''
    for u in offer.users.all():
        if u != user:
            return u
