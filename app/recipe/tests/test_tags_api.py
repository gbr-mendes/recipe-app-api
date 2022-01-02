from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def user_sample(email='testcase@email.com', password='testCasse'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    """Test the public availeble tags API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to get the tags list"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Test for requests from authenticated users
    """
    def setUp(self):
        self.client = APIClient()
        self.user = user_sample()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """Test retriving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_tags_limited_to_user(self):
        """Test that the tags returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='altuser@email.com',
            name='Alt User',
            password='altUser'
        )

        Tag.objects.create(user=user2, name='Juices')
        tag = Tag.objects.create(user=self.user, name='Meats')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
