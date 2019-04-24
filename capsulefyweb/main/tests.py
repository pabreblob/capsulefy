from django.test import TestCase

from main import views
from .models import User, Capsule
from django.test.client import RequestFactory
from .views import *
from .logic import remove_expired_capsules
from dateutil.relativedelta import relativedelta
import  datetime
class SimpleTest(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.username = 'testuser'
        self.email = 'testuser@test.com'
        self.password = 'testpass'
        self.test_user = User.objects.create_user(self.username, self.email, self.password, birthdate='2001-01-01')
        login = self.client.login(username=self.username, password=self.password)
        self.assertEqual(login, True)


    def test_create_free(self):
        createcapsule = self.client.get('/newfreecapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'Test',
            'description': 'Test',
            'release_date': '2019-10-10',
            'emails': 'test@test.com',
            'twitter': False,
            'facebook': False
            #'file': None
        }
        request = self.request_factory.post('/newfreecapsule', data, follow=True)
        request.user = self.test_user
        createFreeCapsule(request)
        capsule = Capsule.objects.filter(emails='test@test.com').first()
        self.assertIsNotNone(capsule)
        self.assertEqual(capsule.title, data['title'])
        self.assertEqual(capsule.modules.first().description, data['description'])
        self.assertEqual(capsule.modules.first().release_date.strftime('%Y-%m-%d'), data['release_date'])
        self.assertEqual(capsule.emails, data['emails'])
        self.assertEqual(capsule.twitter, data['twitter'])
        self.assertEqual(capsule.facebook, data['facebook'])

    def test_edit_free(self):
        createcapsule = self.client.get('/newfreecapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'Test',
            'description': 'Test',
            'release_date': '2019-10-10',
            'emails': 'test@test.com',
            'twitter': False,
            'facebook': False
            #'file': None
        }
        request = self.request_factory.post('/newfreecapsule', data, follow=True)
        request.user = self.test_user
        createFreeCapsule(request)
        capsule = Capsule.objects.filter(emails='test@test.com').first()
        self.assertIsNotNone(capsule)
        newdata = {
            'title': 'TestEdited',
            'description': 'Test was edited',
            'release_date': '2019-10-20',
            'emails': 'test@tested.com',
            'twitter': False,
            'facebook': True
            #'file': None
        }
        editrequest = self.request_factory.post('/editfreecapsule/' + str(capsule.id), newdata, follow=True)
        editrequest.user = self.test_user
        editFreeCapsule(editrequest, capsule.id)
        editedcapsule = Capsule.objects.filter(id=capsule.id).first()
        self.assertIsNotNone(editedcapsule)
        self.assertEqual(editedcapsule.title, newdata['title'])
        self.assertEqual(editedcapsule.modules.first().description, newdata['description'])
        self.assertEqual(editedcapsule.modules.first().release_date.strftime('%Y-%m-%d'), newdata['release_date'])
        self.assertEqual(editedcapsule.emails, newdata['emails'])
        self.assertEqual(editedcapsule.twitter, newdata['twitter'])
        self.assertEqual(editedcapsule.facebook, newdata['facebook'])

    def test_delete_free(self):
        createcapsule = self.client.get('/newfreecapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'Test',
            'description': 'Test',
            'release_date': '2019-10-10',
            'emails': 'test@test.com',
            'twitter': False,
            'facebook': False
            #'file': None
        }
        request = self.request_factory.post('/newfreecapsule', data, follow=True)
        request.user = self.test_user
        createFreeCapsule(request)
        capsule = Capsule.objects.filter(emails='test@test.com').first()
        self.assertIsNotNone(capsule)
        delrequest = self.request_factory.get('/deletecapsule/' + str(capsule.id), follow=True)
        delrequest.user = self.test_user
        deleteCapsule(delrequest, capsule.id)
        delcapsule = Capsule.objects.filter(id=capsule.id).first()
        self.assertIsNone(delcapsule)

    def test_create_modular_capsule(self):
        # Creating a new modular capsule
        views.testMode = True
        createcapsule = self.client.get('/newmodularcapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'TestModular',
            'emails': 'test@test.com',
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'twitter': False,
            'facebook': False,
            'private': False,
            'form-0-description': 'Modulo1',
            'form-0-release_date': '2019-10-10',
            'form-1-description': 'Modulo2',
            'form-1-release_date': '2020-10-10'
        }
        request = self.request_factory.post('/newmodularcapsule', data, follow=True)
        request.user = self.test_user
        createModularCapsule(request)
        capsule = Capsule.objects.filter(title='TestModular').first()
        self.assertIsNotNone(capsule)
        self.assertEqual(capsule.title, data['title'])
        self.assertEqual(capsule.emails, data['emails'])
        self.assertEqual(capsule.twitter, data['twitter'])
        self.assertEqual(capsule.facebook, data['facebook'])
        self.assertIs(len(capsule.modules.all()), 2)
        views.testMode = False

    def test_edit_modular_capsule(self):
        #Creating a new modular capsule
        views.testMode = True
        createcapsule = self.client.get('/newmodularcapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'TestModular',
            'emails': 'test@test.com',
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'twitter': False,
            'facebook': False,
            'private': False,
            'form-0-description': 'Modulo1',
            'form-0-release_date': '2019-10-10',
            'form-1-description': 'Modulo2',
            'form-1-release_date': '2020-10-10'
        }
        request = self.request_factory.post('/newmodularcapsule', data, follow=True)
        request.user = self.test_user
        createModularCapsule(request)
        capsule = Capsule.objects.filter(title='TestModular').first()
        self.assertIs(len(capsule.modules.all()), 2)
        views.testMode = False
        #Editing a modular capsule
        editcapsule = self.client.get('/editmodularcapsule/'+str(capsule.id), follow=True)
        self.assertEquals(editcapsule.status_code, 200)
        data = {
            'title': 'TestModular',
            'emails': 'test@test.com',
            'twitter': False,
            'facebook': False,
            'private': True
        }
        request = self.request_factory.post('/editmodularcapsule/'+str(capsule.id), data, follow=True)
        request.user = self.test_user
        editModularCapsule(request, capsule.id)
        capsule = Capsule.objects.filter(title='TestModular').first()
        self.assertTrue(capsule.private)

    def test_create_module(self):
        # Creating a new modular capsule
        views.testMode = True
        createcapsule = self.client.get('/newmodularcapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'TestModular',
            'emails': 'test@test.com',
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'twitter': False,
            'facebook': False,
            'private': False,
            'form-0-description': 'Modulo1',
            'form-0-release_date': '2019-10-10',
            'form-1-description': 'Modulo2',
            'form-1-release_date': '2020-10-10'
        }
        request = self.request_factory.post('/newmodularcapsule', data, follow=True)
        request.user = self.test_user
        createModularCapsule(request)
        capsule = Capsule.objects.filter(title='TestModular').first()
        self.assertIs(len(capsule.modules.all()), 2)
        views.testMode = False
        #Creating a module
        createcapsule = self.client.get('/newmodule/' + str(capsule.id), follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'description': 'Module3',
            'release_date': '2019-10-10'
            #'file': None
        }
        request = self.request_factory.post('/newmodule/'+str(capsule.id), data, follow=True)
        request.user = self.test_user
        createModule(request, capsule.id)
        capsule = Capsule.objects.filter(title='TestModular').first()
        self.assertIs(len(capsule.modules.all()), 3)

    def test_edit_module(self):
        # Creating a new modular capsule
        views.testMode = True
        createcapsule = self.client.get('/newmodularcapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'TestModular',
            'emails': 'test@test.com',
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'twitter': False,
            'facebook': False,
            'private': False,
            'form-0-description': 'Modulo1',
            'form-0-release_date': '2019-10-10',
            'form-1-description': 'Modulo2',
            'form-1-release_date': '2020-10-10'
        }
        request = self.request_factory.post('/newmodularcapsule', data, follow=True)
        request.user = self.test_user
        createModularCapsule(request)
        capsule = Capsule.objects.filter(title='TestModular').first()
        self.assertIs(len(capsule.modules.all()), 2)
        views.testMode = False
        # Creating a module
        createcapsule = self.client.get('/newmodule/' + str(capsule.id), follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'description': 'Module3',
            'release_date': '2019-10-10'
            #'file': None
        }
        request = self.request_factory.post('/newmodule/' + str(capsule.id), data, follow=True)
        request.user = self.test_user
        createModule(request, capsule.id)
        capsule = Capsule.objects.filter(title='TestModular').first()
        self.assertIs(len(capsule.modules.all()), 3)

        # Editing a module
        module = Module.objects.filter(description="Module3").first()
        editcapsule = self.client.get('/editmodule/' + str(module.id), follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'description': 'Module3Modified',
            'release_date': '2019-10-10'
            #'file': None
        }
        request = self.request_factory.post('/editmodule/' + str(module.id), data, follow=True)
        request.user = self.test_user
        editModule(request, module.id)
        module = Module.objects.all().get(id=module.id)
        self.assertTrue(module.description=="Module3Modified")

    def test_delete_module(self):
        # Creating a new modular capsule
        views.testMode= True
        createcapsule = self.client.get('/newmodularcapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'TestModular',
            'emails': 'test@test.com',
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'twitter': False,
            'facebook': False,
            'private': False,
            'form-0-description': 'Modulo1',
            'form-0-release_date': '2019-10-10',
            'form-1-description': 'Modulo2',
            'form-1-release_date': '2020-10-10'
        }
        request = self.request_factory.post('/newmodularcapsule', data, follow=True)
        request.user = self.test_user
        createModularCapsule(request)
        capsule = Capsule.objects.filter(title='TestModular').first()
        self.assertIs(len(capsule.modules.all()), 2)
        views.testMode = False
        # Creating a module
        createcapsule = self.client.get('/newmodule/' + str(capsule.id), follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'description': 'Module3',
            'release_date': '2019-10-10',
            #'file': None
        }
        request = self.request_factory.post('/newmodule/' + str(capsule.id), data, follow=True)
        request.user = self.test_user
        createModule(request, capsule.id)
        capsule = Capsule.objects.filter(title='TestModular').first()
        self.assertIs(len(capsule.modules.all()), 3)

        # Deleting a module
        module = Module.objects.filter(description="Module3").first()
        request = self.request_factory.post('/deletemodule/' + str(module.id), follow=True)
        request.user = self.test_user
        deleteModule(request, module.id)
        self.assertIs(len(capsule.modules.all()), 2)

    def test_delete_modular_capsule(self):
        # Creating a new modular capsule
        views.testMode = True
        createcapsule = self.client.get('/newmodularcapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'TestModular',
            'emails': 'test@test.com',
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'twitter': False,
            'facebook': False,
            'private': False,
            'form-0-description': 'Modulo1',
            'form-0-release_date': '2019-10-10',
            'form-1-description': 'Modulo2',
            'form-1-release_date': '2020-10-10'
        }
        request = self.request_factory.post('/newmodularcapsule', data, follow=True)
        request.user = self.test_user
        createModularCapsule(request)
        capsule = Capsule.objects.filter(title='TestModular').first()
        self.assertIs(len(capsule.modules.all()), 2)
        views.testMode = False
        # Deleting a capsule
        capsule = Capsule.objects.filter(title='TestModular').first()
        request = self.request_factory.post('/deletecapsule/' + str(capsule.id), follow=True)
        request.user = self.test_user
        deleteCapsule(request, capsule.id)
        self.assertIs(Capsule.objects.filter(title='TestModular').first(), None)

    def test_remove_expired(self):
        createcapsule = self.client.get('/newfreecapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'Test',
            'description': 'Test',
            'release_date': '2019-10-10',
            'emails': 'test@test.com',
            'twitter': False,
            'facebook': False,
            'capsule_type':'F'
        }
        request = self.request_factory.post('/newfreecapsule', data, follow=True)
        request.user = self.test_user
        createFreeCapsule(request)
        capsule = Capsule.objects.filter(emails='test@test.com').first()
        self.assertIsNotNone(capsule)
        module = Module.objects.filter(capsule_id=capsule.id).first()
        module.release_date=datetime.datetime.now(timezone.utc)-relativedelta(months=6)
        module.save()
        remove_expired_capsules()
        delcapsule = Capsule.objects.filter(id=capsule.id).first()
        self.assertIsNone(delcapsule)

    def test_display_capsule_free(self):
        #Creation of a capsule
        createcapsule = self.client.get('/newfreecapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'Test',
            'description': 'Test',
            'release_date': '2019-10-10',
            'emails': 'test@test.com',
            'twitter': False,
            'facebook': False
            # 'file': None
        }
        request = self.request_factory.post('/newfreecapsule', data, follow=True)
        request.user = self.test_user
        createFreeCapsule(request)
        capsule = Capsule.objects.filter(emails='test@test.com').first()
        self.assertIsNotNone(capsule)
        self.assertEqual(capsule.title, data['title'])
        self.assertEqual(capsule.modules.first().description, data['description'])
        self.assertEqual(capsule.modules.first().release_date.strftime('%Y-%m-%d'), data['release_date'])
        self.assertEqual(capsule.emails, data['emails'])
        self.assertEqual(capsule.twitter, data['twitter'])
        self.assertEqual(capsule.facebook, data['facebook'])
        request = self.request_factory.get('/displaycapsule/')
        request.user = self.test_user

        response = displayCapsules(request, capsule.id)
        self.assertEquals(response.status_code, 200)

    def test_display_capsule_notpublished(self):
        #Creation of a capsule
        createcapsule = self.client.get('/newfreecapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'Test',
            'description': 'Test',
            'release_date': '2019-10-10',
            'emails': 'test@test.com',
            'twitter': False,
            'facebook': False
            # 'file': None
        }
        request = self.request_factory.post('/newfreecapsule', data, follow=True)
        request.user = self.test_user
        createFreeCapsule(request)
        capsule = Capsule.objects.filter(emails='test@test.com').first()
        self.assertIsNotNone(capsule)
        self.assertEqual(capsule.title, data['title'])
        self.assertEqual(capsule.modules.first().description, data['description'])
        self.assertEqual(capsule.modules.first().release_date.strftime('%Y-%m-%d'), data['release_date'])
        self.assertEqual(capsule.emails, data['emails'])
        self.assertEqual(capsule.twitter, data['twitter'])
        self.assertEqual(capsule.facebook, data['facebook'])

        self.request_factory = RequestFactory()
        self.username = 'testuser2'
        self.email = 'testuser2@test.com'
        self.password = 'testpass2'
        self.test_user2 = User.objects.create_user(self.username, self.email, self.password, birthdate='2001-01-01')
        login = self.client.login(username=self.username, password=self.password)

        request = self.request_factory.get('/displaycapsule/')
        request.user= self.test_user2
        response = displayCapsules(request, capsule.id)
        self.assertEquals(response.status_code, 404)

    def test_display_capsule_notpaid(self):
        #Creation of a capsule
        views.testMode = True
        createcapsule = self.client.get('/newmodularcapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'TestDisplay',
            'emails': 'test@test.com',
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'twitter': False,
            'facebook': False,
            'private': False,
            'form-0-description': 'Modulo1',
            'form-0-release_date': '2019-10-10',
            'form-1-description': 'Modulo2',
            'form-1-release_date': '2020-10-10'
        }
        request = self.request_factory.post('/newmodularcapsule', data, follow=True)
        request.user = self.test_user
        createModularCapsule(request)
        capsule = Capsule.objects.filter(title='TestDisplay').first()
        self.assertIsNotNone(capsule)
        self.assertEqual(capsule.title, data['title'])
        self.assertEqual(capsule.emails, data['emails'])
        self.assertEqual(capsule.twitter, data['twitter'])
        self.assertEqual(capsule.facebook, data['facebook'])
        self.assertIs(len(capsule.modules.all()), 2)
        views.testMode = False

        request = self.request_factory.get('/displaycapsule/')
        request.user = self.test_user

        response = displayCapsules(request, capsule.id)
        self.assertEquals(response.status_code, 404)

    def test_select_capsule(self):
        createcapsule = self.client.get('/select_capsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)

    def test_refresh_deadman(self):
        # Creation of a capsule
        views.testMode = True
        createcapsule = self.client.get('/newmodularcapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'TestRefresh',
            'emails': 'test@test.com',
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'twitter': False,
            'facebook': False,
            'private': False,
            'form-0-description': 'Modulo1',
            'form-0-release_date': '2019-10-10',
        }
        request = self.request_factory.post('/newmodularcapsule', data, follow=True)
        request.user = self.test_user
        createModularCapsule(request)
        capsule = Capsule.objects.filter(title='TestRefresh').first()
        self.assertIsNotNone(capsule)
        self.assertEqual(capsule.title, data['title'])
        self.assertEqual(capsule.emails, data['emails'])
        self.assertEqual(capsule.twitter, data['twitter'])
        self.assertEqual(capsule.facebook, data['facebook'])
        self.assertIs(len(capsule.modules.all()), 1)
        views.testMode = False

        capsule.dead_man_counter = 300
        capsule.dead_man_initial_counter = 500
        capsule.dead_man_switch = True
        capsule.save()
        capsule = Capsule.objects.filter(title='TestRefresh').first()
        self.assertEquals(capsule.dead_man_counter, 300)
        request = self.request_factory.get('/refresh/')
        request.user = self.test_user
        response = refresh_deadman(request, capsule.id)
        capsule = Capsule.objects.filter(title='TestRefresh').first()
        self.assertEquals(capsule.dead_man_counter, 500)

    def test_refresh_deadman_notowner(self):
        # Creation of a capsule
        views.testMode = True
        createcapsule = self.client.get('/newmodularcapsule', follow=True)
        self.assertEquals(createcapsule.status_code, 200)
        data = {
            'title': 'TestRefresh',
            'emails': 'test@test.com',
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'twitter': False,
            'facebook': False,
            'private': False,
            'form-0-description': 'Modulo1',
            'form-0-release_date': '2019-10-10',
        }
        request = self.request_factory.post('/newmodularcapsule', data, follow=True)
        request.user = self.test_user
        createModularCapsule(request)
        capsule = Capsule.objects.filter(title='TestRefresh').first()
        self.assertIsNotNone(capsule)
        self.assertEqual(capsule.title, data['title'])
        self.assertEqual(capsule.emails, data['emails'])
        self.assertEqual(capsule.twitter, data['twitter'])
        self.assertEqual(capsule.facebook, data['facebook'])
        self.assertIs(len(capsule.modules.all()), 1)
        views.testMode = False
        self.username = 'testuser2'
        self.email = 'testuser2@test.com'
        self.password = 'testpass2'
        self.test_user2 = User.objects.create_user(self.username, self.email, self.password, birthdate='2001-01-01')
        login = self.client.login(username=self.username, password=self.password)
        request = self.request_factory.get('/refresh/')
        request.user = self.test_user2
        response = refresh_deadman(request, capsule.id)
        self.assertEquals(response.status_code, 404)
