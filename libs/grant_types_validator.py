from oauth2_provider.oauth2_validators import OAuth2Validator as ParentValidator
from django.conf import settings


class SettingsFlowValidatorMixin(object):
    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        """
        Validate grant_type is whitelisted in django settings
        """
        try:
            assert(grant_type in settings.OAUTH2_PROVIDER_ALLOWED_GRANT_TYPES)
        except AssertionError:
            return False
        return super().validate_grant_type(client_id, grant_type, client, request, *args, **kwargs)

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        try:
            assert(response_type in settings.OAUTH2_PROVIDER_ALLOWED_RESPONSE_TYPES)
        except AssertionError:
            return False
        return super().validate_response_type(client_id, response_type, client, request, *args, **kwargs)


class OAuth2Validator(SettingsFlowValidatorMixin, ParentValidator):
    pass
