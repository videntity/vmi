from django import forms
from .models import UserProfile
from django.utils.translation import ugettext_lazy as _
from .password_recovery_passphrase_generator import passphrase_hash
from django.contrib.auth import get_user_model
# Copyright Videntity Systems Inc.
__author__ = "Alan Viars"


class RecoverPasswordWithPassphraseForm(forms.Form):
    username = forms.CharField(max_length=150, label=_('Username'),
                               widget=forms.TextInput(attrs={'placeholder': 'Your username*'}))
    passphrase = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Your Passphrase*'}), max_length=512,
                                 label=_('Passphrase*'))
    required_css_class = 'required'

    def clean(self):
        username = self.cleaned_data.get("username", "").strip().lower()
        try:
            User = get_user_model()
            user = User.objects.get(username=username)
            up = UserProfile.objects.get(user=user)
        except User.DoesNotExist:
            raise forms.ValidationError(_('User not found.'))
        except UserProfile.DoesNotExist:
            raise forms.ValidationError(_('UserProfile not found.'))

        passphrase = self.cleaned_data.get("passphrase", "").strip().lower()
        passphrase_hashed = passphrase_hash(passphrase)
        if passphrase_hashed != up.password_recovery_passphrase_hash:
            raise forms.ValidationError(_('The passphrase does not match.'))
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip().lower()
        try:
            User = get_user_model()
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(_('User not found.'))
        return username

    def clean_passphrase(self):
        passphrase = self.cleaned_data.get("passphrase", "").strip().lower()
        return " ".join(passphrase.split())
