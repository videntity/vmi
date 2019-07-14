import base64
import json
from django.test import TestCase
from oauth2_provider.models import (
    get_access_token_model,
    get_application_model,
    get_grant_model,
    get_refresh_token_model,
)
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs, urlencode, urlparse
from django.urls import reverse
from .jwt import get_jwt_builder
from django.conf import settings


Application = get_application_model()
AccessToken = get_access_token_model()
Grant = get_grant_model()
RefreshToken = get_refresh_token_model()
UserModel = get_user_model()
JWTBuilder = get_jwt_builder()


def get_basic_auth_header(user, password):
    """
    Return a dict containg the correct headers
    to set to make HTTP Basic Auth request
    """
    user_pass = "{0}:{1}".format(user, password)
    auth_string = base64.b64encode(user_pass.encode("utf-8"))
    auth_headers = {
        "HTTP_AUTHORIZATION": "Basic " + auth_string.decode("utf-8"),
    }

    return auth_headers


class RequestValidatorTests(TestCase):

    def setUp(self):
        self.test_user = UserModel.objects.create_user(
            "test_user",
            "test@example.com",
            "123456")
        self.dev_user = UserModel.objects.create_user(
            "dev_user",
            "dev@example.com",
            "123456")

        self.application = Application(
            name="Test Application",
            redirect_uris=(
                "http://localhost http://example.com http://example.org"
            ),
            user=self.dev_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()

        self.web_application = Application(
            name="Test Application",
            redirect_uris=(
                "http://localhost http://example.com http://example.org"
            ),
            user=self.dev_user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_IMPLICIT,
        )
        self.web_application.save()

    def test_standard_oauth_authorization_code_works(self):
        """
        If application.skip_authorization = True,
        should skip the authorization page.
        """
        self.client.login(username="test_user", password="123456")
        self.application.skip_authorization = True
        self.application.save()

        query_string = urlencode({
            "client_id": self.application.client_id,
            "state": "random_state_string",
            "redirect_uri": "http://example.org",
            "response_type": "code",
            "ui_locales": "se",
            "scope": "openid",
        })
        url = "{url}?{qs}".format(url=reverse("oauth2_provider:authorize"),
                                  qs=query_string)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        query_dict = parse_qs(urlparse(response["Location"]).query)
        authorization_code = query_dict["code"].pop()

        # exchange authorization code for a valid access token
        token_request_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": "http://example.org",
        }
        auth_headers = get_basic_auth_header(self.application.client_id,
                                             self.application.client_secret)

        response = self.client.post(
            reverse("oauth2_provider:token"),
            data=token_request_data,
            **auth_headers)
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["token_type"], "Bearer")
        self.assertEqual(
            content["expires_in"],
            settings.OAUTH2_PROVIDER['ACCESS_TOKEN_EXPIRE_SECONDS'])
        id_token = content.get("id_token")
        self.assertIsNotNone(id_token)
        claims = JWTBuilder().decode(
            id_token,
            audience=self.application.client_id)
        self.assertEqual(claims['sub'], self.test_user.id)

    def test_standard_oauth_implicit_works(self):
        """
        If application.skip_authorization = True,
        should skip the authorization page.
        """
        self.client.login(username="test_user", password="123456")
        self.web_application.skip_authorization = True
        self.web_application.save()

        query_string = urlencode({
            "client_id": self.web_application.client_id,
            "state": "random_state_string",
            "redirect_uri": "http://example.org",
            "response_type": "id_token token",
            "nonce": "bad-nonce",
            "scope": "openid",
        })
        url = "{url}?{qs}".format(url=reverse("oauth2_provider:authorize"),
                                  qs=query_string)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("error", response["Location"])

    def test_id_token_only_implicit_works(self):
        """
        If application.skip_authorization = True,
        should skip the authorization page.
        """
        self.client.login(username="test_user", password="123456")
        self.web_application.skip_authorization = True
        self.web_application.save()

        query_string = urlencode({
            "client_id": self.web_application.client_id,
            "state": "random_state_string",
            "redirect_uri": "http://example.org",
            "response_type": "id_token",
            "nonce": "bad-nonce",
        })
        url = "{url}?{qs}".format(url=reverse("oauth2_provider:authorize"),
                                  qs=query_string)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("error", response["Location"])
