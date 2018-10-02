from oauth2_provider.models import AbstractGrant
from django.db import models


class Grant(AbstractGrant):
    nonce = models.CharField(
        max_length=255,
        default=None,
        blank=True,
        null=True)

    class Meta(AbstractGrant.Meta):
        swappable = "OAUTH2_PROVIDER_GRANT_MODEL"
