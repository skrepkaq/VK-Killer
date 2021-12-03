import io
import os
import secrets
import time
from PIL import Image
from account.models import Account, Post


path = 'media/images/'
if not os.path.exists(path):
    os.makedirs(path)


def get_all(user: Account) -> list[Post]:
    '''Возвращает все посты пользователя'''
    return [{'user': {'id': p.user.id,
                      'username': p.user.username,
                      'avatar': p.user.avatar.url},
             'id': p.id,
             'message': p.message,
             'image': p.image,
             'time': time.strftime("%H:%M", p.timestamp.timetuple()),
             'likes': p.likes.all()} for p in Post.objects.filter(user=user)]


def create(request) -> bool:
    '''
    Проверяет картинку на размер, валидность, сжимает и сохраняет её.
    Создаёт пост и в случаае успеха возвращает True
    '''
    if request.method == 'POST':
        if request.POST['action'] == "create_post":
            image = request.FILES.get('image')
            message = request.POST.get('message')

            image_fin_str = ''
            if image:
                if image.size > 10485760:
                    return False
                filename = _image_save(image.read())
                if not filename:
                    return False
                image_fin_str = 'images/' + filename
            Post.objects.create(user=request.user, message=message, image=image_fin_str)
            return True


def like(request) -> bool:
    '''Ставит или убирает лайк с поста. Возвращает True в случае успеха'''
    if request.method == 'POST':
        if request.POST['action'].startswith('like'):
            post_id = request.POST['action'].split('_')[1]
            post = Post.objects.get(pk=post_id)

            if request.user in post.likes.all():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)
            return True
    return False


def _image_save(image_bytes: bytes) -> str:
    '''
    Подгоняет размер картинки и сохраняет её.
    Возвращает имя файла
    '''
    try:
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        scale = 500/max(image.size)  # максимальный размер картинки 500x500px
        size = (int(width*scale), int(height*scale))
        print(scale, size)
        if scale < 1:
            image = image.resize(size, Image.ANTIALIAS)
        filename = secrets.token_hex(16) + '.jpg'
        image.convert('RGB').save(path + filename, optimize=True, quality=75)
        return filename
    except Exception:
        return None
