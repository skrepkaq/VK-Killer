from django.contrib import admin
from account.models import Account, Friend, Dm, Message, Post, Comment, BanWord


admin.site.register(Account)
admin.site.register(Friend)
admin.site.register(Dm)
admin.site.register(Message)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(BanWord)
