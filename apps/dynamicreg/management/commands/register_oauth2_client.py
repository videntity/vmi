from django.core.management.base import BaseCommand, CommandError
from oauth2_provider.models import Application
from django.contrib.auth import get_user_model
from collections import OrderedDict
import json
import uuid

__author__ = "Alan Viars"

User = get_user_model()


def delete_app(client_id):
    try:
        application = Application.objects.get(client_id=client_id)
        application.delete()
        return application
    except Application.DoesNotExist:
        raise CommandError(
            "Application %s not deleted because it doesn't exist." % (client_id))


def register_app(client_id, client_name, redirect_uris=[],
                 skip_authorization=False, username=None):

    dynreg = OrderedDict()
    dynreg['client_name'] = client_name
    dynreg['client_id'] = client_id
    dynreg['redirect_uris'] = redirect_uris
    application, g_o_c = Application.objects.get_or_create(
        client_id=dynreg['client_id'])
    application.name = dynreg['client_name']
    application.redirect_uris = dynreg['redirect_uris']
    application.client_type = 'confidential'
    application.authorization_grant_type = 'authorization-code'
    application.skip_authorization = skip_authorization
    application.save()

    if username:
        user = User.objects.get(username=username)
        application.user = user
        application.save()
    dynreg['client_secret'] = application.client_secret
    dynreg['grant_types'] = [
        application.authorization_grant_type, "refresh_token"]
    return dynreg


class Command(BaseCommand):
    help = 'Register an OAuth2 client/ relying party'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('client_id', nargs='?')
        parser.add_argument('client_name', nargs='?',
                            default=str(uuid.uuid4()))
        parser.add_argument('--redirect_uris', nargs='+',
                            help="A required list or redirect URIS")
        parser.add_argument('--client_secret', nargs='?', default=None)
        parser.add_argument('--skip_authorization', nargs='?',
                            default=False, type=int)
        parser.add_argument('--username', nargs='?', default=None)

        # Perform a delete
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete application instead of closing it.',
        )

    def handle(self, *args, **options):
        if options['delete']:
            delete_app(options['client_id'])
            self.stdout.write("%s application deleted." %
                              (options['client_id']))
        else:

            dynreg = register_app(options['client_id'], options['client_name'],
                                  options['redirect_uris'],
                                  options['skip_authorization'],
                                  options['username'],
                                  )
            self.stdout.write(json.dumps(dynreg, indent=4))
