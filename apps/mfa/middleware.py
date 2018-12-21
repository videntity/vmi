from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from apps.mfa import (
    start_mfa,
    get_device,
    user_has_mfa,
)
from .exceptions import VerificationRequired


class DeviceVerificationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.mfa_device = SimpleLazyObject(lambda: get_device(request))


class AssertDeviceVerificationMiddleware(MiddlewareMixin):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(callback, 'mfa_exempt', False):
            return None

        if not request.user.is_authenticated:
            return None

        if not request.mfa_device and user_has_mfa(request.user):
            return start_mfa(request)
        return None
