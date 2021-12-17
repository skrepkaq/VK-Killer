from random import sample
from account.models import Friend, Account


def get(user: Account, only_accepted: bool) -> list[Account]:
    '''
    Возвращает список заявок в друзья
    Если only_accepted == True - только принятных
    '''
    users = []
    for offer in user.friend_offers.all():
        friend = _get_other_from_offer(user, offer)
        accepted = offer.users_accepted.all()
        is_accepted = len(accepted) == 2
        if is_accepted or (not only_accepted and user not in accepted):
            # заявка принята, либо не only_accepted и заявка отправлена мне, а не мною
            users.append({'user': friend,
                          'is_accepted': is_accepted})
    return users


def get_my_offers(user: Account) -> list[Account]:
    '''Возвращает список друзей и пользователей на которых подписан user'''
    return [_get_other_from_offer(user, fr) for fr in user.friends.all()]


def get_random_accepted(user: Account, k: int) -> list[Account]:
    '''Возвращает k случайных принятых заявок в друзья и общее количество друзей'''
    users = [u["user"] for u in get(user, True)]
    if len(users) < k: k = len(users)
    return sample(users, k=k), len(users)


def _get_other_from_offer(user: Account, offer: Friend) -> Account:
    '''Возвращает второго пользователя из заявки в друзья'''
    for u in offer.users.all():
        if u != user:
            return u
