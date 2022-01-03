from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Ingredient
from recipe import serializers


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def sample_user(
        email='test@newuser.com',
        name='New User',
        password='password'):
    return get_user_model().objects.create_user(
                                                email=email,
                                                password=password,
                                                name=name
                                                )


class PublicIngredientApiTest(TestCase):
    """Test requests for unauthenticated users"""
    def setUp(self):
        self.client == APIClient()

    def test_login_required(self):
        """Test that login is required to retrive recipes"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test requests for authenticated users"""
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_retrive_ingredients(self):
        """Test retrive ingredients successful"""
        Ingredient.objects.create(name='New Ingredient', user=self.user)
        Ingredient.objects.create(name='New Ingredient2', user=self.user)

        ingredients = Ingredient.objects.all()
        serializer = serializers.IngredientSerializer(ingredients, many=True)
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_retrive_ingredients_for_user(self):
        """Test retrive ingredients for user only"""
        user2 = get_user_model().objects.create_user(
            name='User 2',
            email='usser2@emailtest.com',
            password='passoword'
        )

        ingredient = Ingredient.objects.create(name='First Ingredient',
                                               user=self.user)

        Ingredient.objects.create(name='Alternative Ingredient', user=user2)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test creating an ingredient"""
        payload = {'name': 'An ingredient'}
        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            name=payload['name'],
            user=self.user
        ).exists()

        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_ingredient(self):
        """Test creating an ingredieent with invalid inputs"""
        payload = {
            'name': ''
        }
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
