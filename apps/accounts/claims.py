from apps.oidc.claims import BaseProvider


class UserProfileClaimProvider(BaseProvider):

    def claim_email_verified(self):
        try:
            return self.user.userprofile.email_verified
        except Exception:
            return None

    def claim_sub(self):
        try:
            return self.user.userprofile.subject
        except Exception:
            return None
