from datetime import datetime, timedelta
import uuid
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from profile_management.models import User, PasswordOTP
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch


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


class PasswordOTPViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("password_otp")
        self.user = User.objects.create_user(
            email="test_user@example.com", password="testpass123", username="test_user"
        )

    def test_get_otp_success(self):
        response = self.client.post(self.url, {"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "OTP sent successfully")
        self.assertEqual(str(response.data["data"]["uuid"]), str(self.user.uuid))

        # Verify OTP object is created
        otp_obj = PasswordOTP.objects.filter(email=self.user.email)
        self.assertTrue(otp_obj.exists())

    def test_get_otp_email_required(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Email is required")

    def test_get_otp_user_not_found(self):
        response = self.client.post(self.url, {"email": "nonexistent@example.com"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "User with this email does not exist")

    def test_existing_otp_deleted_before_new_one_created(self):
        PasswordOTP.objects.create(
            email=self.user.email, code="123456", expires_at=datetime.now()
        )
        response = self.client.post(self.url, {"email": self.user.email})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify old OTP object is deleted and new one is created
        self.assertEqual(PasswordOTP.objects.filter(email=self.user.email).count(), 1)


class VerifyOTPViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "john_doe", "johndoe@example.com", "P@ssw0rd_123"
        )
        self.uuid = self.user.uuid
        self.otp = "123456"
        PasswordOTP.objects.create(
            email=self.user.email,
            code=self.otp,
            expires_at=datetime.now() + timedelta(minutes=30),
        )

    def test_verify_otp_success(self):
        url = reverse("password_otp_confirm", args=[self.uuid])
        data = {"otp": self.otp}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_verify_otp_invalid_otp(self):
        url = reverse("password_otp_confirm", args=[self.uuid])
        data = {"otp": "invalid_otp"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "Invalid OTP"})

    def test_verify_otp_expired_otp(self):
        otp_verification = PasswordOTP.objects.get(email=self.user.email, code=self.otp)
        otp_verification.expires_at = datetime.now() - timedelta(minutes=1)
        otp_verification.save()
        url = reverse("password_otp_confirm", args=[self.uuid])
        data = {"otp": self.otp}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "OTP has expired"})

    def test_verify_otp_missing_otp(self):
        url = reverse("password_otp_confirm", args=[self.uuid])
        data = {}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "OTP and UUID are required"})

    def test_verify_otp_missing_uuid(self):
        url = reverse("password_otp_confirm", args=[str(uuid.uuid4())])
        data = {"otp": self.otp}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "User not found"})
