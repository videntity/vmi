# Copyright Videntity Systems, Inc.
from django.conf.urls import url
from .views import get_relationships_via_upstream_idp_sub

# Copyright Videntity Systems Inc.

__author__ = "Alan Viars"

urlpatterns = [
    # Get a user's relationship using an upstream IDentyity Provider's suibject identifier
    url(r'^get-relationships-via-upstream-idp-sub/(?P<upstream_idp_sub>[^/]+)?', get_relationships_via_upstream_idp_sub,
        name='get_relationships_via_sub'),

    url(r'^get-relationships-via-sub/(?P<vmi_sub>[^/]+)?', get_relationships_via_upstream_idp_sub,
        name='get_relationships_via_sub'),

    url(r'^get-relationships-via-username/(?P<username>[^/]+)?', get_relationships_via_upstream_idp_sub,
        name='get_relationships_via_sub'),

]
