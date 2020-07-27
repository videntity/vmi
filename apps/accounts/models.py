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
                     send_new_org_account_approval_email)
from .subject_generator import generate_subject_id
from collections import OrderedDict
from ..ial.models import IdentityAssuranceLevelDocumentation
from twilio.rest import Client
import logging

logger = logging.getLogger('verifymyidentity_.%s' % __name__)

# Copyright Videntity Systems Inc.

__author__ = "Alan Viars"


SEX_CHOICES = (('',  'Blank'),
               ('female', 'Female'),
               ('male', 'Male'),
               ('other', 'Other'),
               )

GENDER_CHOICES = (('', 'Blank'),
                  ('female', 'Female'),
                  ('male', 'Male'),
                  ('custom', 'Custom')
                  )

# For Passports, SSNs, URIs, MPIs, etc.


class IndividualIdentifier(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True)
    type = models.CharField(choices=settings.INDIVIDUAL_ID_TYPE_CHOICES,
                            max_length=255, blank=True, default='', db_index=True)
    name = models.SlugField(max_length=255, blank=True,
                            default='', db_index=True)

    issuer = models.CharField(max_length=255, blank=True, default='')
    # ISO 3166-1
    country = models.CharField(max_length=2, blank=True,
                               default=settings.DEFAULT_COUNTRY_CODE_FOR_INDIVIDUAL_IDENTIFIERS, db_index=True,
                               help_text="e.g., a two letter country code in ISO 3166 format.")

    # ISO 3166-2
    subdivision = models.CharField(max_length=2, blank=True, default='',
                                   verbose_name="State",
                                   help_text="A country's subdivision such as a state or province.")

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
        od['issuer'] = self.issuer
        od['country'] = self.country
        od['subdivision'] = self.subdivision
        od['uri'] = self.uri
        return od

    def save(self, commit=True, *args, **kwargs):
        self.slug = slugify(self.name)
        if commit:
            if not self.name:
                self.name = self.type
            super(IndividualIdentifier, self).save(*args, **kwargs)

# For Tax ID's NPIs, PECOOS IDs, etc.


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

# For Addresses


class Address(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, db_index=True, editable=False)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True)
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

# Future Version - Experimental


class PersonToPersonRelationship(models.Model):
    grantor = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True,
        related_name="persontoperson_grantor")
    grantee = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, null=True,
        related_name="persontoperson_grantee")
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = [['grantor', 'grantee']]

# For Organizations such as governments, companies, non-profits,
# professional groups, etc.


