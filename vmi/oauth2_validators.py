from apps.oidc.request_validator import RequestValidator as OIDCRequestValidator
from libs.grant_types_validator import SettingsFlowValidatorMixin


class RequestValidator(SettingsFlowValidatorMixin,
                       OIDCRequestValidator):
    pass
