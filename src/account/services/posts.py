import os
import time
import re
from account.models import Account, Comment, Post
from account.services import images


path = 'media/images/'
if not os.path.exists(path):
    os.makedirs(path)


def get_all(user: Account) -> list[dict]:
    '''Возвращает все посты пользователя'''
    return [_serialize_post(p, True) for p in Post.objects.filter(user=user)]


def get(id: int) -> dict:
    '''Возвращает готовый для отображения пост по id'''
    post = _get_by_id(id, Post)
    if not post: return False
    return _serialize_post(post)


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


def delete(request) -> bool:
    '''Удаляет пост. В случае успеха возвращает True'''
    if request.method == 'POST':
        if request.POST['action'].startswith('delete_post'):
            post_id = request.POST['action'].split('_')[2]
            post = _get_by_id(post_id, Post)
            if post and post.user == request.user:
                post.delete()
                return True


def like(request) -> bool:
    '''Ставит или убирает лайк с поста/коммента. Возвращает True в случае успеха'''
    if request.method == 'POST':
        if request.POST['action'].startswith('like'):
            content_id = request.POST['action'].split('_')[-1]
            content_type = request.POST['action'].split('_')[1]

            content = _get_by_id(content_id, Post if content_type == 'post' else Comment)
            if not content: return False

            if request.user in content.likes.all():
                content.likes.remove(request.user)
            else:
                content.likes.add(request.user)
            return True
    return False


def _get_by_id(id: int, content) -> Post:
    '''Возвращает пост или комментарий по id'''
    try:
        instance = content.objects.get(pk=id)
    except content.DoesNotExist:
        return False
    return instance


def _serialize_post(p: Post, only_top_comment=False) -> dict:
    '''Подготавливает пост с комментариями для отображения'''
    comments = p.comments.all()
    comments_count = len(comments)

    if only_top_comment and comments:
        comments = sorted(comments, key=lambda x: len(x.likes.all()), reverse=True)[:1]

    return {'user': {'id': p.user.id,
                     'username': p.user.username,
                     'avatar': p.user.avatar.url},
            'id': p.id,
            'message': p.message,
            'image': p.image,
            'time': time.strftime("%H:%M", p.timestamp.timetuple()),
            'comments': comments,
            'comments_count': comments_count,
            'likes': p.likes.all()}
