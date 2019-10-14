from django.core.management.base import BaseCommand
from ...models import Organization

__author__ = "Alan Viars"


organizations = [{"name": "CBO XYZ", "slug": "cbo-xyz"},
                 {"name": "ACME Health", "slug": "acme-health"},
                 {"name": "Onboarding", "slug": "onboarding"},
                 ]


def create_sample_organizations():

    created_orgs = []
    for organization in organizations:
        o, created = Organization.objects.get_or_create(name=organization['name'],
                                                        slug=organization['slug'])
        created_orgs.append(o)

    return created_orgs


class Command(BaseCommand):
    help = 'Create sample organizations. %s' % (organizations)

    def handle(self, *args, **options):

        orgs = create_sample_organizations()
        print("Organizations %s created if they did not already exist." % (orgs))
