from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_ACCOUNT_URL = reverse("accounts:create")
TOKEN_URL = reverse("accounts:token")


def create_user_account(**params):
    return get_user_model().objects.create_user(**params)


class PublicAccountsApiTest(TestCase):
    """Test the user accounts API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a valid user"""
        payload = {
            "email": "test@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }

        response = self.client.post(CREATE_USER_ACCOUNT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", response.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            "email": "test@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        create_user_account(**payload)

        response = self.client.post(CREATE_USER_ACCOUNT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be  more than 6 characters"""
        payload = {"email": "test@example.com", "password": "pass"}

        response = self.client.post(CREATE_USER_ACCOUNT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = (
            get_user_model().objects.filter(email=payload["email"]).exists()
        )
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {"email": "test@example.com", "password": "testpassword"}
        create_user_account(**payload)

        response = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are provided"""
        create_user_account(email="test@example.com", password="testpassword")
        payload = {"email": "test@example.com", "password": "invalidpassword"}

        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_from_non_existent_user(self):
        """Test that the token is not created if the user does not exist"""
        payload = {"email": "test@example.com", "password": "testpassword"}

        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that the email and password are required"""
        response = self.client.post(TOKEN_URL, {"email": "", "password": ""})
        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
