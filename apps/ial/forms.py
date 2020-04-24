from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import IdentityAssuranceLevelDocumentation, ID_DOCUMENTATION_VERIFICATION_METHOD_CHOICES
from django.conf import settings

IAL_EVIDENCE_CLASSIFICATIONS_ID_CARDS = (
    ('ONE-SUPERIOR-OR-STRONG-PLUS-1', "Driver's License"),
    ('ONE-SUPERIOR-OR-STRONG-PLUS-2', "Identification Card"),
    ('ONE-SUPERIOR-OR-STRONG-PLUS-3', 'Health/Insurance Card'),
    ('ONE-SUPERIOR-OR-STRONG-PLUS-4', 'Passport'),
)
#   ('TWO-STRONG-1', """At least two of the following documents: birth certificate,
# Social Security Card, Medicaid card, Medicare Card."""),


EVIDENCE_TYPE_CHOICES = (('id_document', _('Verification based on any kind of government issued identity document')),

                         # Utility bill is not supported at this time.
                         # ('utility_bill', _('Verification based on a utility bill')),
                         )


class SelectVerificationTypeIDCardForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True
            self.fields[field].label = "%s*" % (self.fields[field].label)

        # Set the
        method_choices = []
        if settings.ALLOW_PHYSICAL_INPERSON_PROOFING:
            method_choices.append(("pipp", "Physical In-Person Proofing"))

        if settings.ALLOW_SUPERVISED_REMOTE_INPERSON_PROOFING:
            method_choices.append(
                ("sripp", "Supervised Remote In-Person Proofing"))

        if settings.ALLOW_ONLINE_VERIFICATION_OF_AN_ELECTRONIC_ID_CARD:
            method_choices.append(
                ("eid", "Online verification of an electronic ID card"))

        self.fields[
            'id_documentation_verification_method_type'].choices = method_choices
        self.initial[
            "id_documentation_verification_method_type"] = settings.DEFAULT_PROOFING_METHOD

        self.fields['id_documentation_verification_method_type'].label = _(
            "Method")
        self.fields['evidence_type'].widget = forms.HiddenInput()
        self.fields[
            'evidence'].choices = settings.IAL2_EVIDENCE_CLASSIFICATIONS[3:]
        self.fields['evidence'].label = _("Evidence")

    class Meta:
        model = IdentityAssuranceLevelDocumentation
        fields = ('id_documentation_verification_method_type',
                  'evidence_type', 'evidence')
        required = ('id_documentation_verification_method_type',
                    'evidence_type', 'evidence')


class IDCardForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True
            self.fields[field].label = "%s*" % (self.fields[field].label)
        # Narrow the drop down choices for this form
        self.fields[
            'id_documentation_verification_method_type'].choices = ID_DOCUMENTATION_VERIFICATION_METHOD_CHOICES

        self.fields['id_documentation_verification_method_type'].disabled = True
        self.fields['id_documentation_verification_method_type'].label = _(
            "Method")
        self.fields[
            'id_documentation_verification_method_type'].widget = forms.HiddenInput()
        self.fields['evidence_type'].widget = forms.HiddenInput()
        self.fields['evidence_type'].disabled = True
        self.fields['evidence'].choices = settings.IAL2_EVIDENCE_CLASSIFICATIONS
        self.fields['evidence'].label = _("Evidence")
        self.fields['evidence'].disabled = True

        self.fields['id_document_type'].widget = forms.HiddenInput()
        self.fields['id_document_type'].disabled = True
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
                  'note',
                  )

        required = ('id_documentation_verification_method_type',
                    'evidence_type',
                    'evidence')
