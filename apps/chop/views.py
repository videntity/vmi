import logging
from collections import OrderedDict
import base64
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..accounts.models import PersonToPersonRelationship, UpstreamIdentityProviderToUser, UserProfile
from django.conf import settings
from ratelimit.decorators import ratelimit
from django.shortcuts import get_object_or_404, get_list_or_404
__author__ = "Alan Viars"

# Copyright Videntity Systems Inc.

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


@csrf_exempt
@ratelimit(key='user_or_ip', rate=settings.PERSON_TO_PERSON_API_RATELIMIT, method='GET', block=True)
def get_relationships_via_upstream_idp_sub(request, upstream_idp_sub=None):

    if upstream_idp_sub:
        # Do basic auth...
        if "Authorization" in request.headers:
            auth = request.headers['Authorization'].encode().split()
            if len(auth) == 2:
                if auth[0].decode('utf-8').lower() == "basic":
                    uname, passwd = base64.b64decode(
                        auth[1]).decode('utf-8').split(':')
                    user = authenticate(username=uname, password=passwd)
                    if user is not None and user.is_active:
                        if user.groups.filter(name='PersonToPersonAPI').exists():
                            upstream_idp = get_object_or_404(UpstreamIdentityProviderToUser, upstream_idp_sub=upstream_idp_sub)
                            response = OrderedDict()
                            response.update(upstream_idp.structured_response())
                            up, created = UserProfile.objects.get_or_create(user=user)
                            response['sub'] = up.sub
                            response['vot'] = up.vot_ial_only
                            response['person_to_person'] = []
                            p2p = get_list_or_404(PersonToPersonRelationship, delegate=upstream_idp.user)
                            for r in p2p:
                                response['person_to_person'].append(r.structured_response())
                            return JsonResponse(response)
                        else:
                            logger.warn("Insufficient permissions for API call for username %s" % (uname))
                            return JsonResponse({"error": "Insufficient permissions." +
                                                          "You need to be in the PersonToPersonAPI group."})
                    else:
                        logger.warn("Invalid login attempt with username %s" % (uname))
                        return JsonResponse({"error": "Authentication Failed. Invalid credentials or your account is inactive."})
        else:
            return JsonResponse({"error": "Authorization headers were not supplied."})
    else:
        message = "Welcome to the Verify My Identity person-tp-person API." +\
            "Include an upstream IdP's 'sub' as a path parameter. Your user must be in" +\
            "the PersonToPersonAPI group to call this API."
        return JsonResponse({"message": message})
