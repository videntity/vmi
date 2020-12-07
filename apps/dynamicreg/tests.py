from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth.models import Group
import base64
import json


User = get_user_model()


class DynRegTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="deanna", password="somepassword")
        self.dcrp_group = Group.objects.create(
            name='DynamicClientRegistrationProtocol')
        self.dcrp_group.user_set.add(self.user)
        self.user.save()
        self.auth_headers = {'HTTP_AUTHORIZATION': 'Basic ' +
                             base64.b64encode(b'deanna:somepassword').decode("ascii")}
        self.client = Client()
        self.registration_endpoint = reverse('registration_endpoint')
        self.register_test = {"client_name": "foo",
                              "client_id": "bar",
                              "redirect_uris": ["https://foo.com", "https://bar.com"]}

    def test_register_app(self):
        """
        DCRP Test happy path
        """
        response = self.client.post(self.registration_endpoint,
                                    json.dumps(self.register_test),
                                    follow=True,
                                    content_type="application/json",
                                    **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'client_secret')
        self.assertContains(response, 'client_id')
