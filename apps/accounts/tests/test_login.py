from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse

UserModel = get_user_model()


class SimpleLoginTests(TestCase):

    def setUp(self):
        self.test_user = UserModel.objects.create_user(
            "fred",
            "test@example.com",
            "bedrocks")
        self.client = Client()
        self.url = reverse('mfa_login')

    def test_valid_login_get(self):
        """
        Valid login page
        """
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_valid_login(self):
        """
        Valid User can login
        """
        form_data = {'username': 'fred', 'password': 'bedrocks'}
        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logout')

    def test_valid_login_case_insensitive_username(self):
        """
        Valid User can login and username is case insensitive
        """
        form_data = {'username': 'Fred', 'password': 'bedrocks'}
        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logout')

    def test_invalid_login(self):
        """
        Invalid user cannot login
        """
        form_data = {'username': 'fred', 'password': 'dino'}
        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_logout(self):
        """
        User can logout
        """
        self.client.login(username='fred', password='bedrocks')
        response = self.client.get(reverse('mylogout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
