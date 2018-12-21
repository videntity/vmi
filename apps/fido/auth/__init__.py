from ..models import AttestedCredentialData


def has_fido_device(user):
    return AttestedCredentialData.objects.filter(user=user).exists()
