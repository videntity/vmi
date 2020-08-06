from django.test.client import Client
from django.test import TestCase
from django.urls import reverse


class ClientApiOIDCDiscoveryTest(TestCase):
    """
    Test the OIDC Discovery Endpoint
    Public URIs
    """

    def setUp(self):
        self.client = Client()

    def test_get_oidc_discovery(self):
        """
        Test get oidc discovery
        """
        response = self.client.get(reverse('openid-configuration'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "userinfo_endpoint")
        self.assertContains(response, "jwks_uri")
