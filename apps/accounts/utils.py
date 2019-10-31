import pytz
from datetime import datetime
from .models import ActivationKey, UserProfile

# Copyright Videntity Systems Inc.


def validate_email_verify_key(activation_key):
    utc = pytz.UTC
    try:
        vc = ActivationKey.objects.get(key=activation_key)
        now = datetime.now().replace(tzinfo=utc)
        expires = vc.expires.replace(tzinfo=utc)

        if expires < now:
            vc.delete()
            # The key has expired
            return False
    except(ActivationKey.DoesNotExist):
        # The key does not exist
        return False
    # The key exists and has not expired.
    up = UserProfile.objects.get(user=vc.user)
    up.email_verified = True
    up.save()
    vc.delete()
    return True
