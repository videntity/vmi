# Copyright Videntity Systems, Inc.
from django.conf.urls import url
from .views import delete_id_verify, verify_id_with_card, enter_id_card_info


# Copyright Videntity Systems Inc.

urlpatterns = [


    url(r'^verify-id-with-card/(?P<subject>[^/]+)',
        verify_id_with_card, name='verify_id_with_card'),

    url(r'^enter-id-card-info/(?P<id>[^/]+)',
        enter_id_card_info, name='enter_id_card_info'),

    url(r'^delete-id-verify/(?P<id>[^/]+)',
        delete_id_verify, name='delete_id_verify'),



]
