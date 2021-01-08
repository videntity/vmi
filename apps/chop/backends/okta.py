#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

from jwkest.jwt import JWT
from ...accounts.models import UpstreamIdentityProviderToUser
from ...ial.models import IdentityAssuranceLevelDocumentation
import logging
from django.conf import settings

logger = logging.getLogger('verifymyidentity_.%s' % __name__)

__author__ = "Alan Viars"


def get_upstream_sub(backend, user, response, *args, **kwargs):
    if backend.name == 'okta-openidconnect':
        # Save the id_token 'sub' to the UpstreamIdentityProviderToUser model.
        if 'id_token' in response.keys():
            id_token = response.get('id_token')
            id_token_payload = JWT().unpack(id_token).payload()
            if not UpstreamIdentityProviderToUser.objects.filter(user=user, upstream_idp_sub=id_token_payload['sub'],
                                                                 upstream_idp_vendor=backend.name).exists():

                uidp2u = UpstreamIdentityProviderToUser.objects.create(
                    user=user, upstream_idp_sub=id_token_payload['sub'],
                    upstream_idp_vendor=backend.name,
                    upstream_idp_iss=id_token_payload.get('iss', ''),
                    upstream_idp_aud=id_token_payload.get('aud', ''),
                    name="%s %s" % (user.first_name.title(), user.last_name.title()),
                    email=user.email)
                logger.debug("Upstread IdP %s was autogenerated. for %s %s" % (uidp2u))
        if settings.SOCIAL_AUTH_OKTA_OPENIDCONNECT_AUTO_IAL2:
            idd, created = IdentityAssuranceLevelDocumentation.objects.get_or_create(subject_user=user, evidence="IAL2-ON-FILE")
            idd.note = "Autogenerated from business rules."
            idd.save()
            logger.debug("IAL2 %s was autogenerated." % (idd))
