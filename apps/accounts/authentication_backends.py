from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import UserProfile

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom Email Backend to perform authentication via email
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.EMAIL_FIELD)
        if username is None or password is None:
            return
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            user = User._default_manager.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None


class SubjectBackend(ModelBackend):
    """
    Custom Subject Backend to perform authentication via subject / account number.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return
        try:
            up = UserProfile.objects.get(subject=username)
            user = up.user

        except User.DoesNotExist:
            return None
        except UserProfile.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            return None

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            user = User._default_manager.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
