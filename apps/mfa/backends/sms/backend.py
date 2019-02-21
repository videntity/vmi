from django.utils import timezone
from .views import CodeView
from .models import (
    SMSDevice,
    SMSCode,
)


def has_sms_device(user):
    return SMSDevice.objects.filter(user=user).exists()


class SMSBackend:
    def get_device_model(self):
        return SMSDevice

    def is_enabled(self, user):
        return SMSDevice.objects.filter(user=user).exists()

    def get_device(self, device_id):
        return SMSDevice.objects.get(pk=device_id)

    def start_verification(self, request):
        if SMSDevice.objects.filter(user=request.user).exists():
            # Generate code
            # save code
            code, _ = SMSCode.objects.filter(
                expires__gt=timezone.now()
            ).get_or_create(
                device=SMSDevice.objects.get(user=request.user))
            response = CodeView.as_view()(request)
            if hasattr(response, 'render'):
                return response.render()
            return response
        return None
