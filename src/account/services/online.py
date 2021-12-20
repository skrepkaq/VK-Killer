import time
from channels.db import database_sync_to_async
from account.models import Account


@database_sync_to_async
def connect(user: Account) -> bool:
    '''
    Пользователь зашёл в онлайн - записать last_seen = -1
    Если это новая сессия а не обновление страницы возвращает True
    '''
    is_new_session = time.time() - user.last_seen > 10
    user.last_seen = -1
    user.save()
    return is_new_session


@database_sync_to_async
def disconnect(user: Account) -> None:
    '''Пользователь вышел из онлайна - записать последнее время'''
    user.last_seen = time.time()
    user.save()
