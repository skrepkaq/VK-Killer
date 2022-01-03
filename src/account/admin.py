from django.contrib import admin
from account.models import Account, Friend, Dm, Message, Post, Comment, BanWord


class AccountAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = self.model.objects_all.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


admin.site.register(Account, AccountAdmin)
admin.site.register(Friend)
admin.site.register(Dm)
admin.site.register(Message)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(BanWord)
