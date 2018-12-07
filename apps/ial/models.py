from django.db import models
from django.contrib.auth import get_user_model
from datetime import date
import json
from collections import OrderedDict

__author__ = "Alan Viars"


class IdentityAssuranceLevelDocumentation(models.Model):

    """This model is based on NIST SP 800-63-3 Part A
    https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63a.pdf
    """
    subject_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        db_index=True,
        related_name="subject_user")
    verifying_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        db_index=True,
        null=True,
        related_name="verifying_user")
    identity_proofing_mode = models.CharField(choices=(
        ('R', 'Remote'), ('I', 'In-Person'), ('', 'None')), max_length=1, default='')
    action = models.CharField(
        choices=(
            ('',
             'No Action (Detail Update)'),
            ('1-TO-2',
             'Verify Identity: Change the Identity assurance Level from 1 to 2'),
            ('2-TO-1',
             'Administrative downgrade: Change the Identity Assurance Level (IAL) from 2 to 1 from IAL 2 to 1.')),
        max_length=6,
        default='',
        blank=False)
    evidence = models.CharField(
        choices=(
            ('',
             'None'),
            ('ONE-SUPERIOR-OR-STRONG+',
             'One Superior or Strong+ pieces of identity evidence'),
            ('ONE-STRONG-TWO-FAIR',
             'One Strong and Two Fair pieces of identity evidence'),
            ('TWO-STRONG',
             'Two Pieces of Strong identity evidence'),
            ('TRUSTED-REFEREE-VOUCH',
             'I am a Trusted Referee Vouching for this person'),
            ('KBA',
             'Knowledged-Based Identity Verification')),
        max_length=24,
        default='',
        blank=True)

    id_verify_description = models.TextField(blank=True, default='',
                                             help_text="""Describe the evidence given to assure this person's
                                                identity has been verified.""")

    id_assurance_downgrade_description = models.TextField(
        blank=True,
        default='',
        help_text="""Complete this description when downgrading the ID assurance level.""")

    metadata = models.TextField(
        blank=True,
        default="""{"subject_user":null, "history":[]}""",
        help_text="JSON Object")

    # type is be some enumerated\codified list.
    type = models.CharField(max_length=16, blank=True, default='')
    expires_at = models.DateField(blank=True, null=True)
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
