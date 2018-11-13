# Copyright Videntity Systems, Inc.
from django.conf.urls import url
from .views import (account_settings,
                    mylogout, create_account,
                    forgot_password, activation_verify,
                    reset_password)
from .staff_views import create_staff_account
from .sms_mfa_views import mfa_login, mfa_code_confirm

# Copyright Videntity Systems Inc.

urlpatterns = [
    url(r'^logout', mylogout, name='mylogout'),
    url(r'^settings', account_settings, name='account_settings'),
    url(r'^login', mfa_login, name='mfa_login'),
    url(r'^create-account/(?P<service_title>[^/]+)/', create_account,
        name='create_account_enduser_affilate'),
    url(r'^create-account', create_account, name='create_account_enduser'),
    url(r'^create-staff-account/(?P<organization_slug>[^/]+)/',
        create_staff_account, name='create_account_staff'),
    url(r'^activation-verify/(?P<activation_key>[^/]+)/$',
        activation_verify, name='activation_verify'),
    url(r'^forgot-password', forgot_password, name='forgot_password'),
    url(r'^reset-password', reset_password, name='reset_password'),
    # Confirm MFA ------------------------
    url(r'mfa/confirm/(?P<uid>[^/]+)/',
        mfa_code_confirm, name='mfa_code_confirm'),
]
