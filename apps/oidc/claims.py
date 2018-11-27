import time
from .settings import oidc_settings


def get_claims_provider():
    return oidc_settings.OIDC_BASE_CLAIM_PROVIDER_CLASS


def get_claim_providers():
    return oidc_settings.OIDC_CLAIM_PROVIDERS


class ClaimProvider(object):
    def __init__(self, user=None, token=None, request=None, **kwargs):
        self.user = user
        self.token = token
        self.request = request

    @classmethod
    def get_supported_claims(cls):
        providers = get_claim_providers()
        claims = []
        for p in providers:
            claims += p.get_supported_claims()
        return claims

    def get_claims(self):
        providers = get_claim_providers()
        claims = {}
        for p in providers:
            claims = {
                **claims,
                **p(user=self.user,
                    token=self.token,
                    request=self.request).get_claims()
            }
        return claims


class BaseProvider(object):

    def __init__(self, user=None, token=None, request=None, **kwargs):
        self.user = user
        self.token = token
        self.request = request

    @classmethod
    def get_supported_claims(cls):
        claims = []
        for name in dir(cls):
            if name.startswith('claim_'):
                key = name.replace('claim_', "", 1)
                claims.append(key)
        return claims

    def get_claims(self):
        claims = {}
        for name in dir(self):
            if name.startswith('claim_'):
                method = getattr(self, name)
                val = method()
                if val is not None:
                    key = name.replace('claim_', "", 1)
                    claims[key] = val
        return claims


class UserClaimProvider(BaseProvider):

    def claim_email(self):
        return self.user.email

    def claim_iss(self):
        return oidc_settings.OIDC_ISSUER

    def claim_sub(self):
        return getattr(self.user, 'id', None)

    def claim_aud(self):
        client = getattr(self.request, 'client', None)
        return getattr(client, 'client_id', None)

    def claim_exp(self):
        return time.time() + 3600

    def claim_iat(self):
        return time.time()

    def claim_nonce(self):
        # TODO need to add nonce to auth form
        return getattr(self.request, 'nonce', None)

    def claim_auth_time(self):
        last_login = getattr(self.user, 'last_login', None)
        if last_login is not None:
            return last_login.timestamp()
        return None
