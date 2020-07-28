from django.test.client import Client
from django.test import TestCase
from django.urls import reverse
from unittest import skipIf
from django.conf import settings
import requests


def fhir_server_unreachable():
    try:
        requests.get(settings.DEFAULT_FHIR_SERVER, timeout=2)
        return False
    except requests.exceptions.ConnectionError:
        return True


@skipIf(fhir_server_unreachable(), "Can't reach external sites.")
class ClientApiFhirMetadataDiscoveryTest(TestCase):
    """
    Test the Discovery Endpoints
    These are public URIs
    """

    def setUp(self):
        self.client = Client()

    def test_get_fhir_metadata(self):
        """
        Test get fhir metadata discovery
        """
        response = self.client.get(
            reverse('fhir_metadata_uri'))
        self.assertEqual(response.status_code, 200)
        jr = response.json()
        self.assertEqual(jr['resourceType'], "CapabilityStatement")


class ClientApiOAuth2DiscoveryTest(TestCase):
    """
    Test the OAuth2 Discovery Endpoint
    Public URIs
    """

    def setUp(self):
        self.client = Client()

    def test_get_oauth2_discovery(self):
        """
        Test get oauth2 discovery
        """
        response = self.client.get(reverse('oauth_authorization_server'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "userinfo_endpoint")
