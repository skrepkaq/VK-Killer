from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from .services import avatar


class AccountManager(BaseUserManager):
    def create_user(self, email, username, password):
        user = self.model(email=email,
                          username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email=email,
                                password=password,
                                username=username)
        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user

    def get_queryset(self):
        return super(AccountManager, self).get_queryset().filter(is_active=True)


class AccountManagerALL(models.Manager):
    def get_query_set(self):
        return super(AccountManagerALL, self).get_query_set()


class Account(AbstractBaseUser):
    email = models.EmailField(max_length=60, unique=True)
    username = models.CharField(max_length=20, unique=True)
    avatar = models.ImageField(upload_to='avatars')
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_hidden_from_feed = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    last_seen = models.IntegerField(default=0)
    timezone = models.IntegerField(default=0)
    url = models.CharField(blank=True, null=True, max_length=25)
    feed_position = models.CharField(max_length=1, default='w')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = AccountManager()
    objects_all = AccountManagerALL()

    def save(self, *args, **kwargs):
        if not self.avatar:
            # если у пользователя нет аватарки - сгенерировать и сохранить
            self.avatar = 'avatars/defaults/' + avatar.create(self.username)
        if not self.url:
            # стандартный url = id пользователя
            self.url = self.id
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class Friend(models.Model):
    users = models.ManyToManyField(Account, related_name='friend_offers')
    users_accepted = models.ManyToManyField(Account, related_name='friends')


class Dm(models.Model):
    users = models.ManyToManyField(Account, related_name='dms')


class Message(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='messages')
    dm = models.ForeignKey(Dm, on_delete=models.CASCADE, related_name='messages')
    message = models.CharField(max_length=5000)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.message


class Post(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='posts')
    message = models.CharField(max_length=5000, blank=True)
    image = models.ImageField(upload_to='images', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    likes = models.ManyToManyField(Account, blank=True, related_name='liked_posts')


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='liked_comments')
    message = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(Account, blank=True)


class BanWord(models.Model):
    word = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.word
