from django.db.models import Count
from django.db.models import Q
from channels.db import database_sync_to_async
from account.models import Dm, Message, Account


@database_sync_to_async
def get_user(id: int) -> Account:
    '''Возвращает владельца страницы если существует'''
    try:
        user = Account.objects.get(pk=id)
    except Account.DoesNotExist:
        user = None
    return user


@database_sync_to_async
def get_or_create_dm(user: Account, profile_user: Account) -> Dm:
    '''Возвращает переписку, если её нет, создаёт'''
    dm = Dm.objects.filter(users__in=[user, profile_user])\
                   .annotate(num_users=Count('users')).filter(num_users=2)

    if len(dm) == 0:
        dm = Dm.objects.create()
        dm.users.add(user, profile_user)
    else:
        dm = dm[0]
    return dm


@database_sync_to_async
def get_messages(user: Account, dm: Dm, last_msg_id: int) -> list[Message]:
    '''
    Возвращает список сообщений в переписке.
    Если last_msg_id == -1, последних 30, иначе - сообщений с id меньше чем last_msg_id
    (подгрузка более старых сообщений)
    '''
    num = 20  # Количество сообщений загружаемых за раз
    msgs = Message.objects.filter(dm=dm).order_by('-id')
    msgs.filter(Q(read=False) & ~Q(user=user)).update(read=True)
    # если переписка открыта - отметить все сообщения как прочитанные

    if last_msg_id > 0:
        msgs = msgs.filter(id__lt=last_msg_id)
    else:
        num = 30
    if len(msgs) < num: num = len(msgs)

    return msgs[:num]


@database_sync_to_async
def create(user: Account, dm: Dm, content: str) -> Message:
    '''Создаёт, сохраняет и возвращает новое сообщение'''
    return Message.objects.create(user=user, dm=dm, message=content)


@database_sync_to_async
def mark_read(id: int) -> None:
    '''Отмечает сообщение прочитанным по id'''
    msg = Message.objects.get(pk=id)
    msg.read = True
    msg.save()
