from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

__author__ = "Alan Viars"

groups = ["Member",
          "OrganizationPointOfContact",
          "OrganizationalAgent",
          "IdentityAssuranceTrustedReferee",
          "OrganizationAdministrator"]


def create_groups():

    created_groups = []
    for group in groups:
        g, created = Group.objects.get_or_create(name=group)
        created_groups.append(g)

        # Give POC Permissions
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
    help = 'Create default groups %s ' % (groups)

    def handle(self, *args, **options):
        
        g = create_groups()
        print("Groups %s created" % (g))