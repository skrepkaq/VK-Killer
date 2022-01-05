from channels.db import database_sync_to_async
from account.models import Account, Dm, Message
from account.services import online


def get_with_message(user: Account) -> list[dict]:
    '''Возвращает список переписок с последним сообщением в каждой'''
    dms = _get_dms(user)

    dms_with_msg = []
    for dm in dms:
        dm_user = _get_dm_user(user, dm)
        msg = _get_last_message(dm)
        if not msg or not dm_user: continue

        dms_with_msg.append({'user': {'id': dm_user.id,
                                      'username': dm_user.username,
                                      'url': dm_user.url,
                                      'avatar': dm_user.avatar.url},
                             'message': {'id': msg.id,
                                         'username': msg.user.username,
                                         'time': online.convert_datetime_to_str(msg.timestamp, user.timezone),
                                         'content': msg.message,
                                         'read': msg.read}})
    return dms_with_msg


@database_sync_to_async
def is_unread_messages(user: Account) -> bool:
    '''Возвращает True если у пользователя есть непрочитанные сообщения'''
    dms = _get_dms(user)
    for dm in dms:
        last_msg = _get_last_message(dm)
        if last_msg and last_msg.user != user and not last_msg.read:
            return True
    return False


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
