from django.conf.urls import url
from .views import authorize_link, callback, home
from django.views.generic import TemplateView

# Copyright Videntity Systems, Inc.

__author__ = "Alan Viars"

urlpatterns = [

    url(r'^callback$', callback, name='testclient-callback'),
    url(r'^authorize-link$', authorize_link, name='authorize_link'),
    url(r'^$', home, name='testclient_home'),
    url(r'^error$', TemplateView.as_view(template_name='error.html'),
        name='testclient_error_page'),
]
