from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import IdentityAssuranceLevelDocumentation


class InPersonIdVerifyForm(forms.ModelForm):

    class Meta:
        model = IdentityAssuranceLevelDocumentation
        fields = ('evidence', 'id_verify_description', 'expires_at')

    def clean_evidence(self):
        evidence = self.cleaned_data["evidence"]
        if not evidence:
            raise forms.ValidationError(
                _("""You must supply information about ID verification evidence"""))
        return evidence

    def clean_id_verify_description(self):
        id_verify_description = self.cleaned_data["id_verify_description"]
        if not id_verify_description:
            raise forms.ValidationError(
                _("""You must describe the ID verification performed."""))
        return id_verify_description


class DowngradeIdentityAssuranceLevelForm(forms.ModelForm):

    class Meta:
        model = IdentityAssuranceLevelDocumentation
        fields = ('id_assurance_downgrade_description', )
