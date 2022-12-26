from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="admin123",
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="john.doe@example.com",
            password="user123",
            first_name="John",
            last_name="Doe",
        )

    def test_users_are_listed_in_admin_site(self):
        """Test that users are listed in admin"""
        url = reverse("admin:core_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page is displayed"""
        url = reverse("admin:core_user_change", args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """Test that the user create page is displayed"""
        url = reverse("admin:core_user_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
