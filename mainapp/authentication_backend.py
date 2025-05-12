from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=email))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
