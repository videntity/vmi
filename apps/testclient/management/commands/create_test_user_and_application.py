from django.core.management.base import BaseCommand
from apps.accounts.models import UserProfile
from django.contrib.auth import get_user_model
from oauth2_provider.models import Application
from oauth2_provider.models import AccessToken
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.urls import reverse


def create_user():
    User = get_user_model()
    if User.objects.filter(username="fred").exists():
        User.objects.filter(username="fred").delete()
    u = User.objects.create_user(username="fred",
                                 first_name="Fred",
                                 last_name="Flinstone",
                                 email='fred@example.com',
                                 password="foobarfoobarfoobar",)
    UserProfile.objects.create(user=u)
    return u


def create_application(user):
    Application.objects.filter(name="TestApp").delete()
    redirect_uri = r"%s%s" % (settings.HOSTNAME_URL,
                              reverse('testclient-callback'))
    if not(redirect_uri.startswith("http://") or redirect_uri.startswith("https://")):
        redirect_uri = "https://" + redirect_uri
    a = Application.objects.create(name="TestApp",
                                   redirect_uris=redirect_uri,
                                   user=user,
                                   client_type="confidential",
                                   authorization_grant_type="authorization-code")

    return a


def create_test_token(user, application):

    now = timezone.now()
    expires = now + timedelta(days=1)
    t = AccessToken.objects.create(user=user, application=application,
                                   token="sample-token-string",
                                   expires=expires)
    return t


class Command(BaseCommand):
    help = 'Create a test user and application for the test client (a.k.a. relying party).'

    def handle(self, *args, **options):
        u = create_user()
        a = create_application(u)
        t = create_test_token(u, a)
        self.stdout.write("Name:", a.name)
        self.stdout.write("client_id:", a.client_id)
        self.stdout.write("client_secret:", a.client_secret)
        self.stdout.write("access_token:", t.token)
        self.stdout.write("redirect_uri:", a.redirect_uris)
