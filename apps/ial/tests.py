from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from ..accounts.models import UserProfile
from django.contrib.auth.models import Permission


class IALUpgradeTestCase(TestCase):
    """
    IAL Upgrade
    """

    def _create_user(self, username, password, **extra_fields):
        """
        Helper method that creates a user instance
        with `username` and `password` set.
        """
        User = get_user_model()
        user = User.objects.create_user(username,
                                        password=password,
                                        **extra_fields)
        return user

    def setUp(self):
        User = get_user_model()
        self._create_user('bob', 'barker', first_name='Bob',
                          last_name='Bob', email='bobexample.com')
        self.user = User.objects.get(username='bob')

        self.other_user = self._create_user('alice', 'wonder', first_name='Alice',
                                            last_name='Wonderland', email='alice@example.com')

        self.up = UserProfile.objects.create(user=self.user)
        self.other_user_up = UserProfile.objects.create(user=self.other_user)
        self.other_user_subject = self.other_user_up.subject
        self.client = Client()
        self.client.login(username="bob", password="barker")
        self.url = reverse('inperson_id_verify',
                           args=(self.other_user_subject,))

    def test_untrursted_wo_permission_cannot_raise_ial(self):
        """
        Test a persona can raise IAL of another if the have the permission to do so.
        """
        response = self.client.get(self.url)
        # Should 302 and redirect to login since permission is missing.
        self.assertEqual(response.status_code, 302)

    def test_trusted_ref_can_raise_ial(self):
        """
        Test a persona can raise IAL of another if the have the permission to do so.
        """
        permission = Permission.objects.get(
            codename='change_identityassuranceleveldocumentation')

        self.user.user_permissions.add(permission)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Evidence')

    def test_trusted_ref_cannot_raise_their_own_ial(self):
        """
        Test a persona can raise IAL of another if the have the permission to do so.
        """
        permission = Permission.objects.get(
            codename='change_identityassuranceleveldocumentation')

        self.user.user_permissions.add(permission)
        self.url = reverse('inperson_id_verify', args=(self.up.subject,))
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)


class IALUDowngradeTestCase(TestCase):
    """
    Test IAL Downgrade
    """

    def _create_user(self, username, password, **extra_fields):
        """
        Helper method that creates a user instance
        with `username` and `password` set.
        """
        User = get_user_model()
        user = User.objects.create_user(username,
                                        password=password,
                                        **extra_fields)
        return user

    def setUp(self):
        User = get_user_model()
        self._create_user('bob', 'barker', first_name='Bob',
                          last_name='Bob', email='bobexample.com')
        self.user = User.objects.get(username='bob')

        self.other_user = self._create_user('alice', 'wonder', first_name='Alice',
                                            last_name='Wonderland', email='alice@example.com')

        self.up = UserProfile.objects.create(user=self.user)
        self.other_user_up = UserProfile.objects.create(user=self.other_user)
        self.other_user_subject = self.other_user_up.subject
        self.client = Client()
        self.client.login(username="bob", password="barker")
        self.url = reverse('ial_two_to_one_downgrade',
                           args=(self.other_user_subject,))

    def test_untrursted_wo_permission_cannot_raise_ial(self):
        """
        Test a persona can raise IAL of another if the have the permission to do so.
        """
        response = self.client.get(self.url)
        # Should 302 and redirect to login since permission is missing.
        self.assertEqual(response.status_code, 302)

    def test_trusted_ref_can_raise_ial(self):
        """
        Test a persona can raise IAL of another if the have the permission to do so.
        """
        permission = Permission.objects.get(
            codename='change_identityassuranceleveldocumentation')

        self.user.user_permissions.add(permission)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'downgrade')

    def test_trusted_ref_cannot_raise_their_own_ial(self):
        """
        Test a persona can raise IAL of another if the have the permission to do so.
        """
        permission = Permission.objects.get(
            codename='change_identityassuranceleveldocumentation')

        self.user.user_permissions.add(permission)
        self.url = reverse('inperson_id_verify', args=(self.up.subject,))
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)
