from apps.oidc.claims import BaseProvider
from django.conf import settings


# For address Claim
class AddressClaimProvider(BaseProvider):

    def claim_address(self):
        try:
            return self.user.userprofile.address
        except Exception:
            return None

# For amr Claim


class AMRClaimProvider(BaseProvider):

    def claim_amr(self):
        return ["pwd", ]

# For document claim. For paper and electronic identifiers.
# Passports, URL pointers, Master Patient IDs, SSN, etc.


class IdentifierClaimProvider(BaseProvider):

    def claim_document(self):
        try:
            return self.user.userprofile.doc
        except Exception:
            return None


# For adding agent_to_organuization claim (e.g. "employee of", etc.)
class AgentToOrganizationClaimProvider(BaseProvider):

    def claim_agent_to_organization(self):
        try:
            return self.user.userprofile.agent_to_organization
        except Exception:
            return None


# Reserved for future versions
class AgentToMemberClaimProvider(BaseProvider):

    def claim_agent_to_member(self):
        try:
            return self.user.userprofile.agent_to_member
        except Exception:
            return None

# Reserved for future versions


# Member to
class MemberToOrganizationClaimProvider(BaseProvider):

    def claim_member_to_organization(self):
        try:
            return self.user.userprofile.member_to_organization
        except Exception:
            return None


# Identity Assurance for OIDC.
class VerifiedPersonDataClaimProvider(BaseProvider):

    def claim_verified_claims(self):
        try:
            return self.user.userprofile.verified_claims
        except Exception as e:
            print(e)
            return None


class ExtendedGenderClaimProvider(BaseProvider):

    def claim_gender_identity_custom_value(self):
        try:
            return self.user.userprofile.gender_identity_custom_value
        except Exception:
            return None

    def claim_gender_identity(self):
        try:
            return self.user.userprofile.gender_identity
        except Exception:
            return None


# Contains most of the basic claims
class UserProfileClaimProvider(BaseProvider):

    def claim_sub(self):
        """"This claim is MANDATORY"""
        try:
            return self.user.userprofile.subject
        except Exception:
            return None

    def claim_given_name(self):
        try:
            return self.user.userprofile.given_name.title()
        except Exception:
            return None

    def claim_family_name(self):
        try:
            return self.user.userprofile.family_name.title()
        except Exception:
            return None

    def claim_middle_name(self):
        try:
            return self.user.userprofile.middle_name.title()
        except Exception:
            return None

    def claim_name(self):
        try:
            return "%s %s" % (self.user.userprofile.given_name.title(),
                              self.user.userprofile.family_name.title())
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

    # TO DO Remove or revise this claim ? It will break things.
    def claim_gender(self):
        try:
            gender = self.user.userprofile.sex
            if gender == "male":
                return "male"
            if gender == "female":
                return "female"
        except Exception:
            return ""
    # Downstream health / vital statistics should rely on this claim

    def claim_sex(self):
        try:
            return self.user.userprofile.sex
        except Exception:
            return ""

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

    def claim_website(self):
        try:
            return self.user.userprofile.website
        except Exception:
            return None

    def claim_profile(self):
        try:
            return self.user.userprofile.profile_url
        except Exception:
            return None

    def claim_picture(self):
        try:
            return self.user.userprofile.picture_url
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

    def claim_vtm(self):
        try:
            return settings.VECTORS_OF_TRUST_TRUSTMARK_URL
        except Exception:
            return None

    def claim_verifying_agent_email(self):
        try:
            return self.user.userprofile.verifying_agent_email
        except Exception:
            return None


class SubjectClaimProvider(BaseProvider):
    """"This claim is Mandatory"""

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


# Deprecated - Use AgentToOrganizationClaimProvider instead
class OrganizationAgentClaimProvider(BaseProvider):

    def claim_organization_agent(self):
        try:
            return self.user.userprofile.organization_agent
        except Exception:
            return None


# Deprecated - Use MemberToOrganizationClaimProvider
class MembershipClaimProvider(BaseProvider):

    def claim_memberships(self):
        try:
            return self.user.userprofile.memberships
        except Exception:
            return None
