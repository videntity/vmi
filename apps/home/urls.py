from django.conf.urls import url
from django.contrib import admin
from .views import authenticated_home, user_search


__author__ = "Alan Viars"

admin.autodiscover()

urlpatterns = [
    url(r'',
        authenticated_home,
        name='auth_home'),

    url(r'^search',
        user_search,
        name='user_search'),


]
