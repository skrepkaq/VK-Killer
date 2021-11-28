from django.contrib import admin
from account.models import Account, Friend, Dm, Message


admin.site.register(Account)
admin.site.register(Friend)
admin.site.register(Dm)
admin.site.register(Message)
