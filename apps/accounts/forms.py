from django import forms
import re
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from phonenumber_field.formfields import PhoneNumberField
from .models import UserProfile, create_activation_key, SEX_CHOICES, GENDER_CHOICES

# Copyright Videntity Systems Inc.

YEARS = [x for x in range(1901, 2000)]

agree_tos_label = mark_safe(
    'Do you agree to the <a href="%s">Terms of Service</a> and <a href="%s">Privacy Policy</a>?' % (settings.TOS_URI,
                                                                                                    settings.POLICY_URI))

User = get_user_model()


class PasswordResetRequestForm(forms.Form):
    email = forms.CharField(max_length=75, label=_('Email or User Name'))
    required_css_class = 'required'


class PasswordResetForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, max_length=150,
                                label=_('Password*'))
    password2 = forms.CharField(widget=forms.PasswordInput, max_length=150,
                                label=_('Password (again)*'))

    required_css_class = 'required'

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError(_('The two password fields '
                                          'didn\'t match.'))

        try:
            validate_password(password1)
        except ValidationError as err:
            raise forms.ValidationError(err.error_list[0])
        return password2


class SignupForm(forms.Form):
    username = forms.CharField(max_length=30, label=_(
        "User Name*"), help_text="Your desired user name or handle.")
    pick_your_account_number = forms.CharField(max_length=10, label=_(
        "Choose Your Own Account Number"), help_text="Pick up to 10 numbers to be included in your account number.",
        required=False)
    first_name = forms.CharField(max_length=100, label=_("First/Given Name*"))
    last_name = forms.CharField(max_length=100, label=_("Last/Family Name*"))
    middle_name = forms.CharField(
        max_length=255, label=_("Middle Name"), required=False)
    nickname = forms.CharField(max_length=100, required=False)
    mobile_phone_number = PhoneNumberField(required=False,
                                           label=_(
                                               "Mobile Phone Number"))
    email = forms.EmailField(max_length=75, required=False)
    sex = forms.ChoiceField(choices=SEX_CHOICES, required=False,
                            help_text="Enter birth sex. We use this information to help look up your information.")
    gender_identity = forms.ChoiceField(choices=GENDER_CHOICES, required=False,
                                        label=_("Gender"),
                                        help_text="""Gender identity is not necessarily the same
                                                     as birth sex and a custom value may be supplied.""")
    gender_identity_custom_value = forms.CharField(required=False,
                                                   help_text="If gender identity is custom, include your gender here.")
    birth_date = forms.DateField(label='Birth Date', widget=forms.SelectDateWidget(years=settings.BIRTHDATE_YEARS),
                                 required=False, help_text="We use this information to help look up your information.")
    password1 = forms.CharField(widget=forms.PasswordInput, max_length=128,
                                label=_("Password"),
                                help_text=_("Passwords must be at least 8 characters and not be too common."))
    password2 = forms.CharField(widget=forms.PasswordInput, max_length=128,
                                label=_("Password (again)"))
    agree_tos = forms.BooleanField(label=_(agree_tos_label))
    required_css_class = 'required'

    def clean_first_name(self):
        return self.cleaned_data.get("first_name", "").strip().upper()

    def clean_last_name(self):
        return self.cleaned_data.get("last_name", "").strip().upper()

    def clean_middle_name(self):
        return self.cleaned_data.get("middle_name", "").strip().upper()

    def clean_nickname(self):
        return self.cleaned_data.get("nickname", "").strip().upper()

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(
                _("The two password fields didn't match."))

        try:
            validate_password(password1)
        except ValidationError as err:
            raise forms.ValidationError(err.error_list[0])

        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email', "").strip().lower()
        if email:
            username = self.cleaned_data.get('username')
            if email and User.objects.filter(email=email).exclude(
                    username=username).count():
                raise forms.ValidationError(
                    _('This email address is already registered.'))
            return email
        else:
            return email

    def clean_username(self):
        username = self.cleaned_data.get('username').strip().lower()
        if User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError(_('This username is already taken.'))

        pattern = re.compile(r'^[\w.@+-]+\Z')
        if not pattern.match(username):
            message = _('Enter a valid username. This value may contain only English letters, '
                        'numbers, and @/./+/-/_ characters.')
            raise forms.ValidationError(_(message))

        return username

    def clean_pick_your_account_number(self):
        pick_your_account_number = self.cleaned_data.get(
            'pick_your_account_number')
        if pick_your_account_number:
            if not RepresentsPositiveInt(pick_your_account_number):
                raise forms.ValidationError(
                    _('This value must only include numbers.'))
        return pick_your_account_number

    def save(self):

        new_user = User.objects.create_user(
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'],
            is_active=True)

        UserProfile.objects.create(
            user=new_user,
            number_str_include=self.cleaned_data.get(
                'pick_your_account_number', ""),
            middle_name=self.cleaned_data.get('middle_name', ""),
            mobile_phone_number=self.cleaned_data['mobile_phone_number'],
            nickname=self.cleaned_data.get('nickname', ""),
            sex=self.cleaned_data.get('sex', ""),
            gender_identity=self.cleaned_data.get('gender_identity', ""),
            gender_identity_custom_value=self.cleaned_data.get(
                'gender_identity_custom_value', ""),
            birth_date=self.cleaned_data.get('birth_date', ""),
            agree_tos=settings.CURRENT_TOS_VERSION,
            agree_privacy_policy=settings.CURRENT_PP_VERSION)

        # Send a verification email
        create_activation_key(new_user)
        return new_user


