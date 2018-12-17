import pytz
import random
import uuid
from django.template.defaultfilters import slugify
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
import boto3
from phonenumber_field.modelfields import PhoneNumberField
from .emails import (send_password_reset_url_via_email,
                     send_activation_key_via_email,
                     mfa_via_email,
                     send_new_org_account_approval_email)
from .subject_generator import generate_subject_id
from collections import OrderedDict
from ..ial.models import IdentityAssuranceLevelDocumentation

# Copyright Videntity Systems Inc.

__author__ = "Alan Viars"


SEX_CHOICES = (('M', 'Male'), ('F', 'Female'), ('U', 'Unknown'))

GENDER_CHOICES = (('M', 'Male'),
                  ('F', 'Female'),
                  ('TMF', 'Transgender Male to Female'),
                  ('TFM', 'Transgender Female to Male'),
                  ('U', 'Unknown'))


class IndividualIdentifier(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete='PROTECT', null=True)
    name = models.SlugField(max_length=250, blank=True,
                            default='', db_index=True)
    value = models.CharField(
        max_length=250,
        blank=True,
        default='', db_index=True)
    metadata = models.TextField(
        blank=True,
        default='',
        help_text="JSON Object")
    type = models.CharField(max_length=16, blank=True, default='')

    def __str__(self):
        return self.value

    @property
    def doc_oidc_format(self):
        od = OrderedDict()
        od['type'] = self.type
        od['num'] = self.value
        return od


class OrganizationIdentifier(models.Model):
    name = models.SlugField(max_length=250, default='',
                            blank=True, db_index=True)
    value = models.CharField(
        max_length=250,
        blank=True,
        default='', db_index=True)
    metadata = models.TextField(
        blank=True,
        default='',
        help_text="JSON Object")
    type = models.CharField(max_length=16, blank=True, default='', )

    def __str__(self):
        return self.value


class Address(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete='PROTECT', null=True)
    street_1 = models.CharField(max_length=250, blank=True, default='')
    street_2 = models.CharField(max_length=250, blank=True, default='')
    city = models.CharField(max_length=250, blank=True, default='')
    state = models.CharField(max_length=2, blank=True, default='')
    zipcode = models.CharField(max_length=10, blank=True, default='')
    country = models.CharField(max_length=2, blank=True, default='')
    org_identifiers = models.ManyToManyField(
        OrganizationIdentifier, blank=True)
    ind_identifiers = models.ManyToManyField(IndividualIdentifier, blank=True)
    subject = models.CharField(max_length=250, default='', blank=True)

    def __str__(self):
        address = '%s %s %s %s %s' % (self.street_1, self.street_2,
                                      self.city, self.state, self.zipcode)
        return address

    @property
    def locality(self):
        return self.city

    @property
    def region(self):
        return self.state

    @property
    def street_address(self):
        return '%s %s' % (self.street_1, self.street_2)

    @property
    def formatted_address(self):
        od = OrderedDict()
        od['formatted'] = '%s %s\n%s %s %s' % (
            self.street_1, self.street_2, self.city, self.state, self.zipcode)
        od['street_address'] = self.street_address
        od['locality'] = self.locality
        od['region'] = self.region
        od['postal_code'] = self.zipcode
        od['country'] = self.country
        return od


class Organization(models.Model):
    name = models.CharField(max_length=250, default='', blank=True)
    slug = models.SlugField(max_length=250, blank=True, default='',
                            db_index=True, unique=True)
    registration_code = models.CharField(max_length=100,
                                         default='',
                                         blank=True)
    domain = models.CharField(
        max_length=512,
        blank=True,
        default='',
        help_text="If populated, restrict email registration to this address.")
    website = models.CharField(max_length=512, blank=True, default='')
    phone_number = models.CharField(max_length=15, blank=True, default='')
    point_of_contact = models.ForeignKey(
        get_user_model(), on_delete='PROTECT', null=True,
        related_name="organization_point_of_contact")
    addresses = models.ManyToManyField(Address, blank=True)
    users = models.ManyToManyField(
        get_user_model(), blank=True, related_name='org_staff')
    identifiers = models.ManyToManyField(OrganizationIdentifier, blank=True)

    def __str__(self):
        return self.name

    @property
    def signnup_url(self):
        return "%s%s" % (settings.HOSTNAME_URL, reverse(
            'create_org_account', args=(self.slug,)))

    def save(self, commit=True, *args, **kwargs):
        self.slug = slugify(self.name)
        if commit:
            super(Organization, self).save(*args, **kwargs)


