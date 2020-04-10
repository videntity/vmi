from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from .views import home, select_org_for_account_create

__author__ = "Alan Viars"

admin.autodiscover()

urlpatterns = [
    path(r'', home, name='auth_home'),

    # user_type is either "member" or "agent.
    url("^select-org-for-account-create/(?P<user_type>[^/]+)/$",
        select_org_for_account_create,
        name='select-org-for-account-create_w_usertype'),


    # Account creation defaults to member when no user_type is given.
    path('select-org-for-account-create/',
         select_org_for_account_create,
         name='select-org-for-account-create')
]
