from apps.oidc.claims import BaseProvider


class AddressClaimProvider(BaseProvider):

    def claim_address(self):
        try:
            return self.user.userprofile.address
        except Exception:
            return None


class IdentifierClaimProvider(BaseProvider):

    def claim_document(self):
        try:
            return self.user.userprofile.doc
        except Exception:
            return None


class OrganizationAgentClaimProvider(BaseProvider):

    def claim_organization_agent(self):
        try:
            return self.user.userprofile.organization_agent
        except Exception:
            return None


# TODO
class MemberClaimProvider(BaseProvider):

    def claim_member(self):
        try:
            return self.user.userprofile.organization_membership
        except Exception:
            return None


class VerifiedPersonDataClaimProvider(BaseProvider):

    def claim_verified_person_data(self):
        try:
            return self.user.userprofile.verified_person_data
        except Exception:
            return None


class UserProfileClaimProvider(BaseProvider):

    def claim_sub(self):
        """"This claim is MANDATORY"""
        try:
            return self.user.userprofile.subject
        except Exception:
            return None

    def claim_given_name(self):
        try:
            return self.user.userprofile.given_name
        except Exception:
            return None

    def claim_family_name(self):
        try:
            return self.user.userprofile.family_name
        except Exception:
            return None

    def claim_name(self):
        try:
            return "%s %s" % (self.user.userprofile.given_name,
                              self.user.userprofile.family_name)
        except Exception:
            return None

    def claim_preferred_username(self):
        try:
            return self.user.username
        except Exception:
            return None

    def claim_nickname(self):
        try:
            return self.user.userprofile.nickname
        except Exception:
            return None

    def claim_gender(self):
        try:
            gender = self.user.userprofile.sex
            if gender == "male":
                return "male"
            if gender == "female":
                return "female"
        except Exception:
            return None

    def claim_birthdate(self):
        try:
            return str(self.user.userprofile.birthdate)
        except Exception:
            return None

    def claim_email_verified(self):
        try:
            return self.user.userprofile.email_verified
        except Exception:
            return None

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

    def claim_aal(self):
        try:
            return self.user.userprofile.aal
        except Exception:
            return None

    def claim_ial(self):
        try:
            return self.user.userprofile.ial
        except Exception:
            return None

    def claim_vot(self):
        try:
            return self.user.userprofile.vot
        except Exception:
            return None

    def claim_profile(self):
        try:
            return self.user.userprofile.profile
        except Exception:
            return None

    def claim_picture(self):
        try:
            return self.user.userprofile.picture_url
        except Exception:
            return None

    def claim_website(self):
        try:
            return self.user.userprofile.website
        except Exception:
            return None


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
