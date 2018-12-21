from . import has_fido_device
from ..views.verify import VerifyView
from ..models import AttestedCredentialData


class FIDO2Backend:
    def get_device_model(self):
        return AttestedCredentialData

    def is_enabled(self, user):
        return has_fido_device(user)

    def get_device(self, device_id):
        return AttestedCredentialData.objects.get(pk=device_id)

    def start_verification(self, request):
        if has_fido_device(request.user):
            return VerifyView.as_view()(request).render()
        return None
