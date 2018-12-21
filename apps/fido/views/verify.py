from urllib.parse import urlparse
from base64 import b64encode, b64decode
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
    renderer_classes,
    parser_classes,
)
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import authentication
from rest_framework import renderers
from rest_framework import parsers
from fido2.client import ClientData
from fido2.server import Fido2Server, RelyingParty
from fido2.ctap2 import AttestationObject, AuthenticatorData
from fido2 import cbor

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from apps.mfa.decorators import mfa_exempt
from apps.mfa import verify
from ..models import AttestedCredentialData
from .register import CBORParser, CBORRenderer


class VerifyView(LoginRequiredMixin, TemplateView):
    template_name = "authenticate.html"


@mfa_exempt
@api_view(['POST'])
@authentication_classes([authentication.SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
@renderer_classes((CBORRenderer,))
def begin(request):
    rp_host = urlparse(request.build_absolute_uri()).hostname
    rp = RelyingParty(rp_host, 'Demo server')
    server = Fido2Server(rp)

    existing_credentials = AttestedCredentialData.objects.filter(user=request.user).all()
    auth_data, state = server.authenticate_begin(existing_credentials)
    request.session['state'] = {
        'challenge': b64encode(state['challenge']).decode('utf-8'),
        'user_verification': state['user_verification'].value,
    }
    return Response(auth_data, content_type="application/cbor")

@mfa_exempt
@api_view(['POST'])
@authentication_classes([authentication.SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
@renderer_classes((CBORRenderer,))
@parser_classes((CBORParser,))
def complete(request):
    cred = authenticate(request)
    # Store like request.user
    verify(request, cred)
    return Response("OK")

def authenticate(request):
    rp_host = urlparse(request.build_absolute_uri()).hostname
    rp = RelyingParty(rp_host, 'Demo server')
    server = Fido2Server(rp)

    data = request.data[0]
    credential_id = data['credentialId']
    credentials = AttestedCredentialData.objects.filter(
        user=request.user,
    ).all()
    client_data = ClientData(data['clientDataJSON'])
    auth_data = AuthenticatorData(data['authenticatorData'])
    signature = data['signature']

    stored_state = request.session['state']
    state = {
        'challenge': b64decode(stored_state['challenge'].encode()),
        'user_verification': stored_state['user_verification'],
    }

    cred = server.authenticate_complete(
        state,
        credentials,
        credential_id,
        client_data,
        auth_data,
        signature
    )
    return cred
