from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Organization
from django.conf import settings
from django.utils.safestring import mark_safe
from phonenumber_field.formfields import PhoneNumberField
from .models import SEX_CHOICES, IDCardConfirmation
from .texts import send_text
from ..ial.models import IdentityAssuranceLevelDocumentation
from django.core.exceptions import ValidationError
import re
# Copyright Videntity Systems Inc.

YEARS = [x for x in range(1901, 2002)]

User = get_user_model()

agree_tos_label = mark_safe(
    'Do you agree to the <a href="%s">Terms of Service</a> and <a href="%s">Privacy Policy</a>?' % (settings.TOS_URI,
                                                                                                    settings.POLICY_URI))


class ConfirmForm(forms.Form):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    middle_name = forms.CharField(
        max_length=100, label=_("Middle Name"), required=False)
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    mobile_phone_number = PhoneNumberField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    birth_date = forms.DateField(label=_('Birth Date*'), widget=forms.SelectDateWidget(
        attrs={'readonly': 'readonly'},
        years=settings.BIRTHDATE_YEARS),
        required=True, help_text="We use this information to help look up your information.")
    sex = forms.ChoiceField(label=_('Sex*'),
                            choices=SEX_CHOICES, required=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    email = forms.EmailField(max_length=150, label=_("Email"), required=False,
                             help_text=_("""An email email is highly
                                recommended so we may send
                                you important updates on
                                account activity"""))
    picture = forms.ImageField(required=False,
                               help_text=_("""Upload your profile picture."""))
    username = forms.CharField(max_length=30, label=_("Username*"))
    password1 = forms.CharField(widget=forms.PasswordInput, max_length=128, label=_("Password*"),
                                help_text=_("Passwords must be at least 8 characters and not be too common."))
    password2 = forms.CharField(
        widget=forms.PasswordInput, max_length=128, label=_("Password (again)*"))
    agree_tos = forms.BooleanField(label=_(agree_tos_label))
    confirmation_uuid = forms.CharField(
        widget=forms.HiddenInput(), required=False)
    org_slug = forms.CharField(widget=forms.HiddenInput(), required=False)
    required_css_class = 'required'

    def clean(self):
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]

        if password1 != password2:
            raise forms.ValidationError(
                _("The two password fields didn't match."))
        try:
            validate_password(password1)
        except ValidationError as err:
            raise forms.ValidationError(err.error_list[0])

        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email', "").strip().lower()

        if email:
            username = self.cleaned_data.get('username')
            if email and User.objects.filter(email=email).exclude(
                    username=username).count():
                raise forms.ValidationError(
                    _('This email address is already registered.'))
            return email

        return email

    def clean_username(self):

        pattern = re.compile(r'^[\w.@+-]+\Z')

        username = self.cleaned_data.get('username').strip().lower()
        if User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError(_('This username is already taken.'))

        if not pattern.match(username):
            message = _('Enter a valid username. This value may contain only English letters, '
                        'numbers, and @/./+/-/_ characters.')
            raise forms.ValidationError(_(message))

        return username

    def clean_first_name(self):
        return self.cleaned_data.get("first_name", "").strip().upper()

    def clean_last_name(self):
        return self.cleaned_data.get("last_name", "").strip().upper()

    def clean_middle_name(self):
        return self.cleaned_data.get("middle_name", "").strip().upper()

    def clean_nickname(self):
        return self.cleaned_data.get("nickname", "").strip().upper()

    def save(self):

        # Save user
        new_user = User.objects.create_user(
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'],
            is_active=True)

        # Save user profile
        up = UserProfile.objects.create(
            user=new_user,
            number_str_include=str(self.cleaned_data.get(
                'birth_date', "")).replace("-", ""),
            nickname=self.cleaned_data.get('nickname', ''),
            middle_name=self.cleaned_data.get('middle_name', ""),
            picture=self.cleaned_data.get('picture'),
            mobile_phone_number=self.cleaned_data['mobile_phone_number'],
            phone_verified=True,
            sex=self.cleaned_data.get('sex', ""),
            birth_date=self.cleaned_data.get('birth_date', ""),
            agree_tos=settings.CURRENT_TOS_VERSION,
            agree_privacy_policy=settings.CURRENT_PP_VERSION)
        up.save()

        # Get the confirmation model object
        idc = IDCardConfirmation.objects.get(
            confirmation_uuid=self.cleaned_data.get('confirmation_uuid', ''))

        # Add IAL2 Evidence
        IdentityAssuranceLevelDocumentation.objects.create(subject_user=new_user,
                                                           id_documentation_verification_method_type='pipp',
                                                           id_verify_description="RealID Scan.",
                                                           pdf417_barcode_parsed=idc.details,
                                                           evidence='ONE-SUPERIOR-OR-STRONG-PLUS')
        # Add the user to the org.
        organization_slug = self.cleaned_data['org_slug']
        org = Organization.objects.get(slug=organization_slug)
        org.members.add(new_user)

        # Delete the IDC record, since its spent.
        idc.delete()

        # Send activated message
        msg = "Your %s account is now active.  You may log in at %s" % (settings.APPLICATION_TITLE,
                                                                        settings.HOSTNAME_URL)
        send_text(up.mobile_phone_number, msg)


class BarcodeForm(forms.Form):
    barcode = forms.CharField(widget=forms.Textarea, label=_("Barcode*"))
    # checked_id = forms.BooleanField(label=_("Checked ID?"),
    #                                 help_text=("""I visually compared the photo ID with
    # the individual in person or by video conference. """))
    org_slug = forms.CharField(
        widget=forms.HiddenInput(), max_length=128, required=True)
    required_css_class = 'required'

    def clean_barcode(self):
        barcode = self.cleaned_data.get('barcode', "")
        if barcode:
            # Parse barcode
            print("clean")
        return barcode

    def parse_barcode(self):
        barcode = self.cleaned_data.get('barcode', "")
        if barcode:
            splitlines = barcode.splitlines()
            for line in splitlines:
                # print("line:", line)
                if line.startswith("ANSI"):
                    print("MAINLINE")
                    mainline = line
                    for l in re.split("\x0a", mainline):
                        print(l)
            # Parse barcode
            print("parse")
        return barcode
