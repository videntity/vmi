import pytz
import random
import uuid
from django.template.defaultfilters import slugify
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
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


SEX_CHOICES = (('female', 'Female'),
               ('male', 'Male'),
               ('other', 'Gender Neutral'),
               ('',  'Left Blank'))

GENDER_CHOICES = (('female', 'Female'),
                  ('male', 'Male'),
                  ('custom', 'Custom'))


class IndividualIdentifier(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, null=True)
    type = models.CharField(choices=settings.INDIVIDUAL_ID_TYPE_CHOICES,
                            max_length=255, blank=True, default='', db_index=True)
    name = models.SlugField(max_length=255, blank=True,
                            default='', db_index=True)
    # ISO 3166-1
    country = models.CharField(max_length=2, blank=True,
                               default=settings.DEFAULT_COUNTRY_CODE_FOR_INDIVIDUAL_IDENTIFIERS, db_index=True,
                               help_text="e.g., a two letter country code in ISO 3166 format.")

    # ISO 3166-2
    subdivision = models.CharField(max_length=2, blank=True, default='',
                                   verbose_name="State",
                                   help_text="e.g., a country's subdivision such as a state or province.")

    value = models.CharField(max_length=250, blank=True,
                             default='', db_index=True)

    uri = models.TextField(blank=True, default='', db_index=True)

    metadata = models.TextField(
        blank=True,
        default='',
        help_text="JSON Object")

    def __str__(self):
        return self.value

    @property
    def doc_oidc_format(self):
        od = OrderedDict()
        od['type'] = self.type
        od['num'] = self.value
        return od

    @property
    def region(self):
        return self.subdivision

    @property
    def state(self):
        return self.subdivision

    @property
    def doc_oidc_format_enhanced(self):
        od = self.doc_oidc_format
        od['country'] = self.country
        od['subdivision'] = self.subdivision
        od['type'] = self.type
        od['uri'] = self.uri
        return od

    def save(self, commit=True, *args, **kwargs):
        self.slug = slugify(self.name)
        if commit:
            if not self.name:
                self.name = self.type
            super(IndividualIdentifier, self).save(*args, **kwargs)


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
    uuid = models.UUIDField(default=uuid.uuid4, db_index=True, editable=False)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, null=True)
    street_1 = models.CharField(max_length=250, blank=True, default='')
    street_2 = models.CharField(max_length=250, blank=True, default='')
    city = models.CharField(max_length=250, blank=True, default='')
    state = models.CharField(max_length=2, blank=True, default='')
    zipcode = models.CharField(max_length=10, blank=True, default='')
    country = models.CharField(max_length=2, blank=True, default='')
    # org_identifiers = models.ManyToManyField(
    #    OrganizationIdentifier, blank=True, related_name="addresses_org_identifiers")
    # ind_identifiers = models.ManyToManyField(IndividualIdentifier, blank=True)
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
    def formatted(self):
        return '%s %s\n%s, %s %s' % (
            self.street_1, self.street_2, self.city, self.state, self.zipcode)

    @property
    def formatted_address(self):
        od = OrderedDict()
        od['formatted'] = self.formatted
        od['street_address'] = self.street_address
        od['locality'] = self.locality
        od['region'] = self.region
        od['postal_code'] = self.zipcode
        od['country'] = self.country
        return od


class PersonToPersonRelationship(models.Model):
    grantor = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, null=True,
        related_name="persontoperson_grantor")
    grantee = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, null=True,
        related_name="persontoperson_grantee")
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = [['grantor', 'grantee']]


