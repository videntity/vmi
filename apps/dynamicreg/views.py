import json
import base64
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ratelimit.decorators import ratelimit
from django.conf import settings
from .management.commands.register_oauth2_client import register_app

# Copyright Videntity Systems, Inc


@csrf_exempt
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='POST', block=True)
def registration_endpoint(request):
    """OAuth2 Dynamic Client Registration Protocol"""
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if "Authorization" in request.headers:
            auth = request.headers['Authorization'].encode().split()
            if len(auth) == 2:
                if auth[0].decode('utf-8').lower() == "basic":
                    uname, passwd = base64.b64decode(
                        auth[1]).decode('utf-8').split(':')
                    user = authenticate(username=uname, password=passwd)
                    if user is not None and user.is_active:
                        if user.groups.filter(name='DynamicClientRegistrationProtocol').exists():
                            client_id = None
                            if 'client_id' in body.keys():
                                client_id = body['client_id']
                            client_secret = None
                            if 'client_secret' in body.keys():
                                client_secret = body['client_secret']

                            skip_authorization = False
                            if 'skip_authorization' in body.keys():
                                skip_authorization = body['skip_authorization']

                            client_type = 'confidential'
                            if 'client_type' in body.keys():
                                client_type = body['client_type']

                            redirect_uris = []
                            if 'redirect_uris' in body.keys():
                                redirect_uris = body['redirect_uris']

                            grant_type = 'authorization_code'
                            if 'grant_type' in body.keys():
                                grant_type = body['grant_type']
                            response = register_app(client_name=body['client_name'],
                                                    client_id=client_id,
                                                    client_secret=client_secret,
                                                    redirect_uris=redirect_uris,
                                                    client_type=client_type,
                                                    grant_type=grant_type,
                                                    skip_authorization=skip_authorization,
                                                    username=user.username)
                            return JsonResponse(response)
                        else:
                            return JsonResponse({"error": "Insufficient permissions." +
                                                          "You need to be in the DynamicClientRegistrationProtocol group."})
                    else:
                        return JsonResponse({"error": "Authentication Failed." +
                                                      "You have supplied invalid credentials or your account is inactive."})
    # Request methos is GET:
    message = "Welcome to Verify My Identity OAuth 2.0 Dynamic Client Registration Protocol." +\
              "POST here with proper credentials to register an application." +\
              "See https://github.com/videntity/vmi/blob/master/apps/dynamicreg/README.md"
    return JsonResponse({"message": message})
