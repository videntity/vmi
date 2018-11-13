from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, create_activation_key, Organization

# Copyright Videntity Systems Inc.

User = get_user_model()


class StaffSignupForm(forms.Form):
    registration_code = forms.CharField(max_length=100,
                                        label=_("Registration Phrase"))
    email = forms.EmailField(max_length=75, label=_("Email"), required=True)
    first_name = forms.CharField(max_length=100, label=_("First Name"))
    last_name = forms.CharField(max_length=100, label=_("Last Name"))
    username = forms.CharField(max_length=30, label=_("User name"))
    mobile_phone_number = forms.CharField(required=True,
                                          label=_("Mobile Phone Number"),
                                          max_length=10)
    password1 = forms.CharField(widget=forms.PasswordInput, max_length=128,
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput, max_length=128,
                                label=_("Password (again)"))
    org_slug = forms.CharField(widget=forms.HiddenInput(),
                               max_length=128, required=True)

    required_css_class = 'required'

    def clean(self):
        org_slug = self.cleaned_data["org_slug"]
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]
        org_slug = self.cleaned_data["org_slug"]
        registration_code = self.cleaned_data.get('registration_code', "")
        email = self.cleaned_data.get('email', "")
        org = Organization.objects.get(slug=org_slug)
        if org.registration_code != registration_code:
            raise forms.ValidationError(_('Invalid registration code.'))

        domain_to_match = org.domain
        if domain_to_match:
            print("ORG DOMAIN", email, email.split())
            user, supplied_domain = email.split("@")
            if supplied_domain != domain_to_match:
                raise forms.ValidationError(
                    _("""You must user your
                       company or organization
                       supplied email."""))

        if password1 != password2:
            raise forms.ValidationError(
                _("The two password fields didn't match."))
        try:
            validate_password(password1)
        except ValidationError as err:
            raise forms.ValidationError(err.error_list[0])

        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email', "")
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
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError(_('This username is already taken.'))
        return username

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
            mobile_phone_number=self.cleaned_data['mobile_phone_number'],
        )

        organization_slug = self.cleaned_data['org_slug']
        org = Organization.objects.get(slug=organization_slug)
        up.organizations.add(org)
        up.save()
        # Need to add user groups here.
        # group = Group.objects.get(name='BlueButton')
        # new_user.groups.add(group)

        # Send a verification email
        create_activation_key(new_user)
        return new_user
