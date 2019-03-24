from django.test import TestCase
from .models import User, Capsule
from django.test.client import RequestFactory
from .views import *


class SimpleTest(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.username = 'testuser'
        self.email = 'testuser@test.com'
        self.password = 'testpass'
        self.test_user = User.objects.create_user(self.username, self.email, self.password, birthdate='2001-01-01')
        login = self.client.login(username=self.username, password=self.password)
        self.assertEqual(login, True)

    def test_create(self):
        createcapsule = self.client.get('/newfreecapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'Test',
            'description': 'Test',
            'release_date': '2019-10-10',
            'emails': 'test@test.com',
            'twitter': False,
            'facebook': False,
            'file': None
        }
        request = self.request_factory.post('/newfreecapsule', data, follow=True)
        request.user = self.test_user
        createFreeCapsule(request)
        capsule = Capsule.objects.filter(emails='test@test.com').first()
        self.assertIsNotNone(capsule)
