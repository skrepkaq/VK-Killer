import os
import hashlib
from PIL import Image
from django.contrib import messages
from account.services import images


path = 'media/avatars/'
if not os.path.exists(path + 'defaults/'):
    os.makedirs(path + 'defaults/')


def create(username: str) -> str:
    '''
    Создаёт и сохраняет аватарку с цветом, зависящим от ника.
    Возвращает имя файла
    '''
    img = Image.open(path + 'template.png')
    img = img.convert("RGB")

    color = _get_color(username)
    file_name = ' '.join(map(str, color)) + '.png'

    new_image_data = []
    for item in img.getdata():
        if item[0] < 50:
            new_image_data.append(color)  # если цвет чёрный - перекрасить
        else:
            new_image_data.append(item)

    img.putdata(new_image_data)
    img.save(path + 'defaults/' + file_name)
    return file_name


def _get_color(username: str) -> tuple[int]:
    '''
    Создаёт RGB цвет где один из цветов = 0, другой = 255, а оставшийся 0-255,
    строго основываясь на нике, никакого рандома
    '''
    name_bytes = hashlib.sha256(username.encode()).digest()
    color = [0, name_bytes[5], 255]  # цвет в формате [0, 0-255, 255]

    for _ in range(5):  # перемешать 5 раз
        for i in range(3):
            ran_n = name_bytes[i*5]%3  # случайное число 0-2
            color[i], color[ran_n] = color[ran_n], color[i]  # поменять местами два случайных значения

    return tuple(color)


def update(request) -> bool:
    '''
    Обрабатывает и сохраняет аватарку пользователю.
    Возвращает True если была попытка изменить аватарку
    '''
    if request.method == 'POST':
        if request.POST['action'] == "change_avatar":
            image = request.FILES.get('image')
            if image:
                print(image.content_type)
                if image.content_type.startswith('image/'):
                    if image.size < 20971520:
                        filename = images.save(image.read(), path, 'avatar', 300)
                        if filename:
                            request.user.avatar = 'avatars/' + filename
                            request.user.save()
                        else:
                            messages.error(request, 'Файл повреждён')
                    else:
                        messages.error(request, 'Изображене должно быть меньше 20МБ')
                else:
                    messages.error(request, 'Неверный формат изображения')
            return True
    return False
