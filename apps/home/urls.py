from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView
from .views import authenticated_home


__author__ = "Alan Viars"

admin.autodiscover()

urlpatterns = [
    url(r'',
        authenticated_home,
        name='auth_home'),

]
