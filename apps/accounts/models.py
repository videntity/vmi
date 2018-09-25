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
from django.urls import reverse
from .emails import (send_password_reset_url_via_email,
                     send_activation_key_via_email,
                     mfa_via_email)

# Copyright Videntity Systems Inc.

__author__ = "Alan Viars"


USER_CHOICES = (
    ('BEN', 'Beneficiary'),
    ('DEV', 'Developer'),
)

AAL_CHOICES = (
    ('1', 'ALA-1'),
    ('2', 'AAL-2'),
    ('3', 'AAL-3'),
)


IAL_CHOICES = (
    ('1', 'ILA-1'),
    ('2', 'IAL-2'),
    ('3', 'IAL-3'),
)

QUESTION_1_CHOICES = (
    ('1', 'What is your favorite color?'),
    ('2', 'What is your favorite vegetable?'),
    ('3', 'What is your favorite movie?'),
)

QUESTION_2_CHOICES = (
    ('1', 'What was the name of your best friend from childhood?'),
    ('2', 'What was the name of your elementary school?'),
    ('3', 'What was the name of your favorite pet?'),
)

QUESTION_3_CHOICES = (
    ('1', 'What was the make of your first automobile?'),
    ('2', "What was your maternal grandmother's maiden name?"),
    ('3', "What was your paternal grandmother's maiden name?"),
)

MFA_CHOICES = (
    ('', 'None'),
    ('EMAIL', "Email"),
    ('FIDO', "FIDO U2F"),
    ('SMS', "Text Message (SMS)"),
)


@python_2_unicode_compatible
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=255,
                                         blank=True,
                                         default='')
    aal = models.CharField(default='0',
                           choices=AAL_CHOICES,
                           max_length=1)
    ial = models.CharField(default='0',
                           choices=IAL_CHOICES,
                           max_length=1)
    user_type = models.CharField(default='DEV',
                                 choices=USER_CHOICES,
                                 max_length=5)

    
    # May not be needed.
    create_applications = models.BooleanField(
        blank=True,
        default=True,
        help_text=_(
            'Check this to allow the account to register applications.'),
    )
    
    
    # liekly needed/
    authorize_applications = models.BooleanField(
        blank=True,
        default=True,
        help_text=_(
            'Check this to allow the account to authorize applications.'),
    )

    mfa_login_mode = models.CharField(
        blank=True,
        default="",
        max_length=5,
        choices=MFA_CHOICES,
    )

    mobile_phone_number = models.CharField(
        max_length=12,
        blank=True,
        help_text=_('US numbers only.'),
    )

    password_reset_question_1 = models.CharField(default='1',
                                                 choices=QUESTION_1_CHOICES,
                                                 max_length=1)
    password_reset_answer_1 = models.CharField(default='',
                                               blank=True,
                                               max_length=50)
    password_reset_question_2 = models.CharField(default='1',
                                                 choices=QUESTION_2_CHOICES,
                                                 max_length=1)
    password_reset_answer_2 = models.CharField(default='',
                                               blank=True,
                                               max_length=50)
    password_reset_question_3 = models.CharField(default='1',
                                                 choices=QUESTION_3_CHOICES,
                                                 max_length=1)
    password_reset_answer_3 = models.CharField(default='',
                                               blank=True,
                                               max_length=50)

    def __str__(self):
        name = '%s %s (%s)' % (self.user.first_name,
                               self.user.last_name,
                               self.user.username)
        return name

    def name(self):
        if self.organization_name:
            return self.organization_name
        else:
            name = '%s %s' % (self.user.first_name, self.user.last_name)
        return name

    def save(self, **kwargs):
        if not self.access_key_id or self.access_key_reset:
            self.access_key_id = random_key_id()
            self.access_key_secret = random_secret()
        self.access_key_reset = False
        super(UserProfile, self).save(**kwargs)


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
    user = models.ForeignKey(User,on_delete=models.CASCADE)
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


def create_activation_key(user):
    # Create an new activation key and send the email.
    key = ActivationKey.objects.create(user=user)
    return key
