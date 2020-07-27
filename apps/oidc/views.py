# TODO Split these up
import logging
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import permissions
from django.urls import reverse
from oauthlib.oauth2.rfc6749.grant_types import OIDCNoPrompt
from oauth2_provider import scopes
from oauth2_provider.exceptions import OAuthToolkitError
from oauth2_provider.models import get_application_model
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.base import (
    AuthorizationView as OAuth2AuthorizationView
)
from .settings import oidc_settings
from .claims import get_claims_provider
from .jwt import get_jwt_builder
from .forms import NonceAllowForm
from .exceptions import AuthenticationRequired

log = logging.getLogger(__name__)

Scopes = scopes.get_scopes_backend()
ClaimsProvider = get_claims_provider()


class Wellknown(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):

        return Response({
            # TODO get this from oauth server config
            "grant_types_supported": [
                "authorization_code",
                "implicit",
                "refresh_token",
            ],
            # TODO get this from settings or other
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post",
            ],
            "issuer": oidc_settings.OIDC_ISSUER,
            "userinfo_endpoint":
                oidc_settings.OIDC_ISSUER + reverse("oidc:userinfo"),
            "authorization_endpoint":
                oidc_settings.OIDC_ISSUER +
                reverse("oauth2_provider:authorize"),
            "token_endpoint":
                oidc_settings.OIDC_ISSUER + reverse("oauth2_provider:token"),
            "revocation_endpoint":
                oidc_settings.OIDC_ISSUER + reverse("oauth2_provider:revoke-token"),
            "introspection_endpoint":
                oidc_settings.OIDC_ISSUER + reverse("oauth2_provider:introspect"),
            "registration_endpoint":
                oidc_settings.OIDC_ISSUER + reverse("registration_endpoint"),
            "response_types_supported":
                oauth2_settings.OAUTH2_SERVER_CLASS.get_all_response_types(),
            "scopes_supported": Scopes.get_all_scopes().keys(),
            "claims_supported": ClaimsProvider.get_supported_claims(),
            "jwks_uri": oidc_settings.OIDC_ISSUER + reverse("jwks_uri"),
        })


class JWKSURI(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        return Response({
            "keys": [get_jwt_builder().get_jwks()]})


ClaimsProvider = get_claims_provider()


class UserInfo(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        cp = ClaimsProvider(user=request.user, token=None, request=request)
        claims = cp.get_claims()
        return Response(claims)

    def post(self, request, format=None):
        cp = ClaimsProvider(user=request.user, token=None, request=request)
        claims = cp.get_claims()
        return Response(claims)


class AuthorizationView(OAuth2AuthorizationView):

    form_class = NonceAllowForm

    def handle_no_permission(self):
        if self.request.GET.get('prompt') == 'none':
            raise OIDCNoPrompt()
        return super().handle_no_permission()

    def get_initial(self):
        initial_data = super().get_initial()
        initial_data["nonce"] = self.oauth2_data.get("nonce", None)
        return initial_data

    def validate_authorization_request(self, request):
        self.validate_prompt(request)
        self.validate_max_age(request)
        return super().validate_authorization_request(request)

    def validate_prompt(self, request):
        prompt = request.GET.get('prompt', None)
        if prompt == 'login':
            q = request.GET.copy()
            q.pop('prompt')
            nxt = "%s?%s" % (request.path, q.urlencode())
            raise AuthenticationRequired(nxt)

        if getattr(request.user, 'is_authenticated', False):
            # override "prompt=none" out to allow process to proceed as normal
            if request.GET.get('prompt') == 'none':
                request.POST = request.POST.copy()
                request.POST['prompt'] = False

    def validate_max_age(self, request):
        max_age = request.GET.get('max_age', None)
        if max_age is not None:
            last_login = getattr(request.user, 'last_login', None)
            if last_login is not None:
                login_delta = datetime.datetime.now().timestamp() - last_login.timestamp()  # noqa
                if login_delta > float(max_age):
                    raise AuthenticationRequired(
                        request.get_full_path()
                    )

    def get(self, request, *args, **kwargs):
        kwargs['nonce'] = request.GET.get('nonce', None)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        client_id = form.cleaned_data["client_id"]
        application = get_application_model().objects.get(client_id=client_id)
        credentials = {
            "client_id": form.cleaned_data.get("client_id"),
            "redirect_uri": form.cleaned_data.get("redirect_uri"),
            "response_type": form.cleaned_data.get("response_type", None),
            "state": form.cleaned_data.get("state", None),
            "nonce": form.cleaned_data.get("nonce", None),
        }
        scopes = form.cleaned_data.get("scope")
        allow = form.cleaned_data.get("allow")

        try:
            uri, headers, body, status = self.create_authorization_response(
                request=self.request,
                scopes=scopes,
                credentials=credentials,
                allow=allow
            )
        except OAuthToolkitError as error:
            return self.error_response(error, application)

        self.success_url = uri
        log.debug("Success url for the request: {0}".format(self.success_url))
        return self.redirect(self.success_url, application)
