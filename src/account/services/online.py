import time
import locale
from datetime import datetime, timezone, timedelta
from channels.db import database_sync_to_async
from account.models import Account


locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))


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


@database_sync_to_async
def set_timezone(user: Account, timezone: int) -> None:
    '''Обновляет часовой пояс пользователя'''
    if user.timezone != timezone:
        user.timezone = timezone
        user.save()


def get_last_seen_info(user: Account, profile_user: Account) -> str:
    '''Возвращает статус онлайна пользователя с учётом часового пояса'''
    if profile_user.last_seen == 0: return ''
    if profile_user.last_seen == -1: return 'Online'
    offline_time = time.time() - profile_user.last_seen
    if offline_time < 300: return 'Был в сети только что'
    if offline_time < 3600: return f'Был в сети {int(offline_time//60)} минут назад'

    t = datetime.fromtimestamp(profile_user.last_seen, timezone(-timedelta(minutes=user.timezone)))
    tnow = datetime.fromtimestamp(time.time(), timezone(-timedelta(minutes=user.timezone)))

    if tnow.strftime('%d') == t.strftime('%d'):
        day = 'сегодня'
    else:
        day = t.strftime('%d %b')
    h_m = t.strftime('%H:%M')
    return f'Был в сети {day} {h_m}'


def convert_datetime_to_str(dt: datetime, tz: int) -> str:
    '''Конвертирует datetime во время с учётом часового пояса'''
    return dt.astimezone(tz=timezone(-timedelta(minutes=tz))).strftime('%H:%M %d %b')
