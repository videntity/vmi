from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.oidc.claims import get_claims_provider
from apps.accounts.models import UserProfile
from .models import AttestedCredentialData

UserModel = get_user_model()


class ClaimProviderTests(TestCase):

    def setUp(self):
        self.test_user = UserModel.objects.create_user(
            "test_user",
            "test@example.com",
            "123456")
        UserProfile.objects.create(
            user=self.test_user)

        self.dev_user = UserModel.objects.create_user(
            "dev_user",
            "dev@example.com",
            "123456")
        AttestedCredentialData.objects.create(
            user=self.dev_user)
        UserProfile.objects.create(
            user=self.dev_user)

    def test_get_claims(self):
        cp = get_claims_provider()(user=self.dev_user)
        claims = cp.get_claims()
        self.assertEqual(claims["email"], "dev@example.com")
        self.assertEqual(claims['vot'], "P0.Ce")
        self.assertEqual(claims['aal'], "2")

    def test_get_claims_no_change(self):
        cp = get_claims_provider()(user=self.test_user)
        claims = cp.get_claims()
        self.assertEqual(claims["email"], "test@example.com")
        self.assertEqual(claims['vot'], "P0.Cc")
        self.assertEqual(claims['aal'], "1")
