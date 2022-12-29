from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email="test@example.com", password="testpassword"):
    """Create a sample user"""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    def test_create_user_with_email_successfully(self):
        """Test creating a new user with an email is successful"""
        email = "test@example.com"
        password = "testpassword"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """Test the email for a new user is normalized"""

        email = "test@EXAMPLE.COM"
        user = get_user_model().objects.create_user(email, "dummy_password")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating a new user with an invalid email fails"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "dummy_password")

    def test_create_new_superuser(self):
        """Test creating a new superuser is successful"""
        email = "admin@example.com"
        password = "admin123"
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
            is_superuser=True,
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test creating a new tag is successful"""
        tag = models.Tag.objects.create(user=sample_user(), name="test")

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string is correct"""
        ingredent = models.Ingredient.objects.create(
            name="Oil",
            user=sample_user(),
        )

        self.assertEqual(str(ingredent), ingredent.name)

    def test_recipe_str(self):
        """Test the recipe string is correct"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Steak and mushroom sauce",
            time_minutes=5,
            price=5.00,
        )
        self.assertEqual(str(recipe), recipe.title)
