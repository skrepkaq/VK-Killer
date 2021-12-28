import os
import re
import datetime
from django.db.models import Count, Value, Q
from channels.db import database_sync_to_async
from account.models import Account, Comment, Post, BanWord
from account.services import images, friends, online

path = 'media/images/'
if not os.path.exists(path):
    os.makedirs(path)


@database_sync_to_async
def get(user: Account, sourse_info: dict, last_post_id: int) -> list[dict]:
    '''Возвращает список сериализованных постов'''
    num = 10 if last_post_id > 1 else 15  # Количество постов загружаемых за раз, в первый раз

    if sourse_info["type"] == 'profile':
        posts = _get_profile_posts(sourse_info["id"], last_post_id, num)

    elif sourse_info["type"] == 'post':
        posts = _get_post(sourse_info["id"])

    elif sourse_info["type"] == 'feed':
        feed_mode = sourse_info["mode"]
        posts = _get_feed_posts(user, last_post_id, feed_mode, num)

    out_posts = _serialize_posts(posts, user.timezone if user.is_authenticated else 0, sourse_info["type"] != 'post')
    return out_posts


def _get_post(post_id: int) -> Post:
    '''Возвращает конкретный пост'''
    return Post.objects.filter(pk=post_id).annotate(is_random_post=Value(False))


def _get_profile_posts(profile_id: int, last_post_id: int, num: int) -> list[Post]:
    '''Возвращает посты пользователя'''
    profile = Account.objects.get(pk=profile_id)

    posts = profile.posts.all().annotate(is_random_post=Value(False)).order_by('-id')
    return _get_only_lt_id(posts, last_post_id, num)


def _get_feed_posts(user: Account, last_post_id: int, mode: int, num: int):
    '''Возвращает посты ленты в зависимости от её типа'''
    if mode == 0:
        # лента из постов друзей
        posts = _get_only_lt_id(_get_posts_of_friends(user), last_post_id, num)
        # подмешать случайные посты (3 в нормальном случае и до 10 если от друзей закончились)
        posts += _get_random_posts(user, (num-len(posts) if len(posts) < num else 3), 14)
    elif mode == 1:
        # лента из популярных постов за последние 3 дня
        posts = _get_trending_posts(last_post_id, num, 3)
    elif mode == 2:
        # лента из случайных постов за последние 14 дней
        posts = _get_random_posts(user, num, 14)
    return posts


def create(request) -> bool:
    '''
    Проверяет картинку на размер, валидность, сжимает и сохраняет её.
    Создаёт пост и в случае успеха возвращает True
    '''
    if request.method == 'POST':
        if request.POST['action'] == "create_post":
            image = request.FILES.get('image')
            message = request.POST.get('message')

            image_fin_str = ''
            if image:
                if image.size > 20971520:
                    return False
                filename = images.save(image.read(), path, 'image', 500)
                if not filename:
                    return False
                image_fin_str = 'images/' + filename
            else:
                if not message or all([s == ' ' for s in message]):
                    return False
            Post.objects.create(user=request.user, message=message, image=image_fin_str)
            return True


def send_comment(request, post_id: int) -> bool:
    '''
    Создаёт новый комментарий, если успешно возвращает True
    '''
    if request.method == 'POST':
        if request.POST['action'] == "send_comment":
            message = request.POST.get('message')
            post = _get_by_id(post_id, Post)
            if re.fullmatch(r'.{1,200}', message) and not all([s == ' ' for s in message]) and post:
                try:
                    comm = post.comments.all().latest('pk')
                    if comm.user == request.user and comm.message == message: return
                    # нельзя писать несколько одинаковых комментариев подряд
                except Comment.DoesNotExist:
                    pass
                Comment.objects.create(post=post, user=request.user, message=message)
                return True


@database_sync_to_async
def delete(user: Account, post_id: int) -> bool:
    '''Удаляет пост. В случае успеха возвращает True'''
    post = _get_by_id(post_id, Post)
    if post and post.user == user:
        post.delete()
        return True


