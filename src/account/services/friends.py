from random import sample
from account.models import Friend, Account


def get(user: Account, only_accepted: bool) -> list[Account]:
    '''
    Возвращает список заявок в друзья
    Если only_accepted == True - только принятных
    '''
    users = []
    for fr in Friend.objects.filter(users=user):
        for usr in fr.users_accepted.all():
            if usr != user and len(fr.users_accepted.all()) > (1 if only_accepted else 0):
                users.append({'user': usr,
                              'is_accepted': len(fr.users_accepted.all())-1})
    return users


def get_random_accepted(user: Account, k: int) -> list[Account]:
    '''Возвращает k случайных принятых заявок в друзья и общее количество друзей'''
    users = [u["user"] for u in get(user, True)]
    if len(users) < k: k = len(users)
    return sample(users, k=k), len(users)
