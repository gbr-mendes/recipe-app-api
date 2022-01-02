from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('users:create')
GENERATE_TOKEN_USER = reverse('users:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a user with valid payload is ssuccessful"""
        payload = {
            'email': 'test@gbmsolucoesweb.com',
            'name': 'Test Case',
            'password': 'Test1234'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_with_credentials_already_registered(self):
        """Test creating a user with an email already registered"""
        payload = {
            'email': 'test@gbmsolucoesweb.com',
            'password': 'Test1234'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_too_short(self):
        """
        Test that a user is not created with a password
        less than 5 characters
        """

        payload = {
            'email': 'test@gbmsolucoesweb.com',
            'password': 'pw',
            'name': 'Test',
            }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects\
            .filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test creating a token successful for a valid user"""
        payload = {
                    'email': 'test@gbmsolucoesweb.com',
                    'name': 'Test Case',
                    'password': 'testCase123'
                    }
        create_user(**payload)
        res = self.client.post(
            GENERATE_TOKEN_USER,
            {
                'email': 'test@gbmsolucoesweb.com',
                'password': 'testCase123'
            })

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_creadentials(self):
        """Test that a toke IS NOT generated with an invalid password"""
        payload = {
                    'email': 'test@gbmsolucoesweb.com',
                    'name': 'Test Case',
                    'password': 'testCase123'
                    }
        create_user(**payload)
        res = self.client.post(
            GENERATE_TOKEN_USER,
            {
                'email': 'test@gbmsolucoesweb.com',
                'password': 'wrong'
            })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Test that no token is created for a user that does not exists
        """
        res = self.client.post(
            GENERATE_TOKEN_USER,
            {
                'email': 'nouser@gbmsolucoesweb.com',
                'password': 'nouser'
            })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_required_fields_create_token(self):
        """Test that an email and password are requireds to create a token"""
        res = self.client.post(
            GENERATE_TOKEN_USER,
            {
                'email': 'test@gbmsolucoesweb.com',
                'password': ''
            })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
