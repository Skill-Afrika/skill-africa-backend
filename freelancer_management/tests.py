from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from profile_management.models import User


class FreelanceRegistrationViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("freelance_registeration")
        self.valid_data = {
            "username": "john_doe",
            "email": "johndoe@example.com",
            "password": "Str0ng_P@ssw0rd",
        }
        self.invalid_data = {
            "username": "",
            "email": "not-an-email",
            "password": "short",
        }

    def test_successful_registration(self):
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("username", response.data["user"])
        self.assertIn("email", response.data["user"])
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    def test_registration_with_missing_data(self):
        incomplete_data = self.valid_data.copy()
        incomplete_data.pop("email")
        response = self.client.post(self.url, incomplete_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["error"])

    def test_registration_with_invalid_data(self):
        response = self.client.post(self.url, self.invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data["error"])
        self.assertIn("email", response.data["error"])
        self.assertIn("password", response.data["error"])

    def test_registration_with_existing_username(self):
        User.objects.create_user(
            username="john_doe",
            email="johndoe@example.com",
            password="existing_password",
        )
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data["error"])

    def test_registration_with_existing_email(self):
        User.objects.create_user(
            username="existing_user",
            email="johndoe@example.com",
            password="existing_password",
        )
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["error"])
