from datetime import date
from django.contrib.auth import get_user_model
from django.test import Client
from oauth2_provider.models import get_application_model, get_access_token_model
from apps.accounts.models import UserProfile
from .base import BaseTestCase

User = get_user_model()
Application = get_application_model()
AccessToken = get_access_token_model()


class UserTestCase(BaseTestCase):

    def test_create_user_success(self):
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
            content_type='application/json',
            Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertDictContainsSubset({
            # "iss": "http://localhost:8000",
            # "subject": "123456789012345",
            "preferred_username": "james",
            "given_name": "JAMES",
            "family_name": "KIRK",
            "name": "JAMES KIRK",
            "gender": "male",
            "birthdate": "1952-01-03",
            "nickname": "Jim",
            "phone_number": "+15182345678",
            "email": "jamess@example.com",
            "ial": '1',
            # "id_assursance": [],
            "document": [],
            "address": []
        }, response.json())

        up = UserProfile.objects.get(subject=response.json()['sub'])
        self.assertEqual(up.user.username, "james")

    def test_read_user_success(self):
        client = Client()
        create_response = client.post(
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
            content_type='application/json',
            Authorization="Bearer {}".format(self.token.token),
        )
        response = client.get(
             "/api/v1/user/{}/".format(create_response.json()['sub']),
             Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertDictContainsSubset({
            # "iss": "http://localhost:8000",
            # "subject": "123456789012345",
            "preferred_username": "james",
            "given_name": "JAMES",
            "family_name": "KIRK",
            "name": "JAMES KIRK",
            "gender": "male",
            "birthdate": "1952-01-03",
            "nickname": "Jim",
            "phone_number": "+15182345678",
            "email": "jamess@example.com",
            "ial": '1',
            # "id_assursance": [],
            "document": [],
            "address": []
        }, response.json())

    def test_update_user_success(self):
        self.maxDiff = None
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
        update_response = client.put(
             "/api/v1/user/{}/".format(response.json()['sub']),
             {
                "birthdate": "2233-03-22",
                "family_name": "bob",
             },
             content_type="application/json",
             Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(update_response.status_code, 200, update_response.content)
        self.assertEqual("2233-03-22", update_response.json()['birthdate'])

        up = UserProfile.objects.get(subject=response.json()['sub'])
        self.assertEqual(up.birth_date, date(2233, 3, 22))
        self.assertEqual(up.user.last_name, "bob")

    def test_delete_user_success(self):
        self.maxDiff = None
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
            Authorization="Bearer {}".format(self.token.token),
        )

        delete_response = client.delete(
             "/api/v1/user/{}/".format(response.json()['sub']),
             Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(delete_response.status_code, 204, delete_response.content)
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(subject=response.json()['sub'])

    def test_search_users(self):
        """The user API endpoint can be searched with the 'first_or_last_name' parameter."""
        client = Client()

        # There is currently 1 user (the one making the request)
        response1 = client.get(
            "/api/v1/user/",
            Authorization="Bearer {}".format(self.token.token),
        )
        self.assertEqual(len(response1.json()), 1)

        # Create some users
        user1 = User.objects.create(first_name='One', last_name='Example', username='testuser1')
        UserProfile.objects.create(user=user1)
        user2 = User.objects.create(first_name='Two', last_name='Example', username='testuser2')
        UserProfile.objects.create(user=user2)
        user3 = User.objects.create(first_name='Three', last_name='Example', username='testuser3')
        UserProfile.objects.create(user=user3)

        with self.subTest('No search term'):
            # GETting the user list page without a search term returns all users
            response = client.get(
                "/api/v1/user/",
                Authorization="Bearer {}".format(self.token.token),
            )
            self.assertEqual(len(response.json()), 4)

        with self.subTest('Empty search term'):
            # GETting the user list page with an empty search term returns all users
            response = client.get(
                "/api/v1/user/?first_or_last_name=",
                Authorization="Bearer {}".format(self.token.token),
            )
            self.assertEqual(len(response.json()), 4)

        with self.subTest('Exact match'):
            # GETting the user list page with a search term that matches 1 user
            response = client.get(
                "/api/v1/user/?first_or_last_name=one",  # Note: the search is case-insensitive
                Authorization="Bearer {}".format(self.token.token),
            )
            self.assertEqual(len(response.json()), 1)
            self.assertEqual(response.json()[0]['given_name'], 'One')
            self.assertDictContainsSubset(
                {'given_name': 'One', 'family_name': 'Example', 'sub': user1.userprofile.sub},
                response.json()[0]
            )

        with self.subTest('Multiple matches'):
            # GETting the user list page with a search term that matches multiple users
            response = client.get(
                "/api/v1/user/?first_or_last_name=example",
                Authorization="Bearer {}".format(self.token.token),
            )
            self.assertEqual(len(response.json()), 3)
            self.assertEqual(
                set(user['given_name'] for user in response.json()),
                set(['One', 'Two', 'Three'])
            )
            self.assertEqual(
                set(user['family_name'] for user in response.json()),
                set(['Example', 'Example', 'Example'])
            )
            self.assertEqual(
                set(user['sub'] for user in response.json()),
                set([user1.userprofile.sub, user2.userprofile.sub, user3.userprofile.sub])
            )

        with self.subTest('No match'):
            # GETting the user list page with a search term that matches no users
            response = client.get(
                "/api/v1/user/?first_or_last_name=jkfskjdfskjdnbfjshbvjhsbvsjd",
                Authorization="Bearer {}".format(self.token.token),
            )
            self.assertEqual(len(response.json()), 0)
