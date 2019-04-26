# Copyright Videntity Systems, Inc.
from django.conf.urls import url
from django.urls import path
from .views import (account_settings,
                    mylogout, create_account,
                    forgot_password, activation_verify,
                    reset_password, delete_account)
from .staff_views import (create_org_account,
                          approve_org_affiliation,
                          deny_org_affiliation,
                          request_org_affiliation)
from .sms_mfa_views import mfa_login, mfa_code_confirm
from .mfa_views import (
    DisableSMSMFAView,
    EnableSMSMFAView,
    ManageView,
)
from .phone_views import mobile_phone, verify_mobile_phone_number
from .identifier_views import (display_individual_identifiers, add_new_individual_identifier,
                               delete_individual_identifier, edit_individual_identifier)

from .address_views import (display_addresses, add_new_address,
                            delete_address, edit_address)

from .profile_picture_views import upload_profile_picture

# Copyright Videntity Systems Inc.

urlpatterns = [
    url(r'^logout', mylogout, name='mylogout'),
    url(r'^mobile-phone', mobile_phone, name='mobile_phone'),
    url(r'^verify-mobile-phone-number/(?P<uid>[^/]+)/', verify_mobile_phone_number,
        name='verify_mobile_phone_number'),
    url(r'^settings', account_settings, name='account_settings'),
    url(r'^delete', delete_account, name='delete_account'),
    url(r'^login', mfa_login, name='mfa_login'),
    url(r'^upload-profile-picture/(?P<subject>[^/]+)', upload_profile_picture, name='upload_profile_picture_subject'),
    url(r'^upload-profile-picture', upload_profile_picture, name='upload_profile_picture'),
    url(r'^create-account/(?P<service_title>[^/]+)/', create_account,
        name='create_account_enduser_affilate'),
    url(r'^create-account', create_account, name='create_account_enduser'),
    url(r'^activation-verify/(?P<activation_key>[^/]+)/$',
        activation_verify, name='activation_verify'),
    url(r'^forgot-password', forgot_password, name='forgot_password'),
    url(r'^reset-password', reset_password, name='reset_password'),
    # Confirm MFA ------------------------
    url(r'mfa/confirm/(?P<uid>[^/]+)/',
        mfa_code_confirm, name='mfa_code_confirm'),

    # Organization related
    url(r'^create-org-account/(?P<organization_slug>[^/]+)/',
        create_org_account, name='create_org_account'),

    url(r'^approve-org-affiliation/(?P<organization_slug>[^/]+)/(?P<username>[^/]+)/',
        approve_org_affiliation, name='approve_org_affiliation'),

    url(r'^deny-org-affiliation/(?P<organization_slug>[^/]+)/(?P<username>[^/]+)/',
        deny_org_affiliation, name='deny_org_affiliation'),

    url(r'^request-org-affiliation/(?P<organization_slug>[^/]+)',
        request_org_affiliation, name='request_org_afiliation'),

    url("^individual-identifiers/(?P<subject>[^/]+)",
        display_individual_identifiers, name='display_individual_identifiers_subject'),

    url(r"^individual-identifiers/", display_individual_identifiers,
        name='display_individual_identifiers'),


    url("^add-new-individual-identifier/(?P<subject>[^/]+)$",
        add_new_individual_identifier, name='add_new_individual_identifier'),

    url("^delete-individual-identifier/(?P<id>[^/]+)$",
        delete_individual_identifier, name='delete_individual_identifier'),

    url("^edit-individual-identifier/(?P<id>[^/]+)$",
        edit_individual_identifier, name='edit_individual_identifier'),


    url("^addresses/(?P<subject>[^/]+)$",
        display_addresses, name='display_addresses_subject'),
    url(r"^addresses/", display_addresses, name='display_addresses'),


    url("^add-new-address/(?P<subject>[^/]+)$",
        add_new_address, name='add_new_address'),

    url("^delete-address/(?P<id>[^/]+)$",
        delete_address, name='delete_address'),

    url("^edit-address/(?P<id>[^/]+)$", edit_address, name='edit_address'),


    path("mfa", ManageView.as_view(), name='mfa-management'),
    path("sms/enable", EnableSMSMFAView.as_view(), name='sms-mfa-enable'),
    path("sms/disable", DisableSMSMFAView.as_view(), name='sms-mfa-disable'),
]
