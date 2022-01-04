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

    def test_create_basic_recipe(self):
        """Test creating recipes api method"""
        payload = {
            'title': 'New Recipe Test',
            'time_minutes': 30,
            'price': 20.50,
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = models.Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating recipes with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Meats')
        payload = {
            'title': 'Recipe With Tag',
            'time_minutes': 30,
            'price': 20.00,
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = models.Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Testing create recipes with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Salt')
        ingredient2 = sample_ingredient(user=self.user, name='Sugar')

        payload = {
            'title': 'Cheese cake',
            'time_minutes': 30,
            'price': 20.00,
            'ingredients': [ingredient1.id, ingredient2.id]
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = models.Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_update_recipes(self):
        """Testing partial update recipes"""
        recipe = sample_recipe(user=self.user)
        recipe.ingredients.add(sample_ingredient(user=self.user,
                                                 name='Salt'))

        ingredient = sample_ingredient(user=self.user)

        payload = {
            'title': 'Name Updated',
            'ingredients': [ingredient.id, ],
            'link': 'https://www.myrecipe.com'
        }
        url = recipe_detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        ingredients = recipe.ingredients.all()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, payload['link'])
        self.assertEqual(len(ingredients), 1)
        self.assertIn(ingredient, ingredients)
