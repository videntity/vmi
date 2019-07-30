from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

__author__ = "Alan Viars"


def create_groups():
    groups = ["Member",
              "OrganizationPointOfContact",
              "OrganizationalAgent",
              "TrustedReferee",
              "OrganizationAdministrator"]
    created_groups = []
    for group in groups:
        g, created = Group.objects.get_or_create(name=group)
        created_groups.append(g)

        if group == "OrganizationPointOfContact":
            # Add permissions to group
            content_type = ContentType.objects.get(
                app_label='accounts', model='organizationaffiliationrequest')
            can_approve_permission = Permission.objects.get(codename='can_approve_affiliation',
                                                            content_type=content_type)
            g.permissions.add(can_approve_permission)
            g.save()
    return dict(zip(groups, created_groups))


class Command(BaseCommand):
    help = 'Create Groups. Run only 1x at initial setup.'

    def handle(self, *args, **options):
        create_groups()
