from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from recipe import serializers

from core import models


RECIPE_URL = reverse('recipe:recipe-list')


class PublicRecipeApiTests(TestCase):
    """Test for unauthenticated requests"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required  to retrive data from recipe endpoint"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test for requests from authenticaated users to recipe endpoints"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email='testcase@email.com',
            name='Test Case',
            password='testCase'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipes_success(self):
        """Test retring recipes successful"""
        models.Recipe.objects.create(
            name='Chocolate Cake',
            user=self.user
        )

        recipes = models.Recipe.objects.all()
        serializer = serializers.RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPE_URL)
        self.assertEqual(serializer.data, res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrive_retrive_recipes_for_user(self):
        """Test retriving recipes for user only"""
        user2 = get_user_model().objects.create_user(
            email='user2@testcase.com',
            name='User 2',
            password='password'
        )
        recipe = models.Recipe.objects.create(
            name='Chocolate Cake',
            user=self.user
        )
        models.Recipe.objects.create(
            name='Carrot Cake',
            user=user2
        )

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code,  status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], recipe.name)
