from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import IdentityAssuranceLevelDocumentation, ID_DOCUMENTATION_VERIFICATION_METHOD_CHOICES
from django.conf import settings

IAL_EVIDENCE_CLASSIFICATIONS = [
    ('ONE-SUPERIOR-OR-STRONG+', "Valid New York State Driver's License"),
    ('ONE-SUPERIOR-OR-STRONG+', 'Valid New York State Identification Card'),
    ('ONE-SUPERIOR-OR-STRONG+', 'New York State Medicaid ID'),
    ('ONE-SUPERIOR-OR-STRONG+', 'Valid Medicare ID Card'),
    ('ONE-SUPERIOR-OR-STRONG+', 'Valid US Passport'),
    ('ONE-SUPERIOR-OR-STRONG+', 'Valid Veteran ID Card'),
    ('TWO-STRONG', 'Original Birth Certificate and a Social Security Card'),
    ('TRUSTED-REFEREE-VOUCH', 'I am a Trusted Referee Vouching for this person'),
]


class InPersonIdVerifyForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True
            self.fields[field].label = "%s*" % (self.fields[field].label)
        # Narrow the drop down choices for this form
        self.fields[
            'id_documentation_verification_method_type'].choices = ID_DOCUMENTATION_VERIFICATION_METHOD_CHOICES[0:3]
        self.fields['evidence'].choices = IAL_EVIDENCE_CLASSIFICATIONS
        self.fields['expires_at'].widget = forms.SelectDateWidget()
        self.fields['id_document_issuer_date_of_issuance'].widget = forms.SelectDateWidget(
            years=settings.ID_DOCUMENT_ISSUANCE_YEARS)
        self.fields[
            'id_document_issuer_date_of_expiry'].widget = forms.SelectDateWidget()

    class Meta:
        model = IdentityAssuranceLevelDocumentation
        fields = ('id_documentation_verification_method_type',
                  'evidence_type',
                  'evidence',
                  'id_document_type',
                  'id_document_issuer_name',
                  'id_document_issuer_country',
                  'id_document_issuer_region',
                  'id_document_issuer_number',
                  'id_document_issuer_date_of_issuance',
                  'id_document_issuer_date_of_expiry',
                  'expires_at',
                  'front_of_id_card',
                  'back_of_id_card',
                  'pdf417_barcode',
                  # 'utility_bill_provider_name',
                  # 'utility_bill_provider_street_address',
                  # 'utility_bill_provider_locality',
                  # 'utility_bill_provider_region',
                  # 'utility_bill_provider_postal_code',
                  # 'utility_bill_provider_country',
                  )

        required = ('id_documentation_verification_method_type',
                    'evidence_type',
                    'evidence')

    def clean_evidence(self):
        evidence = self.cleaned_data["evidence"]
        if not evidence:
            raise forms.ValidationError(
                _("""You must supply information about ID verification evidence."""))
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
