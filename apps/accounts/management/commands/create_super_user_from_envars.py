from __future__ import absolute_import
from __future__ import unicode_literals
from getenv import env
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

import logging

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


def create_superuser(username, password, email, first_name, last_name):
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        # Otherwise we instantiate the super user
        u = User(username=username, first_name=first_name, last_name=last_name,
                 email=email)
    u.set_password(password)
    u.is_superuser = True
    u.is_staff = True
    u.save()
    return True


class Command(BaseCommand):
    help = 'Create a super user'

    def handle(self, *args, **options):

        # get variables
        super_username = env("DJANGO_SUPERUSER_USERNAME", "superuser")
        super_password = env("DJANGO_SUPERUSER_PASSWORD", "")
        super_email = env("DJANGO_SUPERUSER_EMAIL", "superuser@example.com")
        super_first_name = env("DJANGO_SUPERUSER_FIRSTNAME", "Super")
        super_last_name = env("DJANGO_SUPERUSER_LASTNAME", "User")
        if super_username and super_password and super_email:
            # create a super user
            r = create_superuser(super_username, super_password, super_email,
                                 super_first_name, super_last_name)
            if r:
                logger.info('Superuser created/updated.')
            else:
                logger.info('Something went wrong creating/updating superuser')
        else:
            logger.debug(
                'Environment variables DJANGO_SUPERUSER_USERNAME,'
                'DJANGO_SUPERUSER_PASSWORD,',
                'DJANGO_SUPERUSER_EMAIL must be set '
                'before using this command.')
