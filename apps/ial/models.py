import uuid
from django.db import models
from django.contrib.auth import get_user_model
from datetime import date
from collections import OrderedDict
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
__author__ = "Alan Viars"

ID_DOCUMENT_TYPES = (('driving_permit', 'Driving License'),
                     ('idcard', """ID Card"""),
                     ('passport', 'Passport'),
                     ('us_health_insurance_card', 'US Health and Insurance Card'))

ID_DOCUMENTATION_VERIFICATION_METHOD_CHOICES = (("pipp", "Physical In-Person Proofing"),
                                                ("sripp", "Supervised Remote In-Person Proofing"),
                                                ("eid", "Online verification of an electronic ID card"))

EVIDENCE_TYPE_CHOICES = (('id_document', _('Verification based on any kind of government issued identity document')),
                         ('utility_bill', _('Verification based on a utility bill'))
                         )


class IdentityAssuranceLevelDocumentation(models.Model):

    """This model is based on NIST SP 800-63-3 Part A
    https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63a.pdf
    # Evidence classifications are defined/customizable in settings.
    """
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)
    subject_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        db_index=True,
        related_name="subject_user")

    verifying_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        db_index=True,
        null=True,
        related_name="verifying_user",
        blank=True)

    id_documentation_verification_method_type = models.CharField(choices=ID_DOCUMENTATION_VERIFICATION_METHOD_CHOICES,
                                                                 max_length=16,
                                                                 blank=True, default='pipp')

    evidence_type = models.CharField(
        choices=EVIDENCE_TYPE_CHOICES, max_length=64, default='id_document', blank=True)

    claims = models.TextField(help_text=_("A whitespace delimited list of claims supported by this evidence."),
                              blank=True, default='')

    id_document_type = models.CharField(choices=ID_DOCUMENT_TYPES,
                                        max_length=128,
                                        blank=True, default='')

    id_document_issuer_name = models.CharField(
        max_length=250, blank=True, default='')
    id_document_issuer_country = models.CharField(max_length=2, blank=True,
                                                  default=settings.DEFAULT_COUNTRY_CODE_FOR_INDIVIDUAL_IDENTIFIERS)
    id_document_issuer_region = models.CharField(
        max_length=2, blank=True, default='')
    id_document_issuer_number = models.CharField(
        max_length=250, blank=True, default='')
    id_document_issuer_date_of_issuance = models.DateField(
        blank=True, null=True)
    id_document_issuer_date_of_expiry = models.DateField(blank=True, null=True,
                                                         help_text=_("The date the ID document expires."))

    utility_bill_provider_name = models.CharField(
        max_length=250, blank=True, default='')
    utility_bill_provider_street_address = models.CharField(
        max_length=250, blank=True, default='')
    utility_bill_provider_locality = models.CharField(
        max_length=250, blank=True, default='')
    utility_bill_provider_region = models.CharField(
        max_length=2, blank=True, default='')
    utility_bill_provider_postal_code = models.CharField(
        max_length=20, blank=True, default='')
    utility_bill_provider_country = models.CharField(max_length=2, blank=True,
                                                     default=settings.DEFAULT_COUNTRY_CODE_FOR_INDIVIDUAL_IDENTIFIERS)
    evidence = models.CharField(verbose_name=_('Identity Assurance Level 2 Classification'),
                                choices=settings.IAL2_EVIDENCE_CLASSIFICATIONS[3:],
                                max_length=256,
                                default='',
                                blank=True)

    id_verify_description = models.TextField(blank=True, default='',
                                             help_text=_("""Describe the evidence given to assure this person's
                                                identity has been verified."""))

    note = models.TextField(
        blank=True,
        null=True,
        help_text=_("Add any notes or secondary card information here."))

    expires_at = models.DateField(verbose_name="Invalidate Identity Assurance Date",
                                  blank=True, null=True,
                                  help_text=_("""If left blank, the Identity Assurance Level
                                              of 2 will remain in effect indefinitely."""))
    verification_date = models.DateField(blank=True, null=True)

    front_of_id_card = models.ImageField(
        upload_to='identity_documents/', null=True, blank=True)

    back_of_id_card = models.ImageField(
        upload_to='identity_documents/', null=True, blank=True)

    pdf417_barcode = models.ImageField(
        upload_to='identity_documents/', null=True, blank=True,
        verbose_name="Image of the barcode on the back of the driver's license.")

    pdf417_barcode_parsed = models.TextField(
        blank=True,
        default="",
        help_text="The extracted parsed text content from the pdf417_barcode.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.level

    @property
    def short_description(self):
        # The Identity Assurance Level is derived.
        # If evidence exists to support IAL2
        desc = "%s of %s." % (self.get_id_documentation_verification_method_type_display(),
                              self.get_evidence_display(),)
        if self.verifying_user:
            verified_by = " Verified by %s %s." % (
                self.verifying_user.first_name, self.verifying_user.last_name)
        else:
            verified_by = ""
        return "%s%s" % (desc, verified_by)

    @property
    def level(self):
        # The Identity Assurance Level is derived.
        # If evidence exists to support IAL2
        if self.evidence:
            if self.expires_at:
                # if the evidence is expired
                if date.today() > self.expires_at:
                    return str(1)
            return str(2)
        # The default level is 1
        return str(1)

    @property
    def oidc_ia_evidence(self):

        od = OrderedDict()
        od['type'] = self.evidence_type
        od['method'] = self.id_documentation_verification_method_type
        if od['type'] == "id_document":
            od['document'] = OrderedDict()
            od['document']['type'] = self.id_document_type
            od['document']['issuer'] = OrderedDict()
            od['document']['issuer']['name'] = self.id_document_issuer_name
            od['document']['issuer']['country'] = self.id_document_issuer_country
            od['document']['issuer']['region'] = self.id_document_issuer_region
            od['document']['number'] = self.id_document_issuer_number
            od['document']['date_of_issuance'] = str(
                self.id_document_issuer_date_of_issuance)
            od['document']['date_of_expiry'] = str(
                self.id_document_issuer_date_of_expiry)

        if od['type'] == "utility_bill":
            od['provider'] = OrderedDict()
            od['provider']['name'] = self.utility_bill_provider_name
            od['provider']['country'] = self.utility_bill_provider_country
            od['provider']['region'] = self.utility_bill_provider_region
            od['date'] = str(self.verification_date)

        return od

    def save(self, commit=True, **kwargs):
        if commit:
            if not self.id_verify_description:
                self.id_verify_description = self.short_description

            super(IdentityAssuranceLevelDocumentation, self).save(**kwargs)

    class Meta:
        permissions = (
            ("can_change_level", "Can change identity assurance level"),)
