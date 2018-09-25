# Copyright Videntity Systems, Inc.
from django.conf.urls import url
from .views import (account_settings,
                    mylogout, create_account)

from .sms_mfa_views import mfa_login, mfa_code_confirm

# Copyright Videntity Systems Inc.

urlpatterns = [
    url(r'^logout', mylogout, name='mylogout'),
    url(r'^settings', account_settings, name='account_settings'),
     url(r'^mfa-login', mfa_login, name='mfa_login'),
      url(r'^create-account', create_account, name='create_account_enduser'),
    

    # Confirm MFA ------------------------
    url(r'mfa/confirm/(?P<uid>[^/]+)/',
        mfa_code_confirm, name='mfa_code_confirm'),

]
