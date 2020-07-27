import random
from datetime import timedelta
from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model


def generate_code():
    chrs = getattr(settings, "SMS_CODE_CHARSET",
                   'abcdefghijklmnopqrstuvwxyz1234567890')
    length = getattr(settings, "SMS_CODE_LENGTH", 6)
    return ''.join(random.choices(chrs, k=length))


def exp_time():
    offset = timedelta(seconds=getattr(settings, "SMS_CODE_EXP", 60))
    return timezone.now() + offset


class SMSDevice(models.Model):
    # FROM
    # https://stackoverflow.com/questions/19130942/whats-the-best-way-to-store-phone-number-in-django-models
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )


class SMSCode(models.Model):
    device = models.ForeignKey(
        SMSDevice,
        on_delete=models.CASCADE,
    )
    code = models.CharField(
        db_index=True,
        max_length=255,
        default=generate_code,
        editable=False,
    )
    expires = models.DateTimeField(blank=True, default=exp_time)
    created_at = models.DateTimeField(auto_now_add=True)
