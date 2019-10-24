from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import IdentityAssuranceLevelDocumentation, ID_DOCUMENTATION_VERIFICATION_METHOD_CHOICES


class InPersonIdVerifyForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True
            self.fields[field].label = "%s*" % (self.fields[field].label)
        # NArrow the drop down choices for this form
        self.fields[
            'id_documentation_verification_method_type'].choices = ID_DOCUMENTATION_VERIFICATION_METHOD_CHOICES[0:3]
        self.fields['evidence'].choices = (('ONE-SUPERIOR-OR-STRONG+', 'One Superior or Strong+ pieces of identity evidence'),
                                           ('ONE-STRONG-TWO-FAIR',
                                            'One Strong and Two Fair pieces of identity evidence'),
                                           ('TWO-STRONG',
                                            'Two Pieces of Strong identity evidence'),
                                           ('TRUSTED-REFEREE-VOUCH',
                                            'I am a Trusted Referee Vouching for this person'),
                                           # ('KBA','Knowledged-Based Identity Verification')
                                           )

    class Meta:
        model = IdentityAssuranceLevelDocumentation
        fields = ('id_documentation_verification_method_type',
                  'evidence_type',
                  'evidence',
                  'expires_at',
                  'id_document_type',
                  'id_document_issuer_name',
                  'id_document_issuer_country',
                  'id_document_issuer_region',
                  'id_document_issuer_number',
                  'id_document_issuer_date_of_issuance',
                  'id_document_issuer_date_of_expiry',
                  'utility_bill_provider_name',
                  'utility_bill_provider_street_address',
                  'utility_bill_provider_locality',
                  'utility_bill_provider_region',
                  'utility_bill_provider_postal_code',
                  'utility_bill_provider_country',)

        required = ('id_documentation_verification_method_type',
                    'evidence_type',
                    'evidence')

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
