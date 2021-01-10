from apps.oidc.claims import BaseProvider
from .backend import has_sms_device


class AuthenticatorAssuranceProvider(BaseProvider):

    def claim_aal(self):
        try:
            # we can say that if a user has a device
            # it was used durring authentication as
            # that is currently enforced. This may not
            # hold up if changes are made to the authentication
            # flow of the system.
            if has_sms_device(self.user):
                return "2"
        except Exception:
            return None

    def claim_amr(self):
        try:
            # we can say that if a user has a device
            # it was used durring authentication as
            # that is currently enforced. This may not
            # hold up if changes are made to the authentication
            # flow of the system.
            if has_sms_device(self.user):
                return ["pwd", "sms", ]
        except Exception:
            return None

    def claim_vot(self):
        # https://tools.ietf.org/html/rfc8485#appendix-A.2
        # Ce could also be Cf
        try:
            # we can say that if a user has a device
            # it was used durring authentication as
            # that is currently enforced. This may not
            # hold up if changes are made to the authentication
            # flow of the system.
            if has_sms_device(self.user):
                vot = self.claims.get("vot", False)
                if vot:
                    parts = vot.split(".")
                    parts[1] = "C2"
                    return ".".join(parts)
                return None
        except Exception:
            return None
