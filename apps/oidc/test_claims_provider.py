from django.test import TestCase
from django.contrib.auth import get_user_model
from .claims import DefaultProvider

UserModel = get_user_model()


class ClaimProviderTests(TestCase):

    def setUp(self):
        self.test_user = UserModel.objects.create_user(
            "test_user",
            "test@example.com",
            "123456")
        self.dev_user = UserModel.objects.create_user(
            "dev_user",
            "dev@example.com",
            "123456")

    def test_get_claims(self):
        cp = DefaultProvider(user=self.test_user)
        claims = cp.get_claims()
        self.assertEqual(claims['email'], "test@example.com")
