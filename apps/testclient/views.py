from django.shortcuts import render
from requests_oauthlib import OAuth2Session
from collections import OrderedDict
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from .utils import test_setup, get_client_secret
import logging
from oauthlib.oauth2.rfc6749.errors import MissingTokenError
from django.views.decorators.cache import never_cache
from jwkest.jwt import JWT

# Copyright Videntity Systems, Inc.

__author__ = "Alan Viars"

logger = logging.getLogger('verifymyidentity.%s' % __name__)


def jwt_payload(request):
    if 'jwt' not in request.GET:
        return JsonResponse({"error": "you just supply a jwt as a GET parmeter."})
    myjwt = request.GET.get("jwt")

    try:
        parsed_id_token = JWT().unpack(myjwt)
        parsed_id_token = parsed_id_token.payload()
    except Exception:
        parsed_id_token = {
            "error": "you just supply a valid jwt as a GET parmeter."}
    return JsonResponse(parsed_id_token)


def callback(request):

    response = OrderedDict()
    if 'error' in request.GET:
        return render(request, "access-denied.html", {"error": request.GET.get("error")})
    oas = OAuth2Session(request.session['client_id'],
                        redirect_uri=request.session['redirect_uri'])
    host = settings.HOSTNAME_URL
    if not(host.startswith("http://") or host.startswith("https://")):
        host = "https://%s" % (host)
    auth_uri = host + request.get_full_path()
    token_uri = host + reverse('oauth2_provider:token')
    try:
        token = oas.fetch_token(token_uri,
                                client_secret=get_client_secret(),
                                authorization_response=auth_uri)
    except MissingTokenError:
        logmsg = "Failed to get token from %s" % (request.session['token_uri'])
        logger.error(logmsg)
        return JsonResponse({'error': 'Failed to get token from',
                             'code': 'MissingTokenError',
                             'help': 'Try authorizing again.'}, status=500)
    request.session['token'] = token
    response['token_response'] = OrderedDict()

    for k, v in token.items():
        if k != "scope":
            response['token_response'][k] = v
        else:
            response['token_response'][k] = ' '.join(v)
    response['test_page'] = host + reverse('testclient_home')
    parsed_id_token = JWT().unpack(response['token_response']['id_token'])
    parsed_id_token = parsed_id_token.payload()
    response['id_token_payload'] = parsed_id_token
    return success(request, response)


@never_cache
def success(request, response):
    return render(request, "success.html", response)


def authorize_link(request):

    request.session.update(test_setup())
    oas = OAuth2Session(request.session['client_id'],
                        redirect_uri=request.session['redirect_uri'])
    authorization_url = oas.authorization_url(
        request.session['authorization_uri'])[0]
    return render(request, 'authorize-link.html', {"authorization_url": authorization_url})


def home(request):
    return render(request, 'testclient-home.html')
