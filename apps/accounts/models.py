import pytz
import random
import uuid

from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
import boto3
from .emails import (send_password_reset_url_via_email,
                     send_activation_key_via_email,
                     mfa_via_email)
from luhn import generate
# Copyright Videntity Systems Inc.

__author__ = "Alan Viars"


# Todo make a setting
LUHN_PREFIX = "85721"


INDIVIDUAL_ID_TYPE_CHOICES = (
    ('PATIENT_ID_FHIR', 'Patient ID FHIR'),
    ('MPI', 'Master Patient Index (Not FHIR Patient id)'),
    ('SSN', 'Social Security Number'),
    ('MEDICIAD_ID', 'Medicaid ID Number'),
    ('MEDICICARE_HICN', 'Medicare HICN (Legacy)'),
    ('MEDICIARE_ID', 'Medicare ID Number'),
    ('INDURANCE_ID', 'Insurance ID Number'),
    ('IHE_ID', 'Health Information Exchange ID'),
    ('UHI', 'Universal Health Identifier'),
                              )

ORGANIZATION_ID_TYPE_CHOICES = (
    ('FEIN', 'Federal Employer ID Number (Tax ID)'),
    ('NPI', 'National Provider Identifier'),
    ('OEID', 'Other Entity Identifier'),
    ('PECOS', 'PECOS Medicare ID')
)

SEX_CHOICES = (('M', 'Male'), ('F', 'Female'), ('U', 'Unknown'))

GENDER_CHOICES = (('M', 'Male'),
                  ('F', 'Female'),
                  ('TMF', 'Transgender Male to Female'),
                  ('TFM', 'Transgender Female to Male'),
                  ('U', 'Unknown'))


@python_2_unicode_compatible
class IndividualIdentifier(models.Model):
    name = models.CharField(max_length=255, default='')
    slug = models.SlugField(max_length=32, blank=True, default='')
    value = models.CharField(max_length=1024, default='')
    issuer = models.CharField(max_length=255, blank=True, default='')
    state = models.CharField(max_length=2, blank=True, default='')
    uri = models.CharField(max_length=1024, blank=True, default='')
    id_type = models.CharField(max_length=16, blank=True, default='',
                               choices=INDIVIDUAL_ID_TYPE_CHOICES)

    def __str__(self):
        return self.value


@python_2_unicode_compatible
class OrganizationIdentifier(models.Model):
    name = models.CharField(max_length=255, default='')
    slug = models.SlugField(max_length=32, blank=True, default='')
    value = models.CharField(max_length=1024, default='')
    issuer = models.CharField(max_length=255, blank=True, default='')
    state = models.CharField(max_length=2, blank=True, default='')
    uri = models.CharField(max_length=1024, blank=True, default='')
    id_type = models.CharField(max_length=16, blank=True, default='',
                               choices=ORGANIZATION_ID_TYPE_CHOICES)

    def __str__(self):
        return self.value


@python_2_unicode_compatible
class Address(models.Model):
    street_1 = models.CharField(max_length=255, blank=True, default='')
    street_2 = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=255, blank=True, default='')
    state = models.CharField(max_length=2, blank=True, default='')
    zipcode = models.CharField(max_length=10, blank=True, default='')
    identifiers = models.ManyToManyField(OrganizationIdentifier, blank=True)
    subject = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        address = '%s %s %s %s %s' % (self.street_1, self.street_2,
                                      self.city, self.state, self.zipcode)
        return address


@python_2_unicode_compatible
class Organization(models.Model):
    subject = models.CharField(max_length=255, default='', blank=True)
    title = models.CharField(max_length=255, default='', blank=True)
    slug = models.SlugField(max_length=32, blank=True, default='')
    addresses = models.ManyToManyField(Address, blank=True)
    identifiers = models.ManyToManyField(OrganizationIdentifier, blank=True)

    def __str__(self):
        return self.subject

    def name(self):
        if self.organization_name:
            return self.organization_name
        else:
            name = '%s %s' % (self.user.first_name, self.user.last_name)
        return name


@python_2_unicode_compatible
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(
        max_length=255,
        default='',
        blank=True,
        help_text='Nickname, alias, or other names used.')
    email_verified = models.BooleanField(default=False, blank=True)
    phone_verified = models.BooleanField(default=False, blank=True)
    organizations = models.ManyToManyField(Organization, blank=True)
    addresses = models.ManyToManyField(Address, blank=True)
    identifiers = models.ManyToManyField(IndividualIdentifier, blank=True)
    mobile_phone_number = models.CharField(
        max_length=10, blank=True, default="",
        help_text=_('US numbers only.'),
    )
    uhi = models.CharField(
        max_length=15, blank=True, default="",
        help_text=_('Universal Health ID'),
        # editable=False,
    )
    subject = models.CharField(
        max_length=40,
        default='',
        blank=True,
        editable=False,
        help_text='Auto-generated subject identifier.')

    sex = models.CharField(choices=SEX_CHOICES,
                           max_length=1, default="U",
                           help_text=_('Sex'),
                           )
    gender = models.CharField(choices=GENDER_CHOICES,
                              max_length=3, default="U",
                              help_text=_('Gender / Gender Identity'),
                              )
    birth_date = models.DateField(blank=True, null=True,
                                  )

    def __str__(self):
        display = '%s %s (%s)' % (self.user.first_name,
                                  self.user.last_name,
                                  self.user.username)
        return display

    def given_name(self):
        return self.user.first_name

    def family_name(self):
        return self.user.family_name

    def phone(self):
        return self.mobile_phone_number

    def preferred_username(self):
        return self.user.username

    def name(self):
        name = '%s %s' % (self.user.first_name, self.user.last_name)
        return name

    def save(self, commit=True, **kwargs):
        if not self.uhi:
            if not self.mobile_phone_number:
                self.uhi = random_number(14)
            else:
                self.uhi = "%s%s" % (self.mobile_phone_number,
                                     random_number(4))
            # print("Add Luhn checkdigit")

            # Prefix Luhn so we can later identify as UHI
            prefixed_number = "%s%s" % (LUHN_PREFIX, self.uhi)
            # print("Prefixed", prefixed_number)
            result = generate(prefixed_number)
            # print("Result:", result)
            self.uhi = "%s%s" % (self.uhi, result)

        if not self.subject:
            self.subject = random_number(25)
            self.subject = "%s%s" % (self.subject, generate(self.subject))

        super(UserProfile, self).save(**kwargs)


