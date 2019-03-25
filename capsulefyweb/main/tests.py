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

    def test_create_modular(self):
        createcapsule = self.client.get('/newmodularcapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'TestModular',
            'modulesSize': 2,
            'emails': 'test@test.com',
            'twitter': False,
            'facebook': False,
            'description0': 'Test',
            'release_date0': '2019-10-10',
            'file0': None,
            'description1': 'Test',
            'release_date1': '2020-10-10',
            'file1': None
        }
        request = self.request_factory.post('/newmodularcapsule', data, follow=True)
        request.user = self.test_user
        createModularCapsule(request)
        capsule = Capsule.objects.filter(title='TestModular').first()
        self.assertIs(len(capsule.modules.all()), 2)
