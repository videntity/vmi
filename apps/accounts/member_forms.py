import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, create_activation_key, Organization
from django.conf import settings
from django.utils.safestring import mark_safe
from phonenumber_field.formfields import PhoneNumberField
from .forms import RepresentsPositiveInt
from .models import SEX_CHOICES
from .texts import send_text
from .emails import send_member_verify_request_email

# Copyright Videntity Systems Inc.
YEARS = [x for x in range(1901, 2000)]

User = get_user_model()

agree_tos_label = mark_safe(
    'Do you agree to the <a href="%s">Terms of Service</a> and <a href="%s">Privacy Policy</a>?' % (settings.TOS_URI,
                                                                                                    settings.POLICY_URI))


class MemberSignupForm(forms.Form):
    username = forms.CharField(max_length=30, label=_("Username*"))
    first_name = forms.CharField(max_length=100, label=_("First Name*"))
    last_name = forms.CharField(max_length=100, label=_("Last Name*"))
    middle_name = forms.CharField(
        max_length=100, label=_("Middle Name"), required=False)
    nickname = forms.CharField(
        max_length=100, label=_("Nickname"), required=False)
    birth_date = forms.DateField(label=_('Birth Date*'), widget=forms.SelectDateWidget(years=settings.BIRTHDATE_YEARS),
                                 required=True, help_text="We use this information to help look up your information.")
    sex = forms.ChoiceField(label=_('Sex*'),
                            choices=SEX_CHOICES, required=True,
                            help_text="Enter birth sex. We use this information to help look up your information.")
    picture = forms.ImageField(required=False,
                               help_text=_("""Upload your profile picture."""))

    email = forms.EmailField(max_length=150, label=_("Email"), required=False,
                             help_text=_("""An email email is highly
                                recommended so we may send
                                you important updates on
                                account activity"""))
    mobile_phone_number = PhoneNumberField(required=False, label=_("Mobile Phone Number"),
                                           help_text=_("""An mobile phone number is highly
                                                          recommended so we may send you important
                                                          updates on account activity."""))
    pick_your_account_number = forms.CharField(max_length=10, label=_("Want to Customize Your Account Number?"),
                                               help_text=_("""If you want, pick up to 10 easy-to-remember numbers
                                                           to be included in your account number. If left blank,
                                                           random numbers will be used."""), required=False)
    password1 = forms.CharField(widget=forms.PasswordInput, max_length=128, label=_("Password*"),
                                help_text=_("Passwords must be at least 8 characters and not be too common."))
    password2 = forms.CharField(
        widget=forms.PasswordInput, max_length=128, label=_("Password (again)*"))
    agree_tos = forms.BooleanField(label=_(agree_tos_label))
    org_slug = forms.CharField(
        widget=forms.HiddenInput(), max_length=128, required=True)
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
            sex=self.cleaned_data.get('sex', ""),
            # gender_identity=self.cleaned_data.get('gender_identity', ""),
            # gender_identity_custom_value=self.cleaned_data.get(
            #     'gender_identity_custom_value', ""),
            birth_date=self.cleaned_data.get('birth_date', ""),
            agree_tos=settings.CURRENT_TOS_VERSION,
            agree_privacy_policy=settings.CURRENT_PP_VERSION)
        up.save()

        # Verify Email - Send a verification email
        if self.cleaned_data.get('email'):
            create_activation_key(new_user)

        # Send Welcome Text
        if self.cleaned_data.get('mobile_phone_number'):
            msg = """Hello %s. Welcome to %s and %s.
            As a reminder, your account number is %s and your username is %s.""" % (
                new_user.first_name.title(),
                settings.KILLER_APP_TITLE,
                settings.TOP_LEFT_TITLE,
                up.subject,
                new_user.username)
            send_text(msg, up.mobile_phone_number)

        # Send the organization
        organization_slug = self.cleaned_data['org_slug']
        org = Organization.objects.get(slug=organization_slug)
        for agent in org.users.all():

            send_member_verify_request_email(agent, up, org)
            # print(agent.first_name)

        return new_user