class Organization(models.Model):
    ORG_STATUS_CHOICES = (('ACTIVE', 'Active'),
                          ("INACTIVE", "Inactive"),
                          ("SUSPENDED", "Suspended"))

    status = models.CharField(
        max_length=20, default='ACTIVE', choices=ORG_STATUS_CHOICES)
    name = models.CharField(max_length=250, default='', blank=True)
    number_str_include = models.CharField(
        max_length=10, blank=True, default="",
        verbose_name="Pick Your Own ID",
        help_text=_('Choose up to 10 number to be included in your account number.'))
    slug = models.SlugField(max_length=250, blank=True, default='',
                            db_index=True,
                            help_text=_('Do not change this unless you know what you are doing.'))
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
        help_text="These are the members of an organization. (i.e. customers)")

    users = models.ManyToManyField(
        get_user_model(), blank=True, related_name='org_staff', verbose_name="Organizational Agents",
        help_text="Agents are employees, contractors or persons acting on behalf of the organization.")

    auto_ial_2_for_agents = models.BooleanField(default=True, blank=True)
    auto_ial_2_for_agents_description = models.TextField(default=settings.AUTO_IAL_2_DESCRIPTION,
                                                         blank=True)

    default_groups_for_agents = models.ManyToManyField(Group, blank=True,
                                                       help_text="All new agents will be in these groups by default.")

    open_member_enrollment = models.BooleanField(
        default=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def signup_url(self):
        return "%s%s" % (settings.HOSTNAME_URL, reverse(
            'create_org_account', args=(self.slug,)))

    @property
    def member_signup_url(self):
        return "%s%s" % (settings.HOSTNAME_URL, reverse(
            'create_member_account', args=(self.slug,)))

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

        if not self.slug:
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
                        break

        if commit:
            super(Organization, self).save(*args, **kwargs)
            # If the POC is not an org agent, then make them one.


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
            print("send to", self.organization.point_of_contact.email)
            send_new_org_account_approval_email(
                to_user=self.organization.point_of_contact,
                about_user=self.user,
                organization=self.organization)

            super(OrganizationAffiliationRequest, self).save(**kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE,
                                db_index=True, null=False)
    subject = models.CharField(max_length=64, default='', blank=True,
                               help_text='Subject for identity token',
                               db_index=True)
    middle_name = models.CharField(max_length=255, default='', blank=True,
                                   help_text='Middle Name',)
    picture = models.ImageField(
        upload_to='profile-picture/', null=True, blank=True)
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
                                           help_text=_('United States phone numbers only.'))
    password_recovery_passphrase = models.TextField(default="", blank=True)
    password_recovery_passphrase_hash = models.TextField(
        default="", blank=True)
    public_key = models.TextField(default="", blank=True)
    private_key = models.TextField(default="", blank=True)
    website = models.TextField(default='', blank=True,
                               help_text='A personal website.',)
    mobile_phone_number_verified = models.BooleanField(
        blank=True, default=False)

    number_str_include = models.CharField(
        max_length=10, blank=True, default="",
        verbose_name="Pick Your Own ID",
        help_text=_('Choose up to 10 number to be included in your account number.'))

    sex = models.CharField(choices=SEX_CHOICES,
                           max_length=6, default="", blank=True,
                           help_text=_(
                               'Specify birth sex, not gender identity.')
                           )
    gender_identity = models.CharField(choices=GENDER_CHOICES,
                                       verbose_name="Gender",
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
    verifying_agent_email = models.EmailField(
        blank=True, default="", help_text="Email of agent performing identity verification.")
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
        display = '%s %s (%s)' % (self.user.first_name.lower().title(),
                                  self.user.last_name.lower().title(),
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
    def gender_flattened(self):
        if self.gender_identity_custom_value:
            return self.gender_identity_custom_value.title()
        elif self.gender_identity:
            return self.gender_identity.title()
        return ""

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
                subject_user=self.user, )

        od = OrderedDict()
        od["verification"] = OrderedDict()
        od["verification"]["trust_framework"] = "nist_800_63A_ial_2"
        od["verification"]["time"] = str(self.updated_at)
        od["verification"]["evidence"] = []

        for i in ialds:
            od = OrderedDict()
            od["verification"] = OrderedDict()
            od["verification"]["trust_framework"] = "nist_800_63A_ial_2"
            od["verification"]["time"] = str(self.updated_at)
            od["verification"]["evidence"] = []

            if i.level != "1":
                od["verification"]["evidence"].append(i.oidc_ia_evidence)
                od["verification"]["claims"] = OrderedDict()

                # TODO Check the list of claims to be applied.
                od["verification"]["claims"]["given_name"] = self.given_name
                od["verification"]["claims"]["family_name"] = self.family_name

                if i.evidence_type == "id_document":
                    od["verification"]["claims"][
                        "birthdate"] = self.preferred_birthdate
                if i.evidence_type == "utility_bill":
                    od["verification"]["claims"]["address"] = self.address
                # od["verification"]["claims"]["gender"] = self.gender
                vpa_list.append(od)

        return vpa_list

    @property
    def aal(self):
        return "1"

    @property
    def profile_url(self):
        return "%s%s" % (settings.HOSTNAME_URL, reverse(
            'user_profile_subject', args=(self.subject,)))

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
        # https://tools.ietf.org/html/rfc8485
        # Signed and verifiable assertion, passed through the user agent (web
        # browser)
        response = ""
        ial = self.ial
        aal = self.aal
        if ial == "1":
            response = "%sP1." % (response)
        elif ial == "2":
            response = "%sP2." % (response)
        elif ial == "3":
            response = "%sP3." % (response)
        else:
            response = "%sP0." % (response)

        if aal == "1":
            response = "%sC1" % (response)
        elif aal == "2":
            response = "%sC2" % (response)
        elif aal == "3":
            response = "%sC3" % (response)
        else:
            response = "%sC1" % (response)
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
    def agent_to_organization(self):
        # Get the organizations for this user.
        orgs = []
        for o in Organization.objects.all():
            for u in o.users.all():
                if u == self.user:
                    orgs.append(o.formatted_organization)
        return orgs

    @property
    def agent_organizations(self):
        # Get the organizations for this user is an agent.
        orgs = []
        for o in Organization.objects.all():
            for u in o.users.all():
                if u == self.user:
                    orgs.append(o)
        return orgs

    @property
    def member_organizations(self):
        # Get the organizations for which this user is a member.
        orgs = []
        for o in Organization.objects.all():
            for u in o.members.all():
                if u == self.user:
                    orgs.append(o)
        return orgs

    @property
    def member_to_organization(self):
        # Get the organizations for this user as formated organizations.
        members = []
        for o in Organization.objects.all():
            for m in o.members.all():
                if m == self.user:
                    members.append(o.formatted_organization)
        return members


MFA_CHOICES = (
    ('', 'None'),
    ('EMAIL', _("Email")),
    ('FIDO', _("FIDO U2F or FIDO 2.0")),
    ('SMS', _("Text Message (SMS)")),
)


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
            self.expires = now + timedelta(days=1)
            self.code = str(random.randint(1000, 9999))
            up = UserProfile.objects.get(user=self.user)
            if up.mobile_phone_number:

                number = "%s" % (up.mobile_phone_number)
                # Send SMS to up.mobile_phone_number
                if settings.SMS_STRATEGY == "AWS-SNS":
                    sns = boto3.client('sns', region_name='us-east-1')
                    sns.publish(
                        PhoneNumber=number,
                        Message="Your verification code for %s is : %s" % (settings.ORGANIZATION_NAME,
                                                                           self.code),
                        MessageAttributes={
                            'AWS.SNS.SMS.SenderID': {
                                'DataType': 'String',
                                'StringValue': 'MySenderID'
                            }
                        }
                    )
                    logger.info("Message sent to %s by AWS SNS." % (number))

                if settings.SMS_STRATEGY == "TWILIO":
                    client = Client(settings.TWILIO_ACCOUNT_SID,
                                    settings.TWILIO_TOKEN)
                    message = client.messages.create(
                        to=str(number),
                        from_=settings.TWILIO_FROM_NUMBER,
                        body="Your verification code for %s is : %s" % (settings.ORGANIZATION_NAME,
                                                                        self.code))
                    logger.info("Message sent to %s by Twilio. %s" %
                                (number, message.sid))

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
