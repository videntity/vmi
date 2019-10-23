from django.core.management.base import BaseCommand
from ...models import Organization
from django.contrib.auth.models import Group

__author__ = "Alan Viars"


organizations = [{"name": "CBO XYZ", "slug": "cbo-xyz"},
                 {"name": "ACME Health", "slug": "acme-health"},
                 {"name": "Onboarding", "slug": "onboarding"},
                 ]

default_groups_for_org_agents = [
    'OrganizationalAgent', 'IdentityAssuranceTrustedReferee']


def create_user(username, password, email, first_name, last_name):
    try:
        u = User.objects.get(username=username)
    except User.DoesNotExist:
        # Otherwise we instantiate the super user
        u = User(username=username, first_name=first_name, last_name=last_name,
                 email=email)
    u.set_password(password)
    u.save()
    return True



def create_sample_organizations():
    # Pass - removing this is problematic and unnecessary.
    return []


class Command(BaseCommand):
    help = 'Create sample organizations. %s' % (organizations)

    def handle(self, *args, **options):

        orgs = create_sample_organizations()
        print("Organizations %s created if they did not already exist." % (orgs))
