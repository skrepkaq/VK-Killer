from django.db.models import Count, Q, When, Case, Value
from account.models import Account


def get(user: Account, only_accepted: bool) -> list[dict]:
    '''
    Возвращает список заявок в друзья
    Если only_accepted == True - только принятных
    '''
    offers_query = (
        user.friend_offers
        .alias(num_users=Count('users_accepted'))
        .annotate(is_accepted=Case(When(num_users=2, then=Value(True)), default=Value(False)))
        .filter(Q(is_accepted=True) | ~Q(users_accepted=user) & ~Q(Value(only_accepted)))
        .order_by('is_accepted')
        .reverse()
    )

    offers = []
    for offer in offers_query.prefetch_related('users'):
        for u in offer.users.all():
            if u != user:
                offers.append({'user': u, 'is_accepted': offer.is_accepted})
                break

    return offers


def get_my_offers(user: Account) -> list[Account]:
    '''Возвращает список друзей и пользователей на которых подписан user'''
    friends = []
    for friend in user.friends.all().prefetch_related('users'):
        for u in friend.users.all():
            if u != user:
                friends.append(u)
                break

    return friends


def get_random_accepted(user: Account, k: int) -> list[Account]:
    '''Возвращает k случайных принятых заявок в друзья и общее количество друзей'''
    users = user.friend_offers.alias(num_users=Count('users_accepted')).filter(num_users=2).order_by('?')
    num = len(users)

    other_users = []
    for offer in users.prefetch_related('users')[:k if num > k else num]:
        for u in offer.users.all():
            if u != user:
                other_users.append(u)
                break

    return other_users, num
