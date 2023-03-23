from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


class PublicTagsApiTest(TestCase):
    """Test the public available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test that tags are retrieved"""
        Tag.objects.create(name="Salad", user=self.user)
        Tag.objects.create(name="Dessert", user=self.user)

        response = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the autheticated user"""
        new_user = get_user_model().objects.create_user(
            email="another_user@example.com",
            password="testpassword",
        )
        Tag.objects.create(name="Breakfast", user=new_user)
        tag = Tag.objects.create(name="Vegan", user=self.user)

        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {"name": "Test tag"}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload["name"],
        ).exists()
        self.assertTrue(exists)

    def test_create_invalid_tag(self):
        """Test creating a new tag with an invalid payload"""
        payload = {"name": ""}
        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name="Tag1")
        tag2 = Tag.objects.create(user=self.user, name="Tag2")
        recipe = Recipe.objects.create(
            title="Test recipe",
            time_minutes=10,
            price=5.00,
            user=self.user,
        )
        recipe.tags.add(tag1)

        response = self.client.get(TAGS_URL, {"assigned_only": 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)
