# Copyright Videntity Systems, Inc.
from django.conf.urls import url
from django.urls import path
from .views import (account_settings,
                    mylogout, create_account,
                    forgot_password, activation_verify,
                    reset_password, delete_account, password_reset_email_verified)
from .member_views import create_member_account, find_org_to_create_member_account
from .staff_views import (create_org_account,
                          find_org_to_create_account,
                          approve_org_affiliation,
                          deny_org_affiliation,
                          request_org_affiliation)
from .sms_mfa_views import mfa_login
from .mfa_views import (
    DisableSMSMFAView,
    EnableSMSMFAView,
    ManageView,
)
from .organization_views import display_organization, remove_agent_from_organization
from .phone_views import mobile_phone, verify_mobile_phone_number
from .identifier_views import (display_individual_identifiers, add_new_individual_identifier,
                               delete_individual_identifier, edit_individual_identifier)
from .password_recovery_passphrase_views import (password_recovery_passphrase_home,
                                                 generate_password_recovery_passphrase,
                                                 reset_password_with_recovery_passphrase,
                                                 reset_password_after_passphrase_verified)
from .address_views import (display_addresses, add_new_address,
                            delete_address, edit_address)

from .profile_picture_views import upload_profile_picture
from .change_account_views import activate_subject, deactivate_subject


# Copyright Videntity Systems Inc.

__author__ = "Alan Viars"

urlpatterns = [
    url(r'^logout', mylogout, name='mylogout'),
    url(r'^login/(?P<slug>[^/]+)?', mfa_login, name='mfa_login'),
    url(r'^password-recovery-passphrase/$', password_recovery_passphrase_home,
        name='password_recovery_passphrase_home'),
    url(r'^password-recovery-passphrase/generate', generate_password_recovery_passphrase,
        name='generate_password_recovery_passphrase'),
    url(r'^password-recovery-passphrase/reset-password$', reset_password_with_recovery_passphrase,
        name='reset_password_with_recovery_passphrase'),
    url(r'^password-recovery-passphrase/reset-after-passphrase-verified/(?P<username>[^/]+)/(?P<reset_password_key>[^/]+)/$',
        reset_password_after_passphrase_verified, name='reset_password_after_passphrase_verified'),
    url(r"^organization/(?P<organization_slug>[^/]+)/remove-agent/(?P<user_id>[^/]+)",
        remove_agent_from_organization,
        name='remove_agent_from_organization'),
    url(r"^organization/(?P<organization_slug>[^/]+)/", display_organization,
        name='display_organization'),
    url(r'^reset-forgotten-password(?P<reset_password_key>[^/]+)/$',
        password_reset_email_verified, name='password_reset_email_verified'),
    url(r'^mobile-phone', mobile_phone, name='mobile_phone'),
    url(r'^verify-mobile-phone-number/(?P<uid>[^/]+)/',
        verify_mobile_phone_number, name='verify_mobile_phone_number'),
    url(r'^settings/(?P<subject>[^/]+)',
        account_settings, name='account_settings_subject'),
    url(r'^settings$', account_settings, name='account_settings'),
    url(r'^delete$', delete_account, name='delete_account'),
    url(r'^upload-profile-picture/(?P<subject>[^/]+)',
        upload_profile_picture, name='upload_profile_picture_subject'),
    url(r'^upload-profile-picture', upload_profile_picture,
        name='upload_profile_picture'),
    url(r'^create-account/(?P<service_title>[^/]+)/', create_account,
        name='create_account_enduser_affiliate'),
    url(r'^create-account', create_account, name='create_account_enduser'),



    url(r'^activation-verify/(?P<activation_key>[^/]+)/$',
        activation_verify, name='activation_verify'),
    url(r'^forgot-password', forgot_password, name='forgot_password'),
    url(r'^reset-password', reset_password, name='reset_password'),

    # Member Creates accounts.
    url(r'^find-org-to-create-member-account', find_org_to_create_member_account,
        name='find_org_to_create_member_account'),
    url(r'^create-member/(?P<organization_slug>[^/]+)/',
        create_member_account, name='create_member_account'),

    # Organization related
    url(r'^find-org-to-create-account', find_org_to_create_account,
        name='find_org_to_create_account'),

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

    # Activate/Deactivate
    url("^activate/(?P<subject>[^/]+)$",
        activate_subject, name='activate_subject'),

    # Activate/Deactivate
    url("^deactivate/(?P<subject>[^/]+)$",
        deactivate_subject, name='deactivate_subject'),


    path("mfa", ManageView.as_view(), name='mfa-management'),
    path("sms/enable", EnableSMSMFAView.as_view(), name='sms-mfa-enable'),
    path("sms/disable", DisableSMSMFAView.as_view(), name='sms-mfa-disable'),
]
