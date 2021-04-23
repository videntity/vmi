from django.conf.urls import url
from .views import display_qr, display_json, display_jws, display_user_index, display_all_shc


__author__ = "Alan Viars"


urlpatterns = [
    url(r'^display-qr$',  display_qr, name='healthcard_display_url_qr'),
    url(r'^display-json$',  display_json, name='display_healthcard_json'),
    url(r'^display-jws$',  display_jws, name='display_healthcard_jws'),

    url(r'^psi/(?P<sub>[^/]+)',  display_all_shc, name='shc_psi'),


    # Home page
    url(r'', display_user_index, name='shc_index'),


]
