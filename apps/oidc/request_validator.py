from datetime import timedelta
from oauth2_provider.oauth2_validators import (
    OAuth2Validator,
    GRANT_TYPE_MAPPING,
)
from oauth2_provider.models import AbstractApplication, get_grant_model
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.scopes import get_scopes_backend
from django.utils import timezone
from .claims import get_claims_provider
from .jwt import get_jwt_builder

GRANT_TYPE_MAPPING["openid"] = (AbstractApplication.GRANT_AUTHORIZATION_CODE, )

ClaimsProvider = get_claims_provider()
JWTBuilder = get_jwt_builder()
Grant = get_grant_model()


class RequestValidator(OAuth2Validator):

    def validate_response_type(self,
                               client_id,
                               response_type,
                               client,
                               request,
                               *args,
                               **kwargs):

        # https://github.com/jazzband/django-oauth-toolkit/blob/master/oauth2_provider/oauth2_validators.py#L404
        # TODO restrict response_types to a set defined in `settings`
        if "code" in response_type:
            return client.allows_grant_type(
                AbstractApplication.GRANT_AUTHORIZATION_CODE
            )
        elif "token" in response_type:
            return client.allows_grant_type(AbstractApplication.GRANT_IMPLICIT)
        else:
            return False

    def validate_user_match(self, id_token_hint, scopes, claims, request):
        if id_token_hint is None:
            return True
        return False

    def get_id_token(self, token, token_handler, request):
        cp = ClaimsProvider(user=request.user, token=token, request=request)
        claims = cp.get_claims()
        return JWTBuilder().encode(claims)

    def save_bearer_token(self, token, request, *args, **kwargs):
        # Should also check that response_type was only "id_token"
        if request.response_type == "id_token":
            return
        super().save_bearer_token(token, request, args, kwargs)

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        try:
            grant = Grant.objects.get(code=code, application=client)
            if not grant.is_expired():
                request.scopes = grant.scope.split(" ")
                request.user = grant.user
                request.nonce = grant.nonce
                return True
            return False

        except Grant.DoesNotExist:
            return False

    def save_authorization_code(self,
                                client_id,
                                code,
                                request,
                                *args,
                                **kwargs):

        expires = timezone.now() + timedelta(
            seconds=oauth2_settings.AUTHORIZATION_CODE_EXPIRE_SECONDS)
        g = Grant(
            application=request.client,
            user=request.user,
            code=code["code"],
            expires=expires,
            redirect_uri=request.redirect_uri,
            scope=" ".join(request.scopes),
            nonce=getattr(request, 'nonce', None)
        )
        g.save()

    def validate_scopes(self,
                        client_id,
                        scopes, client,
                        request,
                        *args,
                        **kwargs):

        available_scopes = get_scopes_backend().get_available_scopes(
            application=client,
            request=request)

        request.scopes = list(set(available_scopes) & set(scopes))
        # https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
        # unexpected scopes should be ignored
        return True
