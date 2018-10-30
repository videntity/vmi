from django.contrib import admin
from .models import (UserProfile, Organization,
                     Address, OrganizationIdentifier,
                     IndividualIdentifier)

# Copyright Videntity Systems Inc.

__author__ = "Alan Viars"


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'birth_date', 'mobile_phone_number')
    search_fields = [
        'user__first_name',
        'user__last_name',
        'birth_date',
        'sex',
        'org_identifiers__name',
        'ind_identifiers__name',
        'addresses.zipcode']
    raw_id_fields = ("user", "addresses", "organizations", "org_identifiers",
                     "ind_identifiers")


admin.site.register(UserProfile, UserProfileAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ['name', 'slug', 'org_identifiers__name']


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
