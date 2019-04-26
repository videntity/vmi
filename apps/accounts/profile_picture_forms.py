from django import forms
from .models import UserProfile
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

# Copyright Videntity Systems Inc.


class ProfilePictureForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('picture',)

    def clean_picture(self):
        picture = self.cleaned_data.get('picture', False)
        if picture:
            if picture.size > int(settings.MAX_PROFILE_PICTURE_SIZE):
                raise ValidationError(_("Image file too large."))
            return picture
        else:
            raise ValidationError(_("Couldn't read uploaded image"))

    required_css_class = 'required'
