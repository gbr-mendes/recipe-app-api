from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='testuser@email.com', password='testCase'):
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an emails is successful"""
        email = 'test@gbmsolucoesweb.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """Test the email for a new user is normalized"""
        email = 'test@GBMSOLUCOESWEB.COM'
        user = get_user_model().objects.create_user(email, 'test123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """
        Test if an error is raised if a user is createad with an invalid email
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_superuser(self):
        """Test crerating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@gbmsolucoesweb.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representaion"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representaion"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='New Ingredient'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test recipe string respresentation"""
        recipe = models.Recipe.objects.create(
            name='Chocolate cake',
            user=sample_user(),
        )
        self.assertEqual(str(recipe), recipe.name)
