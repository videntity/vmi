# Copyright Videntity Systems, Inc.
from django.conf.urls import url
from .views import inperson_id_verify, two_to_one_downgrade


# Copyright Videntity Systems Inc.

urlpatterns = [
    url(r'^inperson-id-verify/(?P<subject>[^/]+)',
        inperson_id_verify, name='inperson_id_verify'),


    url(r'^administrative-downgrade/(?P<subject>[^/]+)',
        two_to_one_downgrade, name='ial_two_to_one_downgrade'),

]
