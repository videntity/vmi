# Copyright Videntity Systems, Inc.
from django.conf.urls import url
from .views import jwks_json

# Copyright Videntity Systems Inc.

urlpatterns = [

    url(r'^jwks.json',
        jwks_json, name='smart_health_card_jwks_json'),
]
