from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from base import mods


class BaseTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.token = None
        mods.mock_query(self.client)

        user_noadmin = User(username='noadmin')
        user_noadmin.set_password('qwerty')
        user_noadmin.save()

        user_admin = User(username='admin', is_staff=True)
        user_admin.set_password('qwerty')
        user_admin.save()

    def tearDown(self):
        self.client = None
        self.token = None

    def login(self, user='admin', password='qwerty'):
        data = {'username': user, 'password': password}
        #response = mods.post('authentication/login-page', json=data, response=True)
        response = self.client.post('/authentication/login-page/', data, response=True)
        self.assertEqual(response.status_code, 302)

        user2 = User.objects.filter(username=user).get()
        token, _ = Token.objects.get_or_create(user=user2)
        self.token = token.key
        
        self.assertTrue(self.token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        #response = self.client.post('/authentication/login-page/', data)
        #self.assertEqual(response.status_code, 302)
        #token, _ = Token.objects.get_or_create(user=usuario)
        #self.assertTrue(response.wsgi_request.user.is_authenticated)

    def logout(self):
        self.client.credentials()
