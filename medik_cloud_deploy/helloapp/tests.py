# helloapp tests.py

from django.test import SimpleTestCase, Client

from django.test import TestCase
from django.urls import reverse
from .models import MedApplicant


class MedApplicantTestCase(TestCase):
    def test_signup(self):
        data = {
            'student_name': 'Test User',
            'student_email': 'test@example.com',
            'password': 'testpassword123',
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User registered successfully')
        print(response.content)  # If you want to see the content in the console