@database_sync_to_async
def like(user: Account, content_type: str, id: int) -> None:
    '''Ставит или убирает лайк с поста/коммента'''
    content = _get_by_id(id, Post if content_type == 'post' else Comment)
    if not content or not user.is_authenticated: return

    if user in content.likes.all():
        content.likes.remove(user)
    else:
        content.likes.add(user)


def _get_by_id(id: int, content) -> Post:
    '''Возвращает пост или комментарий по id'''
    try:
        instance = content.objects.get(pk=id)
    except content.DoesNotExist:
        return False
    return instance


def _get_posts_of_friends(user: Account) -> list[Post]:
    '''Возвращает посты друзей пользователя'''
    friends_users = friends.get_my_offers(user)
    return Post.objects.filter(user__in=friends_users).annotate(is_random_post=Value(False)).order_by('-id')


def _get_random_posts(user: Account, count: int, in_last: int = None) -> list[Post]:
    '''
    Возвращает count или меньше случайных постов за последние in_last дней
    (исключая посты от user и от скрытых пользователей)
    '''

    posts = Post.objects.filter(~Q(user=user) & Q(user__is_hidden_from_feed=False))\
                        .annotate(is_random_post=Value(True)).order_by('?')

    banwords = BanWord.objects.all()
    if banwords:
        banwords_re = f'({"|".join([w.word for w in banwords])})'
        posts = posts.exclude(message__regex=banwords_re)

    if in_last:
        time_threshold = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=in_last)
        posts = posts.filter(timestamp__gt=time_threshold)
    if len(posts) < count:
        count = len(posts)
    return posts[:count]


def _get_trending_posts(loaded_posts_count: int, count: int, in_last: int = None) -> list[Post]:
    '''
    Возвращает посты за последние in_last дней, с индеком
    больше loaded_posts_count и сортирует их по лайкам
    '''
    time_threshold = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=in_last)
    posts = Post.objects.filter(Q(user__is_hidden_from_feed=False)
                                & Q(timestamp__gt=time_threshold)).annotate(l_count=Count('likes'))\
                        .annotate(is_random_post=Value(False)).order_by('-l_count')
    posts = posts[loaded_posts_count:]
    return _get_only_lt_id(posts, -1, count)


def _get_only_lt_id(posts: list[Post], last_post_id: int, num: int) -> list[Post]:
    '''Возвращает num постов, если есть и только с id поста меньше last_post_id, если last_post_id > 0'''
    if last_post_id > 0:
        posts = posts.filter(id__lt=last_post_id)
    if len(posts) < num: num = len(posts)
    return posts[:num]


def _serialize_posts(psts: list[Post], tz: int, only_top_comment: bool) -> list[dict]:
    '''Подготавливает посты с комментариями для отправки по ws'''
    out_posts = []
    for p in psts:
        comments = p.comments.all()
        comments_count = len(comments)

        if comments and only_top_comment:
            comments = [max(comments, key=lambda x: len(x.likes.all()))]

        comments = [{'user': {'id': com.user.id,
                              'username': com.user.username,
                              'url': com.user.url,
                              'avatar': com.user.avatar.url},
                     'id': com.id,
                     'message': com.message,
                     'likes': [like.id for like in com.likes.all()]} for com in comments]

        out_posts.append({'user': {'id': p.user.id,
                                   'username': p.user.username,
                                   'url': p.user.url,
                                   'lastSeen': p.user.last_seen,
                                   'avatar': p.user.avatar.url},
                          'id': p.id,
                          'message': p.message,
                          'image': p.image.url if p.image else None,
                          'time': online.convert_datetime_to_str(p.timestamp, tz),
                          'is_random_post': p.is_random_post,
                          'comments': comments,
                          'comments_count': comments_count,
                          'likes': [like.id for like in p.likes.all()]})
    return out_posts
