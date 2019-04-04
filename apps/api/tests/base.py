from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from oauth2_provider.models import get_application_model, get_access_token_model
from oauth2_provider.settings import oauth2_settings
from apps.accounts.models import UserProfile

User = get_user_model()
Application = get_application_model()
AccessToken = get_access_token_model()


class BaseTestCase(TestCase):
    maxDiff = None

    def get_username(self):
        return "bob"

    def get_password(self):
        return "fubar"

    def get_permissions(self):
        return Permission.objects.filter(
            content_type=ContentType.objects.get_by_natural_key('accounts', 'userprofile'),
        ).all()

    def get_user(self):
        user = User.objects.create(
            username=self.get_username(),
            password=self.get_password(),
        )
        UserProfile.objects.create(
            user=user,
        )
        for permission in self.get_permissions():
            user.user_permissions.add(permission)
        return User.objects.get(pk=user.pk)

    def get_expires(self):
        return timezone.now() + timedelta(
            seconds=oauth2_settings.AUTHORIZATION_CODE_EXPIRE_SECONDS)

    def get_client(self):
        return Application.objects.create(
            name="test",
        )

    def setUp(self):
        self.token = AccessToken.objects.create(
            user=self.get_user(),
            application=self.get_client(),
            expires=self.get_expires(),
            token="test",
        )
