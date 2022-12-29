from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe, Tag

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_sample_tag(user, name="Main course"):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user, name="Onion"):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def create_sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        "title": "Sample recipe",
        "time_minutes": 5,
        "price": 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipesApiTest(TestCase):
    """Test the public recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving recipes"""
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesApiTest(TestCase):
    """Test recipes can be retrieved by the logged in user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe_list(self):
        """Test that recipes can be retrieved"""
        create_sample_recipe(self.user)
        create_sample_recipe(self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_recipe_limite_to_user(self):
        """Test that recipes can be retrieved by the logged in user"""
        new_user = get_user_model().objects.create_user(
            email="another_user@example.com",
            password="testpassword",
        )
        create_sample_recipe(new_user)
        create_sample_recipe(self.user)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        response = self.client.get(RECIPES_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_recipe_detail(self):
        """Test retrieve recipe details"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(
            create_sample_tag(user=self.user),
        )
        recipe.ingredients.add(
            create_sample_ingredient(user=self.user),
        )

        url = detail_url(recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test create recipe"""
        payload = {
            "title": "Sample recipe",
            "time_minutes": 35,
            "price": 5.00,
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test create a recipe with tags"""
        tag1 = create_sample_tag(user=self.user, name="Vegan")
        tag2 = create_sample_tag(user=self.user, name="Dessert")
        payload = {
            "title": "Avocado lime cheesecake",
            "tags": [tag1.id, tag2.id],
            "time_minutes": 60,
            "price": 20.00,
        }

        response = self.client.post(RECIPES_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data["id"])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test create a recipe with ingredients"""
        ingredient1 = create_sample_ingredient(user=self.user, name="Prawns")
        ingredient2 = create_sample_ingredient(user=self.user, name="Ginger")
        payload = {
            "title": "Thai prawn red curry",
            "ingredients": [ingredient1.id, ingredient2.id],
            "time_minutes": 20,
            "price": 8.00,
        }

        response = self.client.post(RECIPES_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data["id"])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
