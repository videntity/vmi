from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

__author__ = "Alan Viars"

groups = ["Member",
          "ApplicationDeveloper",
          "OrganizationPointOfContact",
          "OrganizationalAgent",
          "IdentityAssuranceTrustedReferee",
          "OrganizationAdministrator",
          "OrganizationAgentReport",
          "DynamicClientRegistrationProtocol"
          ]


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
            view = Permission.objects.get(codename='view_organizationaffiliationrequest',
                                          content_type=content_type)
            change = Permission.objects.get(codename='change_organizationaffiliationrequest',
                                            content_type=content_type)
            delete = Permission.objects.get(codename='delete_organizationaffiliationrequest',
                                            content_type=content_type)
            add = Permission.objects.get(codename='add_organizationaffiliationrequest',
                                         content_type=content_type)
            g.permissions.add(can_approve_permission,
                              view, add, change, delete)
            g.save()

            # Allow view of Organizations
            content_type = ContentType.objects.get(
                app_label='accounts', model='organization')
            view = Permission.objects.get(codename='view_organization',
                                          content_type=content_type)
            g.permissions.add(view)
            g.save()

        # Give Organizational Administrator power to change orgs.
        if group == "OrganizationAdministrator":
            # Allow view of user
            content_type = ContentType.objects.get(
                app_label='accounts', model='organization')
            add = Permission.objects.get(codename='add_organization',
                                         content_type=content_type)
            change = Permission.objects.get(codename='change_organization',
                                            content_type=content_type)
            delete = Permission.objects.get(codename='delete_organization',
                                            content_type=content_type)
            view = Permission.objects.get(codename='view_organization',
                                          content_type=content_type)
            g.permissions.add(add, change, delete, view)
            g.save()

        # Give TrustedReferees permission to chane IAL information
        if group == "IdentityAssuranceTrustedReferee":
            # Allow view of user
            content_type = ContentType.objects.get(
                app_label='ial', model='identityassuranceleveldocumentation')
            add = Permission.objects.get(codename='add_identityassuranceleveldocumentation',
                                         content_type=content_type)
            change = Permission.objects.get(codename='change_identityassuranceleveldocumentation',
                                            content_type=content_type)
            delete = Permission.objects.get(codename='delete_identityassuranceleveldocumentation',
                                            content_type=content_type)
            view = Permission.objects.get(codename='view_identityassuranceleveldocumentation',
                                          content_type=content_type)
            g.permissions.add(add, change, delete, view)
            g.save()

        # Allow person to register an app
        if group == "ApplicationDeveloper":
            # Add permissions to group
            content_type = ContentType.objects.get(
                app_label='oauth2_provider', model='application')
            add = Permission.objects.get(codename='add_application',
                                         content_type=content_type)
            change = Permission.objects.get(codename='change_application',
                                            content_type=content_type)
            delete = Permission.objects.get(codename='delete_application',
                                            content_type=content_type)
            view = Permission.objects.get(codename='view_application',
                                          content_type=content_type)
            g.permissions.add(add, change, delete, view)
            g.save()

        if group == "OrganizationalAgent":
            # Allow view of user
            content_type = ContentType.objects.get(
                app_label='auth', model='user')
            view = Permission.objects.get(codename='view_user',
                                          content_type=content_type)
            change = Permission.objects.get(codename='change_user',
                                            content_type=content_type)
            add = Permission.objects.get(codename='add_user',
                                         content_type=content_type)
            g.permissions.add(view, change, add)
            g.save()

            # Allow view/change of user profile
            content_type = ContentType.objects.get(
                app_label='accounts', model='userprofile')
            view = Permission.objects.get(codename='view_userprofile',
                                          content_type=content_type)
            change = Permission.objects.get(codename='change_userprofile',
                                            content_type=content_type)
            delete = Permission.objects.get(codename='delete_userprofile',
                                            content_type=content_type)
            g.permissions.add(change, delete, view)
            g.save()

            # Allow view/change/delete/add of addresses.
            content_type = ContentType.objects.get(
                app_label='accounts', model='address')
            add = Permission.objects.get(codename='add_address',
                                         content_type=content_type)
            view = Permission.objects.get(codename='view_address',
                                          content_type=content_type)
            change = Permission.objects.get(codename='change_address',
                                            content_type=content_type)
            delete = Permission.objects.get(codename='delete_address',
                                            content_type=content_type)
            g.permissions.add(change, delete, view, add)
            g.save()

            # Allow view/change/delete/add of individual identifiers.
            content_type = ContentType.objects.get(
                app_label='accounts', model='individualidentifier')
            add = Permission.objects.get(codename='add_individualidentifier',
                                         content_type=content_type)
            view = Permission.objects.get(codename='view_individualidentifier',
                                          content_type=content_type)
            change = Permission.objects.get(codename='change_individualidentifier',
                                            content_type=content_type)
            delete = Permission.objects.get(codename='delete_individualidentifier',
                                            content_type=content_type)
            g.permissions.add(change, delete, view, add)
            g.save()

            # Allow view of Organizations
            content_type = ContentType.objects.get(
                app_label='accounts', model='organization')
            view = Permission.objects.get(codename='view_organization',
                                          content_type=content_type)
            g.permissions.add(view)
            g.save()

    return dict(zip(groups, created_groups))


class Command(BaseCommand):
    help = 'Create default groups %s ' % (groups)

    def handle(self, *args, **options):

        g = create_groups()
        print("Groups %s created if they did not already exist." % (g))
