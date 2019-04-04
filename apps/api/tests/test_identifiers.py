from .base import BaseTestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.test import Client


class IdentifierTestCase(BaseTestCase):

    def get_permissions(self):
        return Permission.objects.filter(
            content_type__in=(
                ContentType.objects.get_by_natural_key('accounts', 'userprofile'),
                ContentType.objects.get_by_natural_key('ial', 'identityassuranceleveldocumentation'),),
        ).all()

    def setUp(self):
        super().setUp()
        client = Client()
        response = client.post(
            "/api/v1/user/",
            {
                "preferred_username": "james",
                "given_name": "James",
                "family_name": "Kirk",
                "gender": "male",
                "password": "tree garden jump fox",
                "birthdate": "1952-01-03",
                "nickname": "Jim",
                "phone_number": "+15182345678",
                "email": "jamess@example.com",
            },
            content_type="application/json",
            Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(201, response.status_code, response.content)
        self.subject = response.json()['sub']

    def test_create_identifier_success(self):
        client = Client()
        response = client.post(
            "/api/v1/user/{}/id-assurance/".format(self.subject),
            {
                "description": "NY Medicaid card.",
                "classification": "ONE-SUPERIOR-OR-STRONG+",
                "exp": "2022-01-01",
                "note": "A paper copy of the document is on file.",
                "verification_date": "2019-03-04"
            },
            content_type="application/json",
            Authorization="Bearer {}".format(self.token.token),
        )

        self.assertEqual(201, response.status_code, response.content)

        self.assertDictContainsSubset({
            "description": "NY Medicaid card.",
            "classification": "ONE-SUPERIOR-OR-STRONG+",
            "exp": "2022-01-01",
            "verifier_subject": self.token.user.userprofile.subject,
            "note": "A paper copy of the document is on file.",
            "verification_date": "2019-03-04"
        }, response.json(), response.json())
        get_response = client.get(
            "/api/v1/user/{}/id-assurance/{}/".format(self.subject, response.json()['uuid']),
            Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(200, get_response.status_code, get_response.content)
        self.assertDictContainsSubset({
            "description": "NY Medicaid card.",
            "classification": "ONE-SUPERIOR-OR-STRONG+",
            "exp": "2022-01-01",
            "verifier_subject": self.token.user.userprofile.subject,
            "note": "A paper copy of the document is on file.",
            "verification_date": "2019-03-04"
        }, get_response.json(), get_response.json())

    def test_create_identifier_user_notfound(self):
        client = Client()
        response = client.post(
            "/api/v1/user/{}/id-assurance/".format(0000),
            {
                "description": "NY Medicaid card.",
                "classification": "ONE-SUPERIOR-OR-STRONG+",
                "exp": "2022-01-01",
                "note": "A paper copy of the document is on file.",
                "verification_date": "2019-03-04"
            },
            Authorization="Bearer {}".format(self.token.token),
        )

        self.assertEqual(404, response.status_code, response.content)

    def test_update_identifier_success(self):
        client = Client()
        response = client.post(
            "/api/v1/user/{}/id-assurance/".format(self.subject),
            {
                "description": "NY Medicaid card.",
                "classification": "ONE-SUPERIOR-OR-STRONG+",
                "exp": "2022-01-01",
                "note": "A paper copy of the document is on file.",
                "verification_date": "2019-03-04"
            },
            content_type="application/json",
            Authorization="Bearer {}".format(self.token.token),
        )

        update_response = client.put(
            "/api/v1/user/{}/id-assurance/{}/".format(self.subject, response.json()['uuid']),
            {
                "exp": "2021-01-01",
            },
            content_type="application/json",
            Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(200, update_response.status_code, update_response.content)

        get_response = client.get(
            "/api/v1/user/{}/id-assurance/{}/".format(self.subject, response.json()['uuid']),
            Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(200, get_response.status_code, get_response.content)
        self.assertDictContainsSubset({
            "description": "NY Medicaid card.",
            "classification": "ONE-SUPERIOR-OR-STRONG+",
            "exp": "2021-01-01",
            "verifier_subject": self.token.user.userprofile.subject,
            "note": "A paper copy of the document is on file.",
            "verification_date": "2019-03-04"
        }, get_response.json(), get_response.json())

    def test_update_identifier_user_notfound(self):
        client = Client()
        client.post(
            "/api/v1/user/{}/id-assurance/".format(self.subject),
            {
                "description": "NY Medicaid card.",
                "classification": "ONE-SUPERIOR-OR-STRONG+",
                "exp": "2022-01-01",
                "note": "A paper copy of the document is on file.",
                "verification_date": "2019-03-04"
            },
            content_type="application/json",
            Authorization="Bearer {}".format(self.token.token),
        )

        update_response = client.put(
            "/api/v1/user/{}/id-assurance/{}/".format(self.subject, 'baduuid'),
            {
                "exp": "2021-01-01",
            },
            content_type="application/json",
            Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(404, update_response.status_code, update_response.content)

    def test_delete_identifier_success(self):
        client = Client()
        response = client.post(
            "/api/v1/user/{}/id-assurance/".format(self.subject),
            {
                "description": "NY Medicaid card.",
                "classification": "ONE-SUPERIOR-OR-STRONG+",
                "exp": "2022-01-01",
                "note": "A paper copy of the document is on file.",
                "verification_date": "2019-03-04"
            },
            content_type="application/json",
            Authorization="Bearer {}".format(self.token.token),
        )

        delete_response = client.delete(
            "/api/v1/user/{}/id-assurance/{}/".format(self.subject, response.json()['uuid']),
            Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(204, delete_response.status_code, delete_response.content)

        get_response = client.get(
            "/api/v1/user/{}/id-assurance/{}/".format(self.subject, response.json()['uuid']),
            Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(404, get_response.status_code, get_response.content)
