from django.contrib import admin
from .models import (UserProfile, Organization,
                     Address, OrganizationIdentifier,
                     IndividualIdentifier,
                     OrganizationAffiliationRequest, PhoneVerifyCode,
                     PersonToPersonRelationship)


# Copyright Videntity Systems Inc.

__author__ = "Alan Viars"


class PersonToPersonRelationshipAdmin(admin.ModelAdmin):
    list_display = ('grantor', 'grantee', 'description', 'created_at')
    search_fields = [
        'grantor__first_name',
        'grantor__last_name',
        'grantee__first_name',
        'grantee__last_name',
        'grantor__email',
        'grantee__email',
        'grantor__username',
        'grantee__username',
    ]

    raw_id_fields = ("grantor", "grantee")


admin.site.register(PersonToPersonRelationship,
                    PersonToPersonRelationshipAdmin)


class PhoneVerifyCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'expires')
    search_fields = [
        'user__first_name',
        'user__last_name', ]
    raw_id_fields = ("user", )


admin.site.register(PhoneVerifyCode, PhoneVerifyCodeAdmin)


class OrganizationAffiliationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'created_at')
    search_fields = [
        'user__first_name',
        'user__last_name',
        'organization__name',
        'organization__slug']
    raw_id_fields = ("user", )


admin.site.register(
    OrganizationAffiliationRequest,
    OrganizationAffiliationRequestAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'birth_date',
                    'sex', 'subject', 'picture_url')
    search_fields = [
        'user__first_name',
        'user__last_name',
        'birth_date',
        'sex', ]
    raw_id_fields = ("user", )
    empty_value_display = ''


admin.site.register(UserProfile, UserProfileAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'signup_url', 'domain', 'picture_url')
    search_fields = ['name', 'slug', 'org_identifiers__name']
    raw_id_fields = ("point_of_contact", "members", "users", "addresses")
    empty_value_display = ''


admin.site.register(Organization, OrganizationAdmin)


class OrganizationIdentifierAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'type')
    search_fields = ['name', 'value', 'type']


admin.site.register(OrganizationIdentifier, OrganizationIdentifierAdmin)


class IndividualIdentifierAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'type')
    search_fields = ['name', 'value', 'type']


admin.site.register(IndividualIdentifier, IndividualIdentifierAdmin)


admin.site.register(Address)
