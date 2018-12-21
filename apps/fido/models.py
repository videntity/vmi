from django.db import models
from django.conf import settings
from fido2 import cose, cbor


class AttestedCredentialData(models.Model):
    aaguid = models.BinaryField()
    _credential_id = models.BinaryField(db_column='credential_id')
    _public_key = models.BinaryField(db_column='public_key')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    @property
    def credential_id(self):
        return bytes(self._credential_id)

    @credential_id.setter
    def credential_id(self, value):
        self._credential_id = value

    @property
    def public_key(self):
        return cose.CoseKey.parse(cbor.loads(bytes(self._public_key))[0])

    @public_key.setter
    def public_key(self, value):
        self._public_key = value