class DeleteAccountForm(forms.Form):
    are_you_sure = forms.BooleanField(label=_("Are you sure?"),
                                      help_text=_("Check the box and press continue to delete your account."))

    required_css_class = 'required'


class AccountSettingsForm(forms.Form):
    username = forms.CharField(max_length=30, label=_("User Name*"))
    first_name = forms.CharField(max_length=100, label=_("First Name*"))
    last_name = forms.CharField(max_length=100, label=_("Last Name*"))
    middle_name = forms.CharField(
        max_length=255, label=_("Middle Name"), required=False)
    nickname = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(label=_('Email'), required=False)
    mobile_phone_number = PhoneNumberField(required=False, label=_("Mobile Phone Number"))
    website = forms.CharField(max_length=512, label=_("Website"), required=False)
    sex = forms.ChoiceField(choices=SEX_CHOICES,
                            required=False,
                            help_text="Enter sex, not gender identity.")
    gender_identity = forms.ChoiceField(choices=GENDER_CHOICES, required=False,
                                        label=_("Gender"),
                                        help_text="Gender identity is not necessarily the same as birth sex.")
    gender_identity_custom_value = forms.CharField(required=False,
                                                   help_text="If gender identity is custom, include your gender here.")
    birth_date = forms.DateField(label='Birth Date', widget=forms.SelectDateWidget(years=YEARS),
                                 required=False)
    required_css_class = 'required'

    def clean_first_name(self):
        return self.cleaned_data.get("first_name", "").strip().upper()

    def clean_last_name(self):
        return self.cleaned_data.get("last_name", "").strip().upper()

    def clean_middle_name(self):
        return self.cleaned_data.get("middle_name", "").strip().upper()

    def clean_nickname(self):
        return self.cleaned_data.get("nickname", "").strip().upper()

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if email:
            if email and User.objects.filter(
                    email=email).exclude(email=email).count():
                raise forms.ValidationError(_('This email address is '
                                              'already registered.'))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username').strip().lower()
        if username and User.objects.filter(
                username=username).exclude(username=username).count():
            raise forms.ValidationError(_('This username is already taken.'))
        return username

    def save(self):

        user = User.objects.get(username=self.cleaned_data['username'])
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        user.save()

        up, created = UserProfile.objects.get_or_create(user=user)
        up.nickname = self.cleaned_data.get('nickname', "")
        up.middle_name = self.cleaned_data.get('middle_name', "")
        up.website = self.cleaned_data.get('website', "")
        up.sex = self.cleaned_data.get('sex', ""),
        up.gender_identity = self.cleaned_data.get('gender_identity', ""),
        up.gender_identity_custom_value = self.cleaned_data.get(
            'gender_identity_custom_value', ""),
        up.birth_date = self.cleaned_data.get('birth_date', ""),
        up.save()
        return user


def RepresentsPositiveInt(s):
    try:
        i = int(s)
        if i > 0:
            return True
        return False
    except ValueError:
        return False
