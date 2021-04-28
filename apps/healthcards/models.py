import logging
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django.conf import settings
from django.db.models import CASCADE
import json
from django.contrib.auth import get_user_model
from shc.generate_random_jwks import (generate_signing_key, generate_encryption_key, generate_keyset)
from shc.utils import (encode_to_numeric, SMART_HEALTH_CARD_PREFIX, encode_vc)
import qrcode
import uuid
from django.urls import reverse
from io import BytesIO
from django.core.files import File
from ..accounts.models import Organization
from collections import OrderedDict

__author__ = "Alan Viars"

logger = logging.getLogger(__name__)

User = get_user_model()


class SmartHealthJWKS(models.Model):
    organization = models.ForeignKey(Organization, on_delete=CASCADE, blank=True, null=True)
    nickname = models.CharField(max_length=255, default='')
    kid = models.CharField(max_length=255, default='', blank=True, editable=False,
                           help_text=_('The Key ID for the public/private keys. This is often an FQDN.'))
    public_keys = models.TextField(blank=True, default='')
    private_keys = models.TextField(blank=True, default='')

    def __str__(self):
        return self.nickname

    def save(self, commit=True, **kwargs):

        if commit:
            if not self.kid:
                private_signing_key = generate_signing_key()
                private_encryption_key = generate_encryption_key()
                keyset = generate_keyset([private_signing_key, private_encryption_key])

                pvks = keyset.export(private_keys=True, as_dict=True)
                sig_only = {"keys": []}
                for pv in pvks['keys']:
                    if pv['use'] == 'sig':
                        sig_only['keys'].append(pv)
                self.private_keys = json.dumps(sig_only, indent=4)
                # self.private_keys =  json.dumps(keyset.export(private_keys=True, as_dict=True), indent=4)
                self.public_keys = json.dumps(keyset.export(private_keys=False, as_dict=True), indent=4)

                pks = keyset.export(private_keys=False, as_dict=True)
                pub_sig_only = {"keys": []}
                for pk in pks['keys']:
                    if pk['use'] == 'sig':
                        pub_sig_only['keys'].append(pk)
                self.public_keys = json.dumps(pub_sig_only, indent=4)
                self.kid = keyset.export(private_keys=False, as_dict=True)['keys'][0]['kid']
            if not self.nickname:
                self.nickname = self.organization.slug

            super(SmartHealthJWKS, self).save(**kwargs)

    @property
    def as_jwks(self):
        return json.loads(self.public_keys)


class SmartHealthCard(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, blank=True, null=True)
    name = models.CharField(max_length=512, blank=True, null=True)
    groups = models.ForeignKey(Group, on_delete=CASCADE, blank=True, null=True)
    payload = models.TextField(max_length=4096, blank=True, default='')
    shc_jws = models.TextField(max_length=4096, blank=True, default='')
    qrcode = models.ImageField(upload_to='qr_codes', blank=True, null=True)
    shc_qrcode = models.ImageField(upload_to='shc_qr_codes', blank=True, null=True)
    description = models.TextField(max_length=2048, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Smart Health Card for %s" % (self.user)

    # @property
    # def get_absolute_url(self):
    #    return "" % (reverse('events.views.details', args=[str(self.id)])

    @property
    def payload_dict(self):
        return json.loads(self.payload, object_pairs_hook=OrderedDict)

    @property
    def human_readable_vax_info(self):
        result = ""
        payload_dict = self.payload_dict
        for r in payload_dict['vc']['credentialSubject']['fhirBundle']['entry']:
            if r['resource']['resourceType'] == 'Patient':
                result = "%s %s, with the birthday %s, received the following Immunizations: " % (r['resource']['name'][0]['given'][0],
                                                                                                  r['resource']['name'][0]['family'],
                                                                                                  r['resource']['birthDate'])
            vaccine = ""
            if r['resource']['resourceType'] == 'Immunization':
                if r['resource']['vaccineCode']['coding'][0]['system'] == "http://hl7.org/fhir/sid/cvx" and \
                   r['resource']['vaccineCode']['coding'][0]['code'] == "207":
                    vaccine = "COVID-19"

                result += "%s %s immunization on %s by %s (Lot #%s).\n" % (r['resource']['status'].title(),
                                                                           vaccine,
                                                                           r['resource']['occurrenceDateTime'],
                                                                           r['resource']['performer'][0]['actor']['display'],
                                                                           r['resource']['lotNumber'])
        return result

    def save(self, commit=True, *args,  **kwargs):
        # Create a URL
        url = "%s%s" % (settings.HOSTNAME_URL, reverse('shc_psi', args=[str(self.user.userprofile.sub)]))
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=0)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image()
        buffer = BytesIO()
        img.save(buffer)
        filename = 'psi-%s-%s.png' % (self.user.userprofile.sub, uuid.uuid4())
        self.qrcode.save(filename, File(buffer), save=False)

        # If the data is prsent, but the QR code does not exist.
        if self.payload and not self.shc_qrcode:
            # print("Generate the SMC!")
            shc_jwks = SmartHealthJWKS.objects.all()[0]
            private_keys = json.loads(shc_jwks.private_keys)
            # print(encode_vc(self.payload, private_keys['keys'][0], shc_jwks.kid))
            numeric_encoded_payload = encode_to_numeric(
            encode_vc(json.loads(self.payload), private_keys['keys'][0], private_keys['keys'][0]['kid']))

            # print(numeric_encoded_payload)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=6,
                border=0)
            qr.add_data(SMART_HEALTH_CARD_PREFIX)
            qr.add_data(numeric_encoded_payload)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer)
            filename = 'shc-%s-%s.png' % (self.user.userprofile.sub, uuid.uuid4())
            self.shc_qrcode.save(filename, File(buffer), save=False)
        if commit:
            super().save(*args, **kwargs)
