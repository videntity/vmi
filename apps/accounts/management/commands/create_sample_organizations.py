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


def create_sample_organizations():

    created_orgs = []
    for organization in organizations:

        o, created = Organization.objects.get_or_create(name=organization['name'],
                                                        slug=organization['slug'])

        for g in default_groups_for_org_agents:
            group, created = Group.objects.get_or_create(name=g)
            o.default_groups_for_agents.add(group)
            o.save()

        created_orgs.append(o)

    return created_orgs


class Command(BaseCommand):
    help = 'Create sample organizations. %s' % (organizations)

    def handle(self, *args, **options):

        orgs = create_sample_organizations()
        print("Organizations %s created if they did not already exist." % (orgs))
