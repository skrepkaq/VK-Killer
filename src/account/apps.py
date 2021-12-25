from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    def ready(self):
        import time
        from django.db.models import F
        from account.models import Account

        Account.objects.filter(last_seen=-1).update(last_seen=time.time())
        Account.objects.filter(url='').update(url=F('id'))
