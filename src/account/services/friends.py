from random import sample
from account.models import Friend, Account


def get(user: Account, only_accepted: bool, my_offers=False) -> list[Account]:
    '''
    Возвращает список заявок в друзья
    Если only_accepted == True - только принятных
    Если my_offers - только мои или принятые заявки
    '''
    users = []
    for offer in user.friend_offers.all():
        friend = _get_other_from_offer(user, offer)
        users_accepted = offer.users_accepted.all()
        is_accepted = len(users_accepted) - 1
        is_my_offer = user in users_accepted
        if (((not only_accepted and not is_my_offer) or is_accepted) and not my_offers) or (my_offers and is_my_offer):
            # ну, крч это условие определяет нужная ли эта заявка, не пытайтесь в нём разобраться
            users.append({'user': friend,
                          'is_accepted': is_accepted})
    return users


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
