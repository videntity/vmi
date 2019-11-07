from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from ..models import Organization

User = get_user_model()


class OrganizationAgentSignupTest(TestCase):
    # Includes two orgs, ACME Health and Transparent Health
    fixtures = ['sample-test-orgs']

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        self.login_url = reverse('mfa_login')
        self.approve_url = reverse('approve_org_affiliation', args=("acme-health", "fred"))
        self.url = reverse('create_org_account', args=("acme-health",))
        self.organization_url = reverse('display_organization', args=("acme-health",))

    def test_valid_home_with_orgs(self):
        """
        Unauthenticated homepage displays a dropdown of organizations
        """
        response = self.client.get(self.home_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ACME')
        self.assertContains(response, 'Transparent Health')

    def test_valid_create_org_account_get(self):
        """
        Unauthenticated homepage displays a dropdown of organizations
        """
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ACME Health')
        self.assertContains(response, 'acme-health')

    def test_valid_form_post(self):
        """
        User can create an account with valid input.
        """
        form_data = {'username': 'Fred',
                     'email': 'fred@acme.org',
                     'mobile_phone_number': '919-789-2251',
                     'first_name': 'Fred',
                     'last_name': 'Frames',
                     'password1': 'bedrocks',
                     'password2': 'bedrocks',
                     'agree_tos': True,
                     'attest_training_completed': True,
                     'org_slug': 'acme-health'}

        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'account was created')
        user = User.objects.get(username="fred")

        # Test user cannont log in.
        self.assertEqual(user.username, "fred")
        self.assertEqual(user.is_active, False)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)

        # Test POC can approve.
        self.client.login(username="poc", password="pocpassword")
        response = self.client.get(self.approve_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logout')

        # Test user may now log in.
        user = User.objects.get(username="fred")
        self.assertEqual(user.username, "fred")
        self.assertEqual(user.is_active, True)

        # Test user is now in default groups set in Organization model.
        user = User.objects.get(username="fred")
        org = Organization.objects.get(slug="acme-health")
        ug_list = []
        og_list = []

        for ug in user.groups.all():
            ug_list.append(ug.name)

        for og in org.default_groups_for_agents.all():
            og_list.append(og.name)

        self.assertListEqual(ug_list, og_list)
        self.assertEqual(user.is_active, True)

        # Test user can now see their organization page.
        self.client.login(username="fred", password="bedrocks")
        response = self.client.get(self.organization_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ACME')

    def test_valid_form_with_picture_post(self):
        """
        User can create an account with valid input.
        """
        form_data = {'username': 'wilma',
                     'email': 'aa@acme.org',
                     'mobile_phone_number': '919-789-2251',
                     'first_name': 'Fred',
                     'last_name': 'Frames',
                     'password1': 'bedrocks',
                     'password2': 'bedrocks',
                     'agree_tos': True,
                     'attest_training_completed': True,
                     'org_slug': 'acme-health'}

        fp = open('./apps/accounts/fixtures/profile.jpg', 'rb')
        form_data['picture'] = fp
        response = self.client.post(self.url, form_data, follow=True)
        fp.close()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'account was created')

    def test_invalid_email_domain_form_post(self):
        """
        Valid User cannot login without valid email domain
        """
        form_data = {'username': 'Lea',
                     'email': 'Lea@jjj.org',
                     'mobile_phone_number': '919-789-2251',
                     'first_name': 'Lea',
                     'last_name': 'Bea',
                     'password1': 'bedrocks',
                     'password2': 'bedrocks',
                     'agree_tos': True,
                     'attest_training_completed': True,
                     'org_slug': 'acme-health'}

        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form contained errors')
    #

    def test_invalid_phone_number_form_post(self):
        """
        Valid User cannot login without valid phone number
        """
        form_data = {'username': 'Frida',
                     'email': 'Lea@acme.org',
                     'mobile_phone_number': '919223',
                     'first_name': 'Frida',
                     'last_name': 'Ka',
                     'password1': 'bedrocks',
                     'password2': 'bedrocks',
                     'agree_tos': True,
                     'attest_training_completed': True,
                     'org_slug': 'acme-health'}

        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid phone number')
