from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

__author__ = "Alan Viars"


def create_groups():
    groups = ["ChangeIdentityAssuranceLevel",
              "ApproveOrganizationalAffiliation",
              "RegisterOAuth2ClientApps"]
    created_groups = []
    for group in groups:
        g, created = Group.objects.get_or_create(name=group)
        created_groups.append(created)
    return dict(zip(groups, created_groups))


class Command(BaseCommand):
    help = 'Create Groups. Run only 1x at initial setup.'

    def handle(self, *args, **options):
        create_groups()
