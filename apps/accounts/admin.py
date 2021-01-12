from django.contrib import admin
from .models import (UserProfile, Organization,
                     Address, OrganizationIdentifier,
                     IndividualIdentifier,
                     OrganizationAffiliationRequest, PhoneVerifyCode,
                     PersonToPersonRelationship, IDCardConfirmation,
                     UpstreamIdentityProviderToUser,
                     UpstreamIdentityProviderUserAuthenticatorAssurance)


# Copyright Videntity Systems Inc.
__author__ = "Alan Viars"


class UpstreamIdentityProviderUserAuthenticatorAssuranceAdmin(admin.ModelAdmin):
    list_display = ('user', 'upstream_idp_sub', 'upstream_idp_vendor',
                    'amr', 'amr_list', 'aal', 'created_at')


admin.site.register(UpstreamIdentityProviderUserAuthenticatorAssurance,
                    UpstreamIdentityProviderUserAuthenticatorAssuranceAdmin)


class UpstreamIdentityProviderToUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'upstream_idp_sub', 'upstream_idp_vendor',
                    'created_at')
    search_fields = [
        'upstream_idp_sub',
        'upstream_idp_vendor',
        'user__first_name',
        'user__last_name',
        'user__email', 'user__username']


admin.site.register(UpstreamIdentityProviderToUser,
                    UpstreamIdentityProviderToUserAdmin)


class PersonToPersonRelationshipAdmin(admin.ModelAdmin):
    list_display = ('delegate', 'subject', 'relationship_type', 'created_by',
                    'created_at')

    search_fields = [
        'relationship_type',
        'subject__first_name',
        'subject__last_name',
        'delegate__first_name',
        'delegate__last_name',
        'subject__email',
        'delegate__email',
        'subject__username',
        'delegate__username',
    ]

    raw_id_fields = ("subject", "delegate",)


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


class IDCardConfirmationAdmin(admin.ModelAdmin):
    list_display = ('mobile_phone_number', 'url', )
    search_fields = [
        'mobile_phone_number',
        'confirmation_uuid', ]
    empty_value_display = ''


admin.site.register(IDCardConfirmation, IDCardConfirmationAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'birth_date',
                    'sex', 'subject', 'picture_url', 'verifying_agent_email')
    search_fields = [
        'user__first_name',
        'user__last_name',
        'birth_date',
        'sex', 'verifying_agent_email']
    raw_id_fields = ("user", )
    empty_value_display = ''


admin.site.register(UserProfile, UserProfileAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'point_of_contact',
                    'domain', 'subject', 'status',)
    search_fields = ['name', 'slug', 'org_identifiers__name', 'subject']
    raw_id_fields = ("point_of_contact", "members", "users", "addresses", "identifiers")
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
