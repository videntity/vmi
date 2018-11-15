# Copyright Videntity Systems, Inc.
from django.conf.urls import url
from .views import (account_settings,
                    mylogout, create_account,
                    forgot_password, activation_verify,
                    reset_password)
from .staff_views import (create_org_account,
                          approve_org_affiliation,
                          deny_org_affiliation,
                          request_org_affiliation)
from .sms_mfa_views import mfa_login, mfa_code_confirm

# Copyright Videntity Systems Inc.

urlpatterns = [
    url(r'^logout', mylogout, name='mylogout'),
    url(r'^settings', account_settings, name='account_settings'),
    url(r'^login', mfa_login, name='mfa_login'),
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

]
