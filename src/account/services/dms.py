import time
from account.models import Account, Dm, Message


def get_with_message(user: Account) -> list[dict]:
    '''Возвращает список переписок с последним сообщением в каждой'''
    dms = _get_dms(user)

    dms_with_msg = []
    for dm in dms:
        dm_user = _get_dm_user(user, dm)
        msg = _get_last_message(dm)
        if not msg: continue

        dms_with_msg.append({'user': {'id': dm_user.id,
                                      'username': dm_user.username,
                                      'avatar': dm_user.avatar.url},
                             'message': {'id': msg.id,
                                         'username': msg.user.username,
                                         'time': time.strftime("%H:%M", msg.timestamp.timetuple()),
                                         'content': msg.message}})
    return dms_with_msg


def _get_dms(user: Account) -> list[Dm]:
    return Dm.objects.filter(users=user)


def _get_last_message(dm: Dm) -> Message:
    try:
        return Message.objects.filter(dm=dm).order_by('-id')[0]
    except IndexError:
        return None


def _get_dm_user(user: Account, dm: Dm) -> Account:
    for u in dm.users.all():
        if u != user: return u
