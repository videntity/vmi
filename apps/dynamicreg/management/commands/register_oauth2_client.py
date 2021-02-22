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


def register_app(client_name, client_id=None,
                 client_secret=None,
                 redirect_uris=[],
                 client_type='confidential',
                 grant_type='authorization-code',
                 skip_authorization=None, username=None):

    dynreg = OrderedDict()
    dynreg['client_name'] = client_name
    if not client_id:
        client_id = str(uuid.uuid4())
    if not client_secret:
        client_secret = str(uuid.uuid4())
    if not skip_authorization:
        skip_authorization = False

    dynreg['client_id'] = client_id
    dynreg['client_secret'] = client_secret
    dynreg['redirect_uris'] = redirect_uris
    dynreg['client_type'] = client_type
    dynreg['reasponse_types'] = ['code', 'id_token']
    dynreg['grant_types'] = ['authorization_code', 'refresh_token']

    if Application.objects.filter(client_id=client_id).exists():
        application = Application.objects.get(client_id=client_id)
        application.client_secret = client_secret
        application.name = client_name
        application.skip_authorization = skip_authorization
        application.redirect_uris = ' '.join(redirect_uris)
        application.client_type = client_type
        application.authorization_grant_type = grant_type
        application.save()

    else:
        application = Application.objects.create(client_id=client_id,
                                                 client_secret=client_secret,
                                                 name=client_name,
                                                 skip_authorization=skip_authorization,
                                                 redirect_uris=' '.join(redirect_uris),
                                                 client_type='confidential',
                                                 authorization_grant_type='authorization-code')

    if username:
        user = User.objects.get(username=username)
        application.user = user
        application.save()

    dynreg['grant_types'] = [
        application.authorization_grant_type, "refresh_token"]
    return dynreg


class Command(BaseCommand):
    help = 'Register an OAuth2 client/ relying party'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('client_name', nargs='?',
                            default=str(uuid.uuid4()))
        parser.add_argument('client_id', nargs='?')
        parser.add_argument('--redirect_uris', nargs='+',
                            help="A required list or redirect URIS", default=[])
        parser.add_argument('--client_secret', default=None)
        parser.add_argument('--client_type', default='confidential')
        parser.add_argument('--grant_type', default='authorization_code')
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

            dynreg = register_app(options['client_name'],
                                  options['client_id'],
                                  options['client_secret'],
                                  options['redirect_uris'],
                                  options['client_type'],
                                  options['grant_type'],
                                  options['skip_authorization'],
                                  options['username'],
                                  )
            self.stdout.write(json.dumps(dynreg, indent=4))
