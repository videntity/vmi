import time
from .settings import oidc_settings


def get_claims_provider():
    return oidc_settings.OIDC_CLAIM_PROVIDER


class BaseProvider(object):

    def __init__(self, user=None, token=None, request=None):
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


class DefaultProvider(BaseProvider):

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
