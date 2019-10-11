import json
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from datetime import date
from collections import OrderedDict
from django.conf import settings

__author__ = "Alan Viars"

ID_DOCUMENT_TYPES = (('idcard', """ID Card"""),
                     ('passport', 'Passport'),
                     ('driving_permit', 'Driving Permit'),
                     ('us_health_insurance_card', 'US Health and Insurance Card'))

ID_DOCUMENTATION_VERIFICATION_METHOD_CHOICES = (("pipp", "Physical In-Person Proofing"),
                                                ("sripp", "Supervised remote In-Person Proofing"),
                                                ("eid", "Online verification of an electronic ID card"),
                                                ("", "Blank"))

EVIDENCE_TYPE_CHOICES = (('id_document', 'Verification based on any kind of government issued identity document'),
                         ('utility_bill', 'Verification based on a utility bill'),
                         ('qes', 'Verification based on a eIDAS Qualified Electronic Signature'))


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
        on_delete=models.PROTECT,
        db_index=True,
        null=True,
        related_name="verifying_user")

    id_documentation_verification_method_type = models.CharField(choices=ID_DOCUMENTATION_VERIFICATION_METHOD_CHOICES,
                                                                 max_length=16,
                                                                 blank=True, default='')

    evidence_type = models.CharField(
        choices=EVIDENCE_TYPE_CHOICES, max_length=64, default='', blank=True)

    claims = models.TextField(help_text="A whitespace delimited list of claims supported by this evidence.",
                              blank=True, default='')

    id_document_type = models.CharField(choices=ID_DOCUMENT_TYPES,
                                        max_length=16,
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
    id_document_issuer_date_of_expiry = models.DateField(blank=True, null=True)

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

    action = models.CharField(
        choices=(
            ('',
             'No Action (Detail Update)'),
            ('1-TO-2',
             'Verify Identity: Change the Identity assurance Level from 1 to 2'),
            ('2-TO-1',
             'Administrative Downgrade: Change the Identity Assurance Level (IAL) from 2 to 1 from IAL 2 to 1.')),
        max_length=6,
        default='',
        blank=False)
    evidence = models.CharField(
        choices=settings.IAL_EVIDENCE_CLASSIFICATIONS,
        max_length=256,
        default='',
        blank=True)

    evidence_subclassification = models.CharField(
        choices=settings.IAL_EVIDENCE_SUBCLASSIFICATIONS,
        max_length=256,
        default='',
        blank=True)

    id_verify_description = models.TextField(blank=True, default='',
                                             help_text="""Describe the evidence given to assure this person's
                                                identity has been verified.""")

    id_assurance_downgrade_description = models.TextField(
        blank=True,
        default='',
        help_text="""Complete this description when downgrading the ID assurance level.""")

    note = models.TextField(
        blank=True,
        null=True,
    )

    metadata = models.TextField(
        blank=True,
        default="""{"subject_user":null, "history":[]}""",
        help_text="JSON Object")

    expires_at = models.DateField(blank=True, null=True)
    verification_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.level

    @property
    def level(self):
        # The Identity assurance level is derived.
        # If there is evidence to support IAL2
        if self.evidence:
            # If the evidence has an expiration
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
        metadata = json.loads(self.metadata, object_pairs_hook=OrderedDict)
        if len(metadata['history']) == 0:
            metadata['subject_user'] = str(self.subject_user)
        # Write the history
        history = OrderedDict()
        history['verifying_user'] = str(self.verifying_user)
        history['actions'] = self.action
        if self.action == "1-TO-2":
            history['id_verify_description'] = self.id_verify_description
        elif self.action == "2-TO-1":
            history[
                'id_assurance_downgrade_description'] = self.id_assurance_downgrade_description
            self.evidence = ''
        history['updated_at'] = str(self.updated_at)
        # append the history
        metadata['history'].append(history)

        if commit:
            self.metadata = json.dumps(metadata)
            super(IdentityAssuranceLevelDocumentation, self).save(**kwargs)

    class Meta:
        permissions = (
            ("can_change_level", "Can change identity assurance level"),)