class OrganizationAffiliationRequest(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete='PROTECT')
    organization = models.ForeignKey(Organization, on_delete='PROTECT')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "organization"),)
        permissions = (("can_approve_affiliation", "Can approve affiliation"),)

    def __str__(self):
        return "%s %s seeks affiliation approval for %s" % (
            self.user.first_name, self.user.last_name, self.organization.name)

    def save(self, commit=True, **kwargs):
        if commit:
            send_new_org_account_approval_email(
                to_user=self.organization.point_of_contact,
                about_user=self.user)
            super(OrganizationAffiliationRequest, self).save(**kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE,
                                db_index=True, null=False)
    subject = models.CharField(max_length=64, default='', blank=True,
                               help_text='Subject for identity token',
                               db_index=True)
    nickname = models.CharField(
        max_length=255,
        default='',
        blank=True,
        help_text='Nickname, alias, or other names used.')
    email_verified = models.BooleanField(default=False, blank=True)
    phone_verified = models.BooleanField(default=False, blank=True)
    mobile_phone_number = PhoneNumberField(blank=True, default="", unique=True,
                                           help_text=_('US numbers only.'),)

    mobile_phone_number_verified = models.BooleanField(
        blank=True, default=False)

    four_digit_suffix = models.CharField(
        max_length=4, blank=True, default="",
        help_text=_('If populated, this field must contain exactly four numbers.'),)
    sex = models.CharField(choices=SEX_CHOICES,
                           max_length=1, default="U",
                           help_text=_('Sex'),
                           )
    gender_identity = models.CharField(choices=GENDER_CHOICES,
                                       max_length=3, default="U",
                                       help_text=_('Gender / Gender Identity'),
                                       )
    birth_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def save(self, commit=True, **kwargs):
        if not self.subject:
            self.subject = generate_subject_id(prefix=settings.SUBJECT_LUHN_PREFIX,
                                               number_1=self.mobile_phone_number,
                                               number_2=self.four_digit_suffix)

        if commit:
            super(UserProfile, self).save(**kwargs)

    def __str__(self):
        display = '%s %s (%s)' % (self.user.first_name,
                                  self.user.last_name,
                                  self.user.username)
        return display

    @property
    def given_name(self):
        return self.user.first_name

    @property
    def family_name(self):
        return self.user.last_name

    @property
    def phone_number(self):
        return self.mobile_phone_number

    @property
    def preferred_username(self):
        return self.user.username

    @property
    def preferred_gender(self):
        return self.sex

    @property
    def preferred_birthdate(self):
        return str(self.birth_date)

    @property
    def sub(self):
        return self.subject

    @property
    def gender(self):
        return self.sex

    @property
    def birthdate(self):
        return self.birth_date

    @property
    def name(self):
        name = '%s %s' % (self.user.first_name, self.user.last_name)
        return name

    @property
    def ial(self):
        o, created = IdentityAssuranceLevelDocumentation.objects.get_or_create(
            subject_user=self.user)
        return str(o.level)

    @property
    def aal(self):
        return "1"

    @property
    def profile_url(self):
        return ""

    @property
    def website(self):
        return ""

    @property
    def picture(self):
        return ""

    @property
    def vot(self):
        """Vectors of Trust rfc8485"""
        # TODO Add MFA support
        response = ""
        ial = self.ial
        aal = self.aal
        if ial == "2":
            response = "%sP2." % (response)
        else:
            response = "%sP0." % (response)
        if aal == "1":
            response = "%sCc" % (response)
        else:
            response = "%sCc" % (response)
        return response

    @property
    def address(self):
        formatted_addresses = []
        addresses = Address.objects.filter(user=self.user)
        for a in addresses:
            formatted_addresses.append(a.formatted_address)
        return formatted_addresses

    @property
    def doc(self):
        formatted_identifiers = []
        identifiers = IndividualIdentifier.objects.filter(user=self.user)
        for i in identifiers:
            formatted_identifiers.append(i.doc_oidc_format)
        return formatted_identifiers

    @property
    def organizations(self):
        # Get the organizations for this user.
        orgs = []
        for o in Organization.objects.all():
            for u in o.users.all():
                if u == self.user:
                    orgs.append(o)
        return orgs


MFA_CHOICES = (
    ('', 'None'),
    ('EMAIL', "Email"),
    ('FIDO', "FIDO U2F"),
    ('SMS', "Text Message (SMS)"),
)


class MFACode(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
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

    @property
    def endpoint(self):
        e = ""
        up = UserProfile.objects.get(user=self.user)
        if self.mode == "SMS" and up.mobile_phone_number:
            e = up.mobile_phone_number
        if self.mode == "EMAIL" and self.user.email:
            e = self.user.email
        return e

    def save(self, commit=True, **kwargs):
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
        if commit:
            super(MFACode, self).save(**kwargs)


class ActivationKey(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    key = models.CharField(default=uuid.uuid4, max_length=40)
    expires = models.DateTimeField(blank=True)

    def __str__(self):
        return 'Key for %s expires at %s' % (self.user.username,
                                             self.expires)

    def save(self, commit=True, **kwargs):
        self.signup_key = str(uuid.uuid4())

        now = pytz.utc.localize(datetime.utcnow())
        expires = now + timedelta(days=settings.SIGNUP_TIMEOUT_DAYS)
        self.expires = expires

        # send an email with reset url
        send_activation_key_via_email(self.user, self.key)
        if commit:
            super(ActivationKey, self).save(**kwargs)


class ValidPasswordResetKey(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    reset_password_key = models.CharField(max_length=50, blank=True)
    # switch from datetime.now to timezone.now
    expires = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s for user %s expires at %s' % (self.reset_password_key,
                                                 self.user.username,
                                                 self.expires)

    def save(self, commit=True, **kwargs):
        self.reset_password_key = str(uuid.uuid4())
        # use timezone.now() instead of datetime.now()
        now = timezone.now()
        expires = now + timedelta(minutes=1440)
        self.expires = expires

        # send an email with reset url
        send_password_reset_url_via_email(self.user, self.reset_password_key)
        if commit:
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
