# TODO Split these up
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import permissions
from django.urls import reverse
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

log = logging.getLogger(__name__)

Scopes = scopes.get_scopes_backend()
ClaimsProvider = get_claims_provider()


class Wellknown(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):

        return Response({
            "grant_types_supported": [
                "authorization_code",
                "implicit",
                "refresh_token",
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
                oidc_settings.OIDC_ISSUER +
                reverse("oauth2_provider:revoke-token"),
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

    def get_initial(self):
        initial_data = super().get_initial()
        initial_data["nonce"] = self.oauth2_data.get("nonce", None)
        return initial_data

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