class Organization(models.Model):
    name = models.CharField(max_length=250, default='', blank=True)
    slug = models.SlugField(max_length=250, blank=True, default='',
                            db_index=True, unique=True, editable=False)
    subject = models.CharField(max_length=64, default='', blank=True,
                               help_text='Subject ID',
                               db_index=True)
    picture = models.ImageField(
        upload_to='organization-logo/', null=True, blank=True)

    registration_code = models.CharField(max_length=100,
                                         default='',
                                         blank=True)
    domain = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Email Domain(s)',
        help_text="A list of domains separated by white space. If populated, restrict email registration to these domains.")
    website = models.CharField(max_length=512, blank=True, default='')
    phone_number = models.CharField(max_length=15, blank=True, default='')
    agree_tos = models.CharField(max_length=64, default="", blank=True,
                                 help_text=_('Do you agree to the terms and conditions?'))
    agree_privacy_policy = models.CharField(max_length=64, default="", blank=True,
                                            help_text=_('Do you agree to the privacy policy?'))

    point_of_contact = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True,
        related_name="organization_point_of_contact")
    addresses = models.ManyToManyField(
        Address, blank=True, related_name="organization_addresses")

    members = models.ManyToManyField(
        get_user_model(), blank=True, related_name='org_members',
        help_text="This field is a placeholder and is not supported in this version.")

    users = models.ManyToManyField(
        get_user_model(), blank=True, related_name='org_staff', verbose_name="Organization Agent",
        help_text="Employees or contractors acting on behalf of the organization.")

    auto_ial_2_for_agents = models.BooleanField(default=True, blank=True)
    auto_ial_2_for_agents_description = models.TextField(default=settings.AUTO_IAL_2_DESCRIPTION,
                                                         blank=True)

    default_groups_for_agents = models.ManyToManyField(Group, blank=True,
                                                       help_text="All new agents will be in these groups by default.")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def signup_url(self):
        return "%s%s" % (settings.HOSTNAME_URL, reverse(
            'create_org_account', args=(self.slug,)))

    @property
    def formatted_organization(self):
        od = OrderedDict()
        od['name'] = self.name
        od['slug'] = self.slug
        od['sub'] = self.subject
        od['picture'] = self.picture_url
        od['website'] = self.website
        od['phone_number'] = self.phone_number
        od['point_of_contact'] = self.point_of_contact_dict
        return od

    @property
    def point_of_contact_dict(self):
        od = OrderedDict()
        self.point_of_contact
        up = UserProfile.objects.get(user=self.point_of_contact)
        od['first_name'] = self.point_of_contact.first_name
        od['last_name'] = self.point_of_contact.last_name
        od['phone_number'] = up.phone_number
        od['email'] = self.point_of_contact.email
        od['sub'] = up.sub
        return od

    @property
    def picture_url(self):
        if self.picture:
            p = "%s%s" % (settings.HOSTNAME_URL, self.picture.url)
            if p.count('http') == 2:
                return self.picture.url
            return p

    def save(self, commit=True, *args, **kwargs):
        self.slug = slugify(self.name)
        if not self.subject:
            self.subject = generate_subject_id(prefix=settings.SUBJECT_LUHN_PREFIX,
                                               starts_with="2",
                                               number_str_include=self.number_str_include)

            # Make sure the Subject has not been assigned to someone else.
            up_exist = Organization.objects.filter(
                subject=self.subject).exists()
            if up_exist:
                while True:
                    self.subject = generate_subject_id(prefix=settings.SUBJECT_LUHN_PREFIX,
                                                       starts_with="2",
                                                       number_str_include=self.number_str_include)
                    if not UserProfile.objects.filter(subject=self.subject).exists():
                        break;
        if commit:
            super(Organization, self).save(*args, **kwargs)


