from .base import BaseTestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from rest_framework.test import RequestsClient


class IdentifierTestCase(BaseTestCase):

    def get_permissions(self):
        return Permission.objects.filter(
            content_type__in=(
                ContentType.objects.get_by_natural_key('accounts', 'userprofile'),
                ContentType.objects.get_by_natural_key('ial', 'identityassuranceleveldocumentation'),),
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

    def test_create_identifier_success(self):
        client = RequestsClient()
        response = client.post(
            "http://testserver/api/v1/user/{}/id-assurance/".format(self.subject),
            json={
                "description": "NY Medicaid card.",
                "classification": "ONE-SUPERIOR-OR-STRONG+",
                "exp": "2022-01-01",
                "note": "A paper copy of the document is on file.",
                "verification_date": "2019-03-04"
            },
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })

        self.assertEqual(201, response.status_code, response.text)

        self.assertDictContainsSubset({
            "description": "NY Medicaid card.",
            "classification": "ONE-SUPERIOR-OR-STRONG+",
            "exp": "2022-01-01",
            "verifier_subject": self.token.user.userprofile.subject,
            "note": "A paper copy of the document is on file.",
            "verification_date": "2019-03-04"
        }, response.json(), response.json())
        get_response = client.get(
            "http://testserver/api/v1/user/{}/id-assurance/{}".format(self.subject, response.json()['uuid']),
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })
        self.assertEqual(200, get_response.status_code, get_response.text)
        self.assertDictContainsSubset({
            "description": "NY Medicaid card.",
            "classification": "ONE-SUPERIOR-OR-STRONG+",
            "exp": "2022-01-01",
            "verifier_subject": self.token.user.userprofile.subject,
            "note": "A paper copy of the document is on file.",
            "verification_date": "2019-03-04"
        }, get_response.json(), get_response.json())

    def test_create_identifier_user_notfound(self):
        client = RequestsClient()
        response = client.post(
            "http://testserver/api/v1/user/{}/id-assurance/".format(0000),
            json={
                "description": "NY Medicaid card.",
                "classification": "ONE-SUPERIOR-OR-STRONG+",
                "exp": "2022-01-01",
                "note": "A paper copy of the document is on file.",
                "verification_date": "2019-03-04"
            },
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })

        self.assertEqual(404, response.status_code, response.text)

    def test_update_identifier_success(self):
        client = RequestsClient()
        response = client.post(
            "http://testserver/api/v1/user/{}/id-assurance/".format(self.subject),
            json={
                "description": "NY Medicaid card.",
                "classification": "ONE-SUPERIOR-OR-STRONG+",
                "exp": "2022-01-01",
                "note": "A paper copy of the document is on file.",
                "verification_date": "2019-03-04"
            },
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })

        update_response = client.put(
            "http://testserver/api/v1/user/{}/id-assurance/{}/".format(self.subject, response.json()['uuid']),
            json={
                "exp": "2021-01-01",
            },
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })
        self.assertEqual(200, update_response.status_code, update_response.text)

        get_response = client.get(
            "http://testserver/api/v1/user/{}/id-assurance/{}".format(self.subject, response.json()['uuid']),
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })
        self.assertEqual(200, get_response.status_code, get_response.text)
        self.assertDictContainsSubset({
            "description": "NY Medicaid card.",
            "classification": "ONE-SUPERIOR-OR-STRONG+",
            "exp": "2021-01-01",
            "verifier_subject": self.token.user.userprofile.subject,
            "note": "A paper copy of the document is on file.",
            "verification_date": "2019-03-04"
        }, get_response.json(), get_response.json())

    def test_update_identifier_user_notfound(self):
        client = RequestsClient()
        client.post(
            "http://testserver/api/v1/user/{}/id-assurance/".format(self.subject),
            json={
                "description": "NY Medicaid card.",
                "classification": "ONE-SUPERIOR-OR-STRONG+",
                "exp": "2022-01-01",
                "note": "A paper copy of the document is on file.",
                "verification_date": "2019-03-04"
            },
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })

        update_response = client.put(
            "http://testserver/api/v1/user/{}/id-assurance/{}/".format(self.subject, 'baduuid'),
            json={
                "exp": "2021-01-01",
            },
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })
        self.assertEqual(404, update_response.status_code, update_response.text)

    def test_delete_identifier_success(self):
        client = RequestsClient()
        response = client.post(
            "http://testserver/api/v1/user/{}/id-assurance/".format(self.subject),
            json={
                "description": "NY Medicaid card.",
                "classification": "ONE-SUPERIOR-OR-STRONG+",
                "exp": "2022-01-01",
                "note": "A paper copy of the document is on file.",
                "verification_date": "2019-03-04"
            },
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })

        delete_response = client.delete(
            "http://testserver/api/v1/user/{}/id-assurance/{}/".format(self.subject, response.json()['uuid']),
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })
        self.assertEqual(204, delete_response.status_code, delete_response.text)

        get_response = client.get(
            "http://testserver/api/v1/user/{}/id-assurance/{}".format(self.subject, response.json()['uuid']),
            headers={
                'Authorization': "Bearer {}".format(self.token.token),
            })
        self.assertEqual(404, get_response.status_code, get_response.text)
