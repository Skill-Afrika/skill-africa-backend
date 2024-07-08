from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from profile_management.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class LoginViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("login_view")
        self.username = "john_doe"
        self.email = "johndoe@example.com"
        self.password = "Str0ng_P@ssw0rd"
        self.user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )
        self.valid_data = {"username": self.username, "password": self.password}
        self.valid_data_username = {
            "username": self.username,
            "password": self.password,
        }
        self.valid_data_email = {"email": self.email, "password": self.password}
        self.invalid_data = {"username": self.username, "password": "wrong_password"}
        self.missing_data = {"username": self.username}

    def test_successful_login_username(self):
        response = self.client.post(self.url, self.valid_data_username, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertIn("username", response.data["user"])
        self.assertIn("email", response.data["user"])
        self.assertIn("role", response.data["user"])
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("access_expiration", response.data)
        self.assertIn("refresh_expiration", response.data)

    def test_successful_login_email(self):
        response = self.client.post(self.url, self.valid_data_email, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertIn("username", response.data["user"])
        self.assertIn("email", response.data["user"])
        self.assertIn("role", response.data["user"])
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("access_expiration", response.data)
        self.assertIn("refresh_expiration", response.data)

    def test_login_with_incorrect_credentials(self):
        response = self.client.post(self.url, self.invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("Incorrect password.", response.data["non_field_errors"][0])

    def test_login_with_missing_data(self):
        response = self.client.post(self.url, self.missing_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("This field is required.", response.data["password"][0])

    def test_login_with_missing_fields(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("This field is required.", response.data["password"][0])

    def test_login_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("Incorrect password.", response.data["non_field_errors"][0])

    def test_login_response_contains_tokens(self):
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertTrue(response.data["access"])
        self.assertTrue(response.data["refresh"])


class LogoutViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("logout_view")
        self.user = User.objects.create_user(
            username="john_doe", email="johndoe@example.com", password="strong_password"
        )
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_successful_logout(self):
        self.client.login(username="john_doe", password="strong_password")
        response = self.client.post(
            self.url, {"refresh": self.refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Successfully logged out.")

    def test_logout_with_missing_refresh_token(self):
        self.client.login(username="john_doe", password="strong_password")
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], "Refresh token was not included in request data."
        )

    def test_logout_with_invalid_refresh_token(self):
        self.client.login(username="john_doe", password="strong_password")
        response = self.client.post(
            self.url, {"refresh": "invalid_token"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Token is invalid or expired")

    def test_logout_with_blacklisted_refresh_token(self):
        self.client.login(username="john_doe", password="strong_password")
        token = RefreshToken(self.refresh_token)
        token.blacklist()
        response = self.client.post(
            self.url, {"refresh": self.refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Token is blacklisted")