MFA_CHOICES = (
    ('', 'None'),
    ('EMAIL', "Email"),
    ('FIDO', "FIDO U2F"),
    ('SMS', "Text Message (SMS)"),
)


@python_2_unicode_compatible
class MFACode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uid = models.CharField(blank=True,
                           default=uuid.uuid4,
                           max_length=36, editable=False)
    tries_counter = models.IntegerField(default=0, editable=False)
    code = models.CharField(blank=True, max_length=4, editable=False)
    mode = models.CharField(max_length=5, default="",
                            choices=MFA_CHOICES)
    valid = models.BooleanField(default=True)
    expires = models.DateTimeField(blank=True)
    added = models.DateField(auto_now_add=True)

    def __str__(self):
        name = 'To %s via %s' % (self.user,
                                 self.mode)
        return name

    def endpoint(self):
        e = ""
        up = UserProfile.objects.get(user=self.user)
        if self.mode == "SMS" and up.mobile_phone_number:
            e = up.mobile_phone_number
        if self.mode == "EMAIL" and self.user.email:
            e = self.user.email
        return e

    def save(self, **kwargs):
        if not self.id:
            now = pytz.utc.localize(datetime.utcnow())
            expires = now + timedelta(days=1)
            self.expires = expires
            self.code = str(random.randint(1000, 9999))
            up = UserProfile.objects.get(user=self.user)
            if self.mode == "SMS" and \
               up.mobile_phone_number and \
               settings.SEND_SMS:
                # Send SMS to up.mobile_phone_number
                sns = boto3.client(
                    'sns',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name='us-east-1')
                number = "+1%s" % (up.mobile_phone_number)
                sns.publish(
                    PhoneNumber=number,
                    Message="Your code is : %s" % (self.code),
                    MessageAttributes={
                        'AWS.SNS.SMS.SenderID': {
                            'DataType': 'String',
                            'StringValue': 'MySenderID'
                        }
                    }
                )
            elif self.mode == "SMS" and not up.mobile_phone_number:
                print("Cannot send SMS. No phone number on file.")
            elif self.mode == "EMAIL" and self.user.email:
                # "Send SMS to self.user.email
                mfa_via_email(self.user, self.code)
            elif self.mode == "EMAIL" and not self.user.email:
                print("Cannot send email. No email_on_file.")
            else:
                """No MFA code sent"""
                pass
        super(MFACode, self).save(**kwargs)


@python_2_unicode_compatible
class ActivationKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(default=uuid.uuid4, max_length=40)
    expires = models.DateTimeField(blank=True)

    def __str__(self):
        return 'Key for %s expires at %s' % (self.user.username,
                                             self.expires)

    def save(self, **kwargs):
        self.signup_key = str(uuid.uuid4())

        now = pytz.utc.localize(datetime.utcnow())
        expires = now + timedelta(days=settings.SIGNUP_TIMEOUT_DAYS)
        self.expires = expires

        # send an email with reset url
        send_activation_key_via_email(self.user, self.key)
        super(ActivationKey, self).save(**kwargs)


@python_2_unicode_compatible
class ValidPasswordResetKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_password_key = models.CharField(max_length=50, blank=True)
    # switch from datetime.now to timezone.now
    expires = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s for user %s expires at %s' % (self.reset_password_key,
                                                 self.user.username,
                                                 self.expires)

    def save(self, **kwargs):
        self.reset_password_key = str(uuid.uuid4())
        # use timezone.now() instead of datetime.now()
        now = timezone.now()
        expires = now + timedelta(minutes=1440)
        self.expires = expires

        # send an email with reset url
        send_password_reset_url_via_email(self.user, self.reset_password_key)
        super(ValidPasswordResetKey, self).save(**kwargs)


def random_key_id(y=20):
    return ''.join(random.choice('ABCDEFGHIJKLM'
                                 'NOPQRSTUVWXYZ') for x in range(y))


def random_secret(y=40):
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz'
                                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                 '0123456789') for x in range(y))


def random_code(y=10):
    return ''.join(random.choice('ABCDEFGHIJKLM'
                                 'NOPQRSTUVWXYZ'
                                 '234679') for x in range(y))


def random_number(y=10):
    return ''.join(random.choice('123456789') for x in range(y))


def create_activation_key(user):
    # Create an new activation key and send the email.
    key = ActivationKey.objects.create(user=user)
    return key
