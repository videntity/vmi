from apps.oidc.claims import BaseProvider


class SubjectClaimProvider(BaseProvider):
    """"This claim is MANDATORY"""

    def claim_sub(self):
        try:
            return self.user.userprofile.subject
        except Exception:
            return None


class EmailVerifiedClaimProvider(BaseProvider):

    def claim_email_verified(self):
        try:
            return self.user.userprofile.email_verified
        except Exception:
            return None


class IdentityAssuranceLevelClaimProvider(BaseProvider):

    def claim_ial(self):
        try:
            return self.user.userprofile.ial
        except Exception:
            return None


class AuthenticatorAssuranceLevelClaimProvider(BaseProvider):

    def claim_aal(self):
        try:
            return self.user.userprofile.aal
        except Exception:
            return None


class VectorsOfTrustClaimProvider(BaseProvider):

    def claim_vot(self):
        try:
            return self.user.userprofile.vot
        except Exception:
            return None


class PhoneNumberClaimProvider(BaseProvider):

    def claim_phone_number(self):
        try:
            return self.user.userprofile.phone_number
        except Exception:
            return None

    def claim_phone_verified(self):
        try:
            return self.user.userprofile.phone_verified
        except Exception:
            return None
