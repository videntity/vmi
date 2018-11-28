from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.oidc.claims import get_claims_provider
from .models import UserProfile

UserModel = get_user_model()


class ClaimProviderTests(TestCase):

    def setUp(self):
        self.test_user = UserModel.objects.create_user(
            "test_user",
            "test@example.com",
            "123456")
        UserProfile.objects.create(
            user=self.test_user,
            email_verified=True,
        )
        self.dev_user = UserModel.objects.create_user(
            "dev_user",
            "dev@example.com",
            "123456")

    def test_email_verified_claim(self):
        cp = get_claims_provider()(user=self.test_user)
        claims = cp.get_claims()
        self.assertTrue(claims['email_verified'])
