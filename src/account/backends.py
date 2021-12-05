from django.contrib.auth import backends
from django.db.models import Q
from account.models import Account


class MyBackend(backends.ModelBackend):
    def authenticate(self, _, password=None, email=None):
        try:
            user = Account.objects.get(Q(username__iexact=email) | Q(email__iexact=email))
            if user.check_password(password):
                return user
        except Account.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            Account().set_password(password)
