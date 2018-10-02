import jwt
from .settings import oidc_settings
from .secrets import RSA256Keys


def get_jwt_builder():
    return oidc_settings.OIDC_JWT_BUILDER


class DefaultBuilder(object):
    @classmethod
    def get_jwks(cls):
        return RSA256Keys().get_public_jwk()

    def encode(self, claims):
        # TODO update lib: https://jwt.io/
        return jwt.encode(
            claims,
            RSA256Keys().get_private_key(),
            algorithm='RS256').decode("utf-8")

    def decode(self, token, *args, **kwargs):
        return jwt.decode(
            token,
            RSA256Keys().get_public_key(),
            algorithm='RS256',
            **kwargs)
