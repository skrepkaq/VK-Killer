import io
import uuid
from PIL import Image


def save(image_bytes: bytes, path: str, mode: str, max_size: int) -> str:
    '''
    Обрабатывает картинку (масшатабирует под max_size и обрезает до квардата если mode == 'avatar'.
    Сохраняет её в path и возвращает имя файла
    '''
    try:
        image = Image.open(io.BytesIO(image_bytes))

        if mode == 'avatar':
            image = _crop_to_square(image)
        image = _resize(image, max_size)

        filename = uuid.uuid4().hex + '.jpg'
        image.convert('RGB').save(path + filename, optimize=True, quality=75)
        return filename
    except Exception:
        return None


def _resize(image: Image, max_size: int) -> Image:
    '''Масштабирует картикну подгоняя её под максимальный размер'''
    width, height = image.size
    scale = max_size/max(image.size)
    if scale < 1:
        new_size = (int(width*scale), int(height*scale))
        image = image.resize(new_size, Image.ANTIALIAS)
    return image


def _crop_to_square(image: Image) -> Image:
    '''Обрезает картинку до квадрата'''
    width, height = image.size
    square_size = min(image.size)

    return image.crop(((width - square_size) // 2,
                       (height - square_size) // 2,
                       (width + square_size) // 2,
                       (height + square_size) // 2))
