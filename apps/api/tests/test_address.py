from .base import BaseTestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from rest_framework.test import RequestsClient


class AddressTestCase(BaseTestCase):

    def get_permissions(self):
        return Permission.objects.filter(
            content_type__in=(
                ContentType.objects.get_by_natural_key('accounts', 'userprofile'),
                ContentType.objects.get_by_natural_key('accounts', 'address'),),
        ).all()

    def setUp(self):
        super().setUp()
        client = RequestsClient()
        response = client.post(
            "http://testserver/api/v1/user/",
            json={
                "preferred_username": "james",
                "given_name": "James",
                "family_name": "Kirk",
                "gender": "M",
                "password": "tree garden jump fox",
                "birthdate": "1952-01-03",
                "nickname": "Jim",
                "phone_number": "+15182345678",
                "email": "jamess@example.com",
             }, headers={
                'Authorization': "Bearer {}".format(self.token.token),
             })
        self.assertEqual(201, response.status_code, response.text)
        self.subject = response.json()['sub']

    def test_create_address_success(self):
        client = RequestsClient()
        response = client.post(
            "http://testserver/api/v1/user/{}/address/".format(self.subject),
            json={
                "street_address": "837 State St.",
                "locality": "Schenectady",
                "region": "NY",
                "postal_code": "12307",
                "country": "US"
            },
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })

        self.assertEqual(201, response.status_code, response.text)

        self.assertDictContainsSubset({
            "formatted": "837 State St. \nSchenectady, NY 12307",
            "street_address": "837 State St.",
            "locality": "Schenectady",
            "region": "NY",
            "postal_code": "12307",
            "country": "US"
        }, response.json(), response.json())
        get_response = client.get(
            "http://testserver/api/v1/user/{}/address/{}".format(self.subject, response.json()['uuid']),
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })
        self.assertEqual(200, get_response.status_code, get_response.text)
        self.assertDictContainsSubset({
            "formatted": "837 State St. \nSchenectady, NY 12307",
            "street_address": "837 State St.",
            "locality": "Schenectady",
            "region": "NY",
            "postal_code": "12307",
            "country": "US"
        }, get_response.json(), get_response.json())

    def test_update_address_success(self):
        client = RequestsClient()
        response = client.post(
            "http://testserver/api/v1/user/{}/address/".format(self.subject),
            json={
                "street_address": "837 State St.",
                "locality": "Schenectady",
                "region": "NY",
                "postal_code": "12307",
                "country": "US"
            },
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })

        update_response = client.put(
            "http://testserver/api/v1/user/{}/address/{}/".format(self.subject, response.json()['uuid']),
            json={
                "region": "MD",
            },
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })
        self.assertEqual(200, update_response.status_code, update_response.text)

        get_response = client.get(
            "http://testserver/api/v1/user/{}/address/{}".format(self.subject, response.json()['uuid']),
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })
        self.assertEqual(200, get_response.status_code, get_response.text)
        self.assertDictContainsSubset({
            "formatted": "837 State St. \nSchenectady, MD 12307",
            "street_address": "837 State St.",
            "locality": "Schenectady",
            "region": "MD",
            "postal_code": "12307",
            "country": "US"
        }, get_response.json(), get_response.json())

    def test_delete_address_success(self):
        client = RequestsClient()
        response = client.post(
            "http://testserver/api/v1/user/{}/address/".format(self.subject),
            json={
                "street_address": "837 State St.",
                "locality": "Schenectady",
                "region": "NY",
                "postal_code": "12307",
                "country": "US"
            },
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })

        delete_response = client.delete(
            "http://testserver/api/v1/user/{}/address/{}/".format(self.subject, response.json()['uuid']),
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })
        self.assertEqual(204, delete_response.status_code, delete_response.text)

        get_response = client.get(
            "http://testserver/api/v1/user/{}/address/{}".format(self.subject, response.json()['uuid']),
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })
        self.assertEqual(404, get_response.status_code, get_response.text)
