import json
import base64
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ratelimit.decorators import ratelimit
from django.conf import settings
from .management.commands.register_oauth2_client import register_app


@csrf_exempt
@ratelimit(key='ip', rate=settings.LOGIN_RATELIMIT, method='POST', block=True)
def registration_endpoint(request):
    """OAuth2 Dynamic Client Registration Protocol"""
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
                        response = register_app(body['client_name'],
                                                body['client_id'],
                                                body['redirect_uris'])
                        return JsonResponse(response)
                    else:
                        return JsonResponse({"error": "Not Authorized."})
                else:
                    return JsonResponse({"error": "Not Authorized -inactive"})

    return JsonResponse({"message": """This is the OAuth 2.0 Dynamic Client Registration Protocol endpoint.
                        POST here with proper credentials to register an application."""})
