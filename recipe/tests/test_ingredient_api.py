from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse("recipe:ingredient-list")


class PublicIngredientsApiTest(TestCase):
    """Tests the public ingredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        response = self.client.get(INGREDIENT_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    """Test ingredients can be retrieved by the logged in user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test that ingredients can be retrieved"""
        Ingredient.objects.create(name="Oil", user=self.user)
        Ingredient.objects.create(name="Onion", user=self.user)

        response = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients returned are for the logged in user"""
        new_user = get_user_model().objects.create_user(
            email="another_user@example.com",
            password="testpassword",
        )
        Ingredient.objects.create(name="Sugar", user=new_user)
        ingredient = Ingredient.objects.create(name="Avocado", user=self.user)

        response = self.client.get(INGREDIENT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test creating a new ingredient"""
        payload = {"name": "Tomato"}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            name=payload["name"], user=self.user
        ).exists()
        self.assertTrue(exists)

    def test_create_invalid_ingredient(self):
        """Test creating a new ingredient with an invalid payload"""
        payload = {"name": ""}
        response = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
