from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField
from .models import UserProfile, create_activation_key

# Copyright Videntity Systems Inc.

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


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, label=_('User'))
    password = forms.CharField(widget=forms.PasswordInput, max_length=128,
                               label=_('Password'))
    required_css_class = 'required'

    def clean_username(self):
        return self.cleaned_data.get("username", "").strip().lower()


class SignupForm(forms.Form):
    username = forms.CharField(max_length=30, label=_("User Name*"),
                               help_text="Your desired user name or handle.")
    first_name = forms.CharField(max_length=100, label=_("First Name*"))
    last_name = forms.CharField(max_length=100, label=_("Last Name*"))
    nickname = forms.CharField(max_length=100, required=False)
    mobile_phone_number = PhoneNumberField(required=False,
                                           label=_(
                                               "Mobile Phone Number"))

    email = forms.EmailField(max_length=75, required=False)
    password1 = forms.CharField(widget=forms.PasswordInput, max_length=128,
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput, max_length=128,
                                label=_("Password (again)"))
    required_css_class = 'required'

    def clean_first_name(self):
        return self.cleaned_data.get("first_name", "").strip().upper()

    def clean_last_name(self):
        return self.cleaned_data.get("last_name", "").strip().upper()

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
        return username

    def clean_four_digit_suffix(self):
        four_digit_suffix = self.cleaned_data.get('four_digit_suffix')
        if four_digit_suffix:
            if not RepresentsPositiveInt(four_digit_suffix, length=4):
                raise forms.ValidationError(
                    _('Your for digit suffix must be exactly 4 digits'))
        return four_digit_suffix

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
            mobile_phone_number=self.cleaned_data['mobile_phone_number'],
            nickname=self.cleaned_data.get('nickname', "")
        )

        # Send a verification email
        create_activation_key(new_user)
        return new_user


class AccountSettingsForm(forms.Form):
    first_name = forms.CharField(max_length=100, label=_("First Name*"))
    last_name = forms.CharField(max_length=100, label=_("Last Name*"))
    nickname = forms.CharField(max_length=100, required=False)
    username = forms.CharField(max_length=30)
    email = forms.EmailField(label=_('Email'), required=False)
    required_css_class = 'required'

    def clean_first_name(self):
        return self.cleaned_data.get("first_name", "").strip().upper()

    def clean_last_name(self):
        return self.cleaned_data.get("last_name", "").strip().upper()

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
        up.save()
        return user


def RepresentsPositiveInt(s, length=10):
    try:
        i = int(s)
        if i > 0 and len(s) == length:
            return True
        return False
    except ValueError:
        return False
