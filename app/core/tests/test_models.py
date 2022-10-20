"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        username = 'test1123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            username=username,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com', 'test1', 'testpass123'],
            ['Test2@Example.com', 'Test2@example.com', 'test2', 'testpass123'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com', 'test3', 'testpass123'],
            ['test4@example.COM', 'test4@example.com', 'test4', 'testpass123'],
        ]
        for email, expected, username, password in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
            )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        password = 'testpass123'
        username = 'test1123'
        email = ''
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
            )

    def test_new_user_without_username_raises_error(self):
        """Test that creating a user without usename raises a ValueError."""
        password = 'testpass123'
        username = ''
        email = 'test123@test.com'
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
            )

    def test_new_user_without_password_raises_error(self):
        """Test that creating a user without password raises a ValueError."""
        password = ''
        username = 'test1123'
        email = 'test123@test.com'
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
            )

    def test_create_superuser(self):
        """Test creating a superuser"""
        email = 'test@example.com'
        password = 'testpass123'
        username = 'test1123'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
            username=username,
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_store(self):
        """Test creating a store is successful."""
        user = get_user_model().objects.create_user(
                email='test@example.com',
                password='testpassword',
                username='testusername',
        )
        store = models.Store.objects.create(
            user=user,
            name="Whole Foods",
        )
        self.assertEqual(str(store), store.name)

    def test_create_grocery(self):
        """Test creating a grocery"""
        user = get_user_model().objects.create_user(
                email='test@example.com',
                password='testpassword',
                username='testusername',
        )
        grocery = models.Grocery.objects.create(
            user=user,
            name="tacos"
        )
        self.assertEqual(str(grocery), grocery.name)
