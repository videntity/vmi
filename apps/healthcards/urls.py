from django.conf.urls import url
from .views import display_user_index, shc_psi


__author__ = "Alan Viars"


urlpatterns = [

    url(r'^psi/(?P<sub>[^/]+)',  shc_psi, name='shc_psi'),


    # Home page
    url(r'', display_user_index, name='shc_index'),


]
