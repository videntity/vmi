from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AuthorizationConfig(AppConfig):
    name = 'apps.mfa.backends.sms'
    verbose_name = _('mfa sms')

    def ready(self):
        from . import signals  # noqa
