import logging
from apps.oidc.claims import BaseProvider
from apps.accounts.models import UpstreamIdentityProviderUserAuthenticatorAssurance
logger = logging.getLogger('verifymyidentity_.%s' % __name__)


# Copyright Videntity Systems Inc.
__author__ = "Alan Viars"


class AuthenticatorAssuranceProvider(BaseProvider):

    def claim_aal(self):
        try:
            if self.user:
                upstream_aal = UpstreamIdentityProviderUserAuthenticatorAssurance.objects.filter(user=self.user)
                if upstream_aal:
                    return upstream_aal[0].aal
        except Exception as e:
            print(e)
            logger.debug(e)
            return None

    def claim_amr(self):
        try:
            upsteam = UpstreamIdentityProviderUserAuthenticatorAssurance.objects.filter(user=self.user)
            if upsteam:
                return upsteam[0].amr_list
            else:
                msg = "No upstream Authenticator Assurance record for user %s" % (self.user)
                print(msg)
                logger.debug(msg)
        except Exception as e:
            print(e)
            logger.debug(e)
            return None

    def claim_vot(self):
        # https://tools.ietf.org/html/rfc8485
        try:
            if self.user:
                upstream_aal = UpstreamIdentityProviderUserAuthenticatorAssurance.objects.filter(user=self.user)
                if upstream_aal:
                    vot = self.claims.get("vot", False)
                    if vot:
                        parts = vot.split(".")
                        parts[1] = "C%s" % (upstream_aal[0].aal)
                        return ".".join(parts)
                return None

        except Exception as e:
            print(e)
            logger.debug(e)
            return None


class UpstreamAuthenticatorAssuranceLevel2Provider(BaseProvider):
    """Auto-returns 2"""

    def claim_aal(self):
        return "2"

    def claim_vot(self):
        # https://tools.ietf.org/html/rfc8485

        try:
            if self.user:
                vot = self.claims.get("vot", False)
                if vot:
                    parts = vot.split(".")
                    parts[1] = "C2"
                    return ".".join(parts)
                return None
        except Exception:
            return None


class UpstreamAuthenticatorAssuranceLevel1Provider(BaseProvider):
    """Auto-returns 2"""

    def claim_aal(self):
        return "1"

    def claim_vot(self):
        # https://tools.ietf.org/html/rfc8485

        try:
            if self.user:
                vot = self.claims.get("vot", False)
                if vot:
                    parts = vot.split(".")
                    parts[1] = "C1"
                    return ".".join(parts)
                return None
        except Exception:
            return None
