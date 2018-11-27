import os
from django.conf import settings
from oauth2_provider.settings import OAuth2ProviderSettings

USER_SETTINGS = getattr(settings, "OIDC_PROVIDER", {})

DEFAULTS = {
    "OIDC_BASE_CLAIM_PROVIDER_CLASS": 'apps.oidc.claims.ClaimProvider',
    "OIDC_CLAIM_PROVIDERS": ['apps.oidc.claims.UserClaimProvider'],
    "OIDC_JWT_BUILDER": 'apps.oidc.jwt.DefaultBuilder',
    "OIDC_ISSUER": os.environ.get('OIDC_ISSUER', 'http://localhost'),
    "OIDC_KEY_STORAGE": 'apps.oidc.secrets.FileKeyStore',
}

IMPORT_STRINGS = (
    "OIDC_BASE_CLAIM_PROVIDER_CLASS",
    "OIDC_JWT_BUILDER",
    "OIDC_KEY_STORAGE",
    "OIDC_CLAIM_PROVIDERS",
)

oidc_settings = OAuth2ProviderSettings(
    user_settings=USER_SETTINGS,
    import_strings=IMPORT_STRINGS,
    defaults=DEFAULTS)
