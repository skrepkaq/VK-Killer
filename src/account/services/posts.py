import os
import time
from account.models import Account, Post
from account.services import images


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
                if image.size > 20971520:
                    return False
                filename = images.save(image.read(), path, 'image', 500)
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
