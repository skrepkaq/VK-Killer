from django.db.models import Count
from account.models import Friend, Account


def get(user: Account, only_accepted: bool) -> list[Account]:
    '''
    Возвращает список заявок в друзья
    Если only_accepted == True - только принятных
    '''
    users = []
    for offer in user.friend_offers.all():
        is_accepted = offer.users_accepted.count() == 2
        if not is_accepted and only_accepted: continue
        friend = _get_other_from_offer(user, offer)
        if is_accepted or (user not in offer.users_accepted.all()):
            # заявка принята, либо заявка отправлена мне, а не мною
            users.append({'user': friend,
                          'is_accepted': is_accepted})
    return users


def get_my_offers(user: Account) -> list[Account]:
    '''Возвращает список друзей и пользователей на которых подписан user'''
    return [_get_other_from_offer(user, fr) for fr in user.friends.all()]


def get_random_accepted(user: Account, k: int) -> list[Account]:
    '''Возвращает k случайных принятых заявок в друзья и общее количество друзей'''
    users = user.friend_offers.annotate(num_users=Count('users_accepted')).filter(num_users=2).order_by('?')
    num = len(users)
    return [_get_other_from_offer(user, users[i]) for i in range(k if num > k else num)], num


def _get_other_from_offer(user: Account, offer: Friend) -> Account:
    '''Возвращает второго пользователя из заявки в друзья'''
    for u in offer.users.all():
        if u != user:
            return u
