# VK Killer

#### Надоело что ФСБ читает твои переписки?
#### Отлично! Ведь никто даже не подумает что ты будешь обсуждать свои секретные секреты тут.
#### Это эквивалент голубиной почты или радио из стаканчиков - супер секретно и надёжно(146%)
#

Используется [Django](https://www.djangoproject.com/) фреймворк с [Django Channels](https://github.com/django/channels) аддоном для работы с вебсокетами

[Redis](https://redis.io/) для работы Django Channels в async режиме

А так же [Docker](https://www.docker.com/)


## Установка

### Из-за бага в Python, не работает на версии 3.10, используйте более ранние!

1. Установите [Docker](https://www.docker.com/)
2. Создайте и активируйте [venv](https://docs.python.org/3/library/venv.html)
3. Используя [pip](https://pip.pypa.io/en/stable/) установите библиотеки из **requirements.txt**.
```bash
pip install -r requirements.txt
```
4. Мигрируйте базу данных с помощью файла **manage.py** из директории **src** ***(следует делать после каждого нового коммита)***
```bash
python manage.py migrate
```

## Использование

1. Запустите сервер с помощью Docker
```bash
docker compose up -d
```
2. Заходите на [http://localhost:8000](http://localhost:8000)
3. Profit!