class OrganizationAffiliationRequest(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
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
    middle_name = models.CharField(max_length=255, default='', blank=True,
                                   help_text='Middle Name',)
    picture = models.ImageField(upload_to='profile-picture/', null=True)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE,
                                db_index=True, null=False)

    nickname = models.CharField(
        max_length=255,
        default='',
        blank=True,
        help_text='Nickname, alias, or other names used.')
    email_verified = models.BooleanField(default=False, blank=True)
    phone_verified = models.BooleanField(default=False, blank=True)
    mobile_phone_number = PhoneNumberField(blank=True, default="",
                                           help_text=_('US numbers only.'),)
    password_recovery_passphrase = models.TextField(default="", blank=True)
    password_recovery_passphrase_hash = models.TextField(
        default="", blank=True)
    public_key = models.TextField(default="", blank=True)
    private_key = models.TextField(default="", blank=True)

    mobile_phone_number_verified = models.BooleanField(
        blank=True, default=False)

    number_str_include = models.CharField(
        max_length=10, blank=True, default="",
        verbose_name="Pick Your Own ID",
        help_text=_('Choose up to 10 number to be included in your account number.'))

    sex = models.CharField(choices=SEX_CHOICES,
                           max_length=6, default="", blank=True,
                           help_text=_('Specify sex, not gender identity.')
                           )
    gender_identity = models.CharField(choices=GENDER_CHOICES,
                                       max_length=64, default="", blank=True,
                                       help_text=_(
                                           'Gender Identity is not necessarily the same as birth sex.'),
                                       )
    gender_identity_custom_value = models.CharField(max_length=64, default="", blank=True,
                                                    help_text=_(
                                                        'Enter a custom value for gender_identity.'),
                                                    )
    birth_date = models.DateField(blank=True, null=True)
    agree_tos = models.CharField(max_length=64, default="", blank=True,
                                 help_text=_('Do you agree to the terms and conditions?'))
    agree_privacy_policy = models.CharField(max_length=64, default="", blank=True,
                                            help_text=_('Do you agree to the privacy policy?'))
    attest_training_completed = models.BooleanField(default=False, blank=True,
                                                    help_text=_("""Yes, I attest that I have completed the
                                                        training for this system and will abide by
                                                        the code of conduct."""))
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def save(self, commit=True, **kwargs):
        if not self.subject:
            self.subject = generate_subject_id(prefix=settings.SUBJECT_LUHN_PREFIX,
                                               number_str_include=self.number_str_include)

            # Make sure the Subject has not been assigned to someone else.
            up_exist = UserProfile.objects.filter(
                subject=self.subject).exists()
            if up_exist:
                while True:
                    self.subject = generate_subject_id(prefix=settings.SUBJECT_LUHN_PREFIX,
                                                       number_str_include=self.number_str_include)
                    if not UserProfile.objects.filter(subject=self.subject).exists():
                        break

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
        return str(self.mobile_phone_number)

    def get_verified_phone_number(self):
        return self.phone_number if self.phone_verified else None

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
        level = 1
        ialdocs = IdentityAssuranceLevelDocumentation.objects.filter(
            subject_user=self.user)
        for doc in ialdocs:
            if int(doc.level) == 2:
                if level == 1:
                    level = doc.level
            elif int(doc.level) == 3:
                level = int(doc.level)
        return str(level)

    @property
    def verified_claims(self):
        vpa_list = []
        ialds = IdentityAssuranceLevelDocumentation.objects.filter(
            subject_user=self.user)

        if not ialds:
            IdentityAssuranceLevelDocumentation.objects.create(
                subject_user=self.user)
            ialds = IdentityAssuranceLevelDocumentation.objects.filter(
                subject_user=self.user)

        od = OrderedDict()
        od["verification"] = OrderedDict()
        od["verification"]["trust_framework"] = "nist_800_63A_ial_2"
        od["verification"]["time"] = str(self.updated_at)
        od["verification"]["evidence"] = []

        for i in ialds:
            od["verification"]["evidence"].append(i.oidc_ia_evidence)
            od["verification"]["claims"] = OrderedDict()
            od["verification"]["claims"]["given_name"] = self.given_name
            od["verification"]["claims"]["family_name"] = self.family_name
            od["verification"]["claims"][
                "birthdate"] = self.preferred_birthdate
            od["verification"]["claims"]["gender"] = self.gender
            vpa_list.append(od)
        return vpa_list

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
    def picture_url(self):
        if self.picture:
            p = "%s%s" % (settings.HOSTNAME_URL, self.picture.url)
            if p.count('http') == 2:
                return self.picture.url
            return p

    @property
    def vot(self):
        """Vectors of Trust rfc8485"""
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
            formatted_identifiers.append(i.doc_oidc_format_enhanced)
        return formatted_identifiers

    @property
    def organization_agent(self):
        # Get the organizations for this user.
        orgs = []
        for o in Organization.objects.all():
            for u in o.users.all():
                if u == self.user:
                    orgs.append(o.formatted_organization)
        return orgs

    @property
    def organizations(self):
        # Get the organizations for this user.
        orgs = []
        for o in Organization.objects.all():
            for u in o.users.all():
                if u == self.user:
                    orgs.append(o)
        return orgs

    @property
    def memberships(self):
        # Get the organizations for this user.
        members = []
        for o in Organization.objects.all():
            for m in o.members.all():
                if m == self.user:
                    members.append(o.formatted_organization)
        return members


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
               up.mobile_phone_number:
                # Send SMS to up.mobile_phone_number
                sns = boto3.client(
                    'sns',
                    # aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    # aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name='us-east-1')
                number = "%s" % (up.mobile_phone_number)
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


class PhoneVerifyCode(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    uid = models.CharField(blank=True,
                           default=uuid.uuid4,
                           max_length=36, editable=False)
    tries_counter = models.IntegerField(default=0, editable=False)
    code = models.CharField(blank=True, max_length=4, editable=False)
    valid = models.BooleanField(default=True)
    expires = models.DateTimeField(blank=True)
    added = models.DateField(auto_now_add=True)

    def __str__(self):
        name = 'To %s via %s' % (self.user,
                                 self.mode)
        return name

    def save(self, commit=True, **kwargs):
        if not self.id:
            now = pytz.utc.localize(datetime.utcnow())
            expires = now + timedelta(days=1)
            self.expires = expires
            self.code = str(random.randint(1000, 9999))
            up = UserProfile.objects.get(user=self.user)
            if up.mobile_phone_number:
                # Send SMS to up.mobile_phone_number
                sns = boto3.client(
                    'sns',
                    # aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    # aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name='us-east-1')
                number = "%s" % (up.mobile_phone_number)
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
        if commit:
            super(PhoneVerifyCode, self).save(**kwargs)


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
        if self.user.email:
            send_password_reset_url_via_email(
                self.user, self.reset_password_key)
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
