import os
import re
from channels.db import database_sync_to_async
from account.models import Account, Comment, Post
from account.services import images, friends


path = 'media/images/'
if not os.path.exists(path):
    os.makedirs(path)


@database_sync_to_async
def get(sourse_info: dict, last_post_id: int) -> list[dict]:
    '''Возвращает запрошенные посты'''
    num = 10 if last_post_id > 1 else 15  # Количество постов загружаемых за раз, в первый раз
    if sourse_info["type"] in ['profile', 'feed']:
        sourse = Account.objects.get(pk=sourse_info["id"])

        if sourse_info["type"] == 'feed':
            # лента из постов друзей
            posts = _get_posts_of_friends(sourse).order_by('-id')
        else:
            # посты конкретного пользователя
            posts = sourse.posts.all().order_by('-id')

        if last_post_id > 0:
            posts = posts.filter(id__lt=last_post_id)
        if len(posts) < num: num = len(posts)

        return posts[:num]
    elif sourse_info["type"] == 'post':
        # конкретный пост
        return Post.objects.filter(pk=sourse_info["id"])


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
            if re.fullmatch(r'.{1,200}', message) and post:
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
    if not content: return

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
    return Post.objects.filter(user__in=friends_users)


def _get_random_posts(count: int) -> list[Post]:
    '''Возвращает count или меньше случайных постов'''
    posts = Post.objects.order_by('?')
    if len(posts) < count:
        count = len(posts)
    return posts[:count]
