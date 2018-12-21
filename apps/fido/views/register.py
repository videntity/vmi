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
from fido2.ctap2 import AttestationObject
from fido2 import cbor

from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.mfa import verify
from ..models import AttestedCredentialData


class RegisterView(LoginRequiredMixin, TemplateView):
    template_name = "register.html"


class CBORRenderer(renderers.BaseRenderer):
    media_type = 'application/cbor'
    format = 'cbor'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return cbor.dumps(data)


class CBORParser(parsers.BaseParser):
    media_type = 'application/cbor'

    def parse(self, stream, media_type=None, parser_context=None):
        return cbor.loads(stream.read())


@api_view(['POST'])
@authentication_classes([authentication.SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
@renderer_classes((CBORRenderer,))
def begin(request):
    rp_host = urlparse(request.build_absolute_uri()).hostname
    rp = RelyingParty(rp_host, 'Demo server')
    server = Fido2Server(rp)

    existing_credentials = AttestedCredentialData.objects.filter(user=request.user).all()

    registration_data, state = server.register_begin({
        'id': request.user.username.encode(),
        'name': request.user.username,
        'displayName': request.user.username,
    }, existing_credentials)
    request.session['state'] = {
        'challenge': state['challenge'],
        'user_verification': state['user_verification'].value,
    }
    return Response(registration_data, content_type="application/cbor")


@api_view(['POST'])
@authentication_classes([authentication.SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
@renderer_classes((CBORRenderer,))
@parser_classes((CBORParser,))
def complete(request):
    rp_host = urlparse(request.build_absolute_uri()).hostname
    rp = RelyingParty(rp_host, 'Demo server')
    server = Fido2Server(rp)

    data = request.data[0]
    client_data = ClientData(data['clientDataJSON'])
    att_obj = AttestationObject(data['attestationObject'])

    state = request.session['state']

    auth_data = server.register_complete(
        state,
        client_data,
        att_obj
    )

    cred = AttestedCredentialData.objects.create(
        aaguid=auth_data.credential_data.aaguid,
        credential_id=auth_data.credential_data.credential_id,
        public_key=cbor.dump_dict(auth_data.credential_data.public_key),
        user=request.user,
    )

    verify(request, cred, backend='apps.fido.auth.backends.FIDO2Backend')
    return Response({'status': 'OK'})
