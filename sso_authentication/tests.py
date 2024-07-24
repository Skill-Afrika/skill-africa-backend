from django.urls import reverse
from django.test import TestCase, Client
from rest_framework import status
from unittest.mock import patch, MagicMock
import uuid
import json
from profile_management.models import User
from freelancer_management.serializers import FreelanceSerializer
from google_auth_oauthlib.flow import Flow


def mock_authorized_session_get(mock_user_info):
    # Create a mock session object
    mock_session = MagicMock()
    # Mock the get method to return a response object with a .json() method
    mock_response = MagicMock()
    mock_response.json.return_value = mock_user_info
    mock_session.get.return_value = mock_response
    return mock_session


class GoogleStartSignInViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.valid_roles = ["freelancer", "sponsor", "admin"]
        self.invalid_role = "invalid_role"

    def test_google_start_sign_in_valid_role(self):
        with patch(
            "uuid.uuid4", return_value=uuid.UUID("12345678123456781234567812345678")
        ):
            with patch(
                "os.getenv",
                return_value=json.dumps(
                    {
                        "web": {
                            "client_id": "fake-client-id",
                            "project_id": "fake-project-id",
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "client_secret": "fake-client-secret",
                            "redirect_uris": [
                                "http://127.0.0.1:8000/google_signin_callback"
                            ],
                        }
                    }
                ),
            ):
                response = self.client.get(
                    reverse("google_signin", args=["freelancer"])
                )
                self.assertEqual(response.status_code, status.HTTP_302_FOUND)
                self.assertIn("https://accounts.google.com/o/oauth2/auth", response.url)

    def test_google_start_sign_in_invalid_role(self):
        response = self.client.get(reverse("google_signin", args=[self.invalid_role]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {"error": {"message": "Path not found"}})


class GoogleEndSignInViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.google_callback_url = reverse("google_signin_callback")
        self.mock_user_info = {
            "id": "mock-id",
            "email": "user@example.com",
            "verified_email": True,
            "name": "Mock User",
            "given_name": "Mock",
            "family_name": "User",
            "picture": "http://mock.picture/url",
            "locale": "en",
        }

    @patch("os.getenv")
    @patch("requests.sessions.Session.get")
    @patch.object(Flow, "fetch_token")
    @patch.object(Flow, "authorized_session")
    def test_google_end_sign_in_existing_user(
        self,
        mock_authorized_session,
        mock_fetch_token,
        mock_get,
        mock_env,
    ):
        mock_fetch_token.return_value = "mock-access-token"
        mock_authorized_session.return_value = mock_authorized_session_get(
            self.mock_user_info
        )
        mock_env.return_value = json.dumps(
            {
                "web": {
                    "client_id": "fake-client-id",
                    "project_id": "fake-project-id",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "fake-client-secret",
                    "redirect_uris": ["http://127.0.0.1:8000/google_signin_callback"],
                }
            }
        )

        mock_get.return_value.json.return_value = self.mock_user_info

        # Create a user that will be returned by the get_user_info method
        user = User.objects.create_user(
            username="mockuser",
            email=self.mock_user_info["email"],
            password="m0ckp@ssw0rd",
            role="freelancer",
        )
        user.save()

        # Also create a Profile for the user
        serializer = FreelanceSerializer(
            data={
                "provider": "google",
                "provider_id": self.mock_user_info["id"],
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.create(
            validated_data={
                "user": user,
                "provider": "google",
                "provider_id": self.mock_user_info["id"],
            }
        )

        session = self.client.session
        session["google_state"] = "state-token"
        session["role"] = "freelancer"
        session.save()

        response = self.client.get(
            self.google_callback_url, {"code": "auth-code", "state": "state-token"}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(response_data["user"]["email"], self.mock_user_info["email"])
        self.assertIn("refresh", response_data)
        self.assertIn("access", response_data)

    @patch("os.getenv")
    @patch("requests.sessions.Session.get")
    @patch.object(Flow, "fetch_token")
    @patch.object(Flow, "authorized_session")
    def test_google_end_sign_in_new_user(
        self,
        mock_authorized_session,
        mock_fetch_token,
        mock_get,
        mock_env,
    ):
        mock_fetch_token.return_value = "mock-access-token"
        mock_authorized_session.return_value = mock_authorized_session_get(
            self.mock_user_info
        )
        mock_env.return_value = json.dumps(
            {
                "web": {
                    "client_id": "fake-client-id",
                    "project_id": "fake-project-id",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "fake-client-secret",
                    "redirect_uris": ["http://127.0.0.1:8000/google_signin_callback"],
                }
            }
        )

        mock_get.return_value.json.return_value = self.mock_user_info

        session = self.client.session
        session["google_state"] = "state-token"
        session["role"] = "freelancer"
        session.save()

        response = self.client.get(
            self.google_callback_url, {"code": "auth-code", "state": "state-token"}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(response_data["user"]["email"], self.mock_user_info["email"])
        self.assertIn("refresh", response_data)
        self.assertIn("access", response_data)

    def test_google_end_sign_in_no_code(self):
        session = self.client.session
        session["google_state"] = "state-token"
        session["role"] = "freelancer"
        session.save()

        response = self.client.get(self.google_callback_url, {"state": "state-token"})

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            response.json(),
            {"error": {"message": "Authorization Code not received from SSO."}},
        )

    def test_google_end_sign_in_state_mismatch(self):
        session = self.client.session
        session["google_state"] = "state-token"
        session["role"] = "freelancer"
        session.save()

        response = self.client.get(
            self.google_callback_url,
            {"code": "auth-code", "state": "different-state-token"},
        )

        self.assertEqual(response.status_code, status.HTTP_428_PRECONDITION_REQUIRED)
        self.assertEqual(
            response.json(), {"error": {"message": "State Mismatch. Time expired?"}}
        )
