import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, create_activation_key, Organization, OrganizationAffiliationRequest
from django.conf import settings
from django.utils.safestring import mark_safe
from phonenumber_field.formfields import PhoneNumberField
from .forms import RepresentsPositiveInt

# Copyright Videntity Systems Inc.
YEARS = [x for x in range(1901, 2000)]

User = get_user_model()

agree_tos_label = mark_safe(
    _('Do you agree to the <a href="%s" target="_blank">Terms of Use</a>?' % (settings.AGENT_TOS_URI)))

# Todo re-ad training URL
# attest_training_completed_label = mark_safe(
#     """Yes, I attest I have completed the <a href="%s" target="_blank">training</a>
#     and will abide by the code of conduct.""" % (settings.TRAINING_URI))

attest_training_completed_label = mark_safe(
    _("""Yes, I attest I have completed the training and will abide by the code of conduct."""))


class StaffSignupForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.REQUIRE_TRAINING_FOR_AGENT_SIGNUP:
            self.fields['attest_training_completed'] = forms.BooleanField(required=True,
                                                                          label=_(attest_training_completed_label))

    # Org Agent Signup Form.
    domain = forms.CharField(disabled=True, max_length=512, required=False,
                             help_text=_("You must register using this email domain."))

    picture = forms.ImageField(required=False,
                               help_text=_("""Upload your profile picture."""))
    username = forms.CharField(max_length=30, label=_("Username*"))
    # pick_your_account_number = forms.CharField(max_length=10, label=_(
    #     "Customize Your Own Account Number"), help_text=_("""Pick up to 10 numbers to be included in your
    #                                            account number. If left blank, random numbers will be used."""),
    #     required=False)
    email = forms.EmailField(max_length=150, label=_("Email*"), required=True)
    mobile_phone_number = PhoneNumberField(required=True, max_length=15,
                                           label=_(
                                               "Mobile Phone Number*"))
    first_name = forms.CharField(max_length=100, label=_("First Name*"))
    last_name = forms.CharField(max_length=100, label=_("Last Name*"))
    middle_name = forms.CharField(
        max_length=100, label=_("Middle Name"), required=False)
    nickname = forms.CharField(
        max_length=100, label=_("Nickname"), required=False)
    password1 = forms.CharField(widget=forms.PasswordInput, max_length=128,
                                label=_("Password*"),
                                help_text=_("Passwords must be at least 8 characters and not be too common."))
    password2 = forms.CharField(widget=forms.PasswordInput, max_length=128,
                                label=_("Password (again)*"))
    agree_tos = forms.BooleanField(label=_(agree_tos_label))
    attest_training_completed = forms.BooleanField(required=True,
                                                   label=_(attest_training_completed_label))
    org_slug = forms.CharField(widget=forms.HiddenInput(),
                               max_length=128, required=True)
    domain = forms.CharField(widget=forms.HiddenInput(),
                             max_length=512, required=False)
    required_css_class = 'required'

    def clean(self):
        org_slug = self.cleaned_data["org_slug"]
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]
        org_slug = self.cleaned_data["org_slug"]
        email = self.cleaned_data.get('email', "")
        org = Organization.objects.get(slug=org_slug)
        domains_to_match = org.domain.split()

        if domains_to_match:
            email_parts = email.split("@")
            # Get the part after the @
            supplied_domain = email_parts[-1]
            if supplied_domain not in domains_to_match:
                raise forms.ValidationError(
                    _("""You must use your
                       company or organization
                       supplied email. Valid domains are %s.""" % (domains_to_match)))

        if password1 != password2:
            raise forms.ValidationError(
                _("The two password fields didn't match."))
        try:
            validate_password(password1)
        except ValidationError as err:
            raise forms.ValidationError(err.error_list[0])

        return self.cleaned_data

    def clean_picture(self):
        picture = self.cleaned_data.get('picture', False)
        if picture:
            if picture.size > int(settings.MAX_PROFILE_PICTURE_SIZE):
                raise ValidationError(_("Image file too large."))
        return picture

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

    def clean_attest_training_completed(self):
        attest_training_completed = self.cleaned_data.get(
            "attest_training_completed", False)
        if settings.REQUIRE_TRAINING_FOR_AGENT_SIGNUP:
            if not attest_training_completed:
                raise forms.ValidationError(
                    _('You must complete the training before completing this form.'))
        return attest_training_completed

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
            is_active=False)

        up = UserProfile.objects.create(
            user=new_user,
            number_str_include=self.cleaned_data.get(
                'pick_your_account_number', ""),
            nickname=self.cleaned_data.get('nickname', ''),
            middle_name=self.cleaned_data.get('middle_name', ""),
            picture=self.cleaned_data.get('picture'),
            mobile_phone_number=self.cleaned_data['mobile_phone_number'],
            agree_tos=settings.CURRENT_TOS_VERSION,
            attest_training_completed=True,
            agree_privacy_policy=settings.CURRENT_PP_VERSION)
        up.save()
        organization_slug = self.cleaned_data['org_slug']
        org = Organization.objects.get(slug=organization_slug)

        OrganizationAffiliationRequest.objects.create(
            organization=org, user=new_user)

        # Verify EmailSend a verification email
        create_activation_key(new_user)
        return new_user
