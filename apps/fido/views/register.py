from base64 import b64encode
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

from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_exempt


class RegisterView(TemplateView):
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
        return cbor.loads(stream)

@api_view(['POST'])
@authentication_classes([authentication.SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
@renderer_classes((CBORRenderer,))
def begin(request):
    rp = RelyingParty(request.get_host(), 'Demo server')
    server = Fido2Server(rp)

    registration_data, state = server.register_begin({
        'id': request.user.username.encode(),
        'name': request.user.username,
        'displayName': request.user.username,
    }, [], resident_key=True)
    request.session['state'] = {
        'challenge': b64encode(state['challenge']).decode('utf-8'),
        'user_verification': state['user_verification'].value,
    }
    return Response(registration_data, content_type="application/cbor")

@api_view(['POST'])
@authentication_classes([authentication.SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
@renderer_classes((CBORRenderer,))
@parser_classes((CBORParser,))
def complete(request):
    irp = RelyingParty(request.get_host(), 'Demo server')
    server = Fido2Server(rp)

    data = cbor.loads(request.data)[0]
    client_data = ClientData(data['clientDataJSON'])
    att_obj = AttestationObject(data['attestationObject'])

    auth_data = server.register_complete(
        request.session['state'],
        client_data,
        att_obj
    )

    raise Exception(auth_data)
    # Credential.objects.create(auth_data.credential_data)
    return Response({'status': 'OK'})
