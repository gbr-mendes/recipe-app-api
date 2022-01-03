from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from recipe import serializers

from core import models


RECIPE_URL = reverse('recipe:recipe-list')


def recipe_detail_url(recipe_id):
    """Create an return a recipe detail url"""
    url = reverse('recipe:recipe-detail', args=[recipe_id])
    return url

def sample_ingredient(user, name='Salt'):
    """Create and return a saample ingredient"""
    return models.Ingredient.objects.create(user=user, name=name)

def sample_tag(user, name="Vegan"):
    """Create and return a sample tag"""
    return models.Tag.objects.create(user=user, name=name)

def sample_recipe(user, **parms):
    """Create and return a recipe"""
    defaults = {
        'title': 'Carrot  Cake',
        'time_minutes': 30,
        'price': 25.00,
    }
    parms.update(defaults)
    return models.Recipe.objects.create(user=user, **parms)


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
            title='Chocolate Cake',
            user=self.user,
            time_minutes=30,
            price=25.00
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
            title='Chocolate Cake',
            user=self.user,
            time_minutes=30,
            price=25.00
        )
        models.Recipe.objects.create(
            title='Carrot Cake',
            user=user2,
            time_minutes=30,
            price=25.00
        )

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code,  status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], recipe.title)
    
    def test_get_recipe_detail(self):
        """Test geting the detail for an especifc recipe"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        res = self.client.get(recipe_detail_url(recipe.id))
        serializer = serializers.RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)
