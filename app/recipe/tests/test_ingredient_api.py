from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URLS = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """Test that publically available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint."""
        res = self.client.get(INGREDIENTS_URLS)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test that privately available ingredients API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@volleads.com',
            password='TestPass'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test that retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Onion')
        Ingredient.objects.create(user=self.user, name='Sugar')

        res = self.client.get(INGREDIENTS_URLS)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for the authenticated user are returened"""
        user2 = get_user_model().objects.create_user(
            email='other@volleads.com',
            password='TEtspass'
        )
        Ingredient.objects.create(user=user2, name='Corriander')
        Ingredient.objects.create(user=user2, name='Sugar')

        ingredient1 = Ingredient.objects.create(user=self.user, name='Salt')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Onion')
        ingredient3 = Ingredient.objects.create(user=self.user,
                                                name="Lady's Finger")

        res = self.client.get(INGREDIENTS_URLS)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)
        self.assertEqual(res.data[0]['name'], ingredient1.name)
        self.assertEqual(res.data[1]['name'], ingredient2.name)
        self.assertEqual(res.data[2]['name'], ingredient3.name)
