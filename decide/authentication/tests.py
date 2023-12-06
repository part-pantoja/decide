from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User

from base import mods


class AuthTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(username='voter1')
        u.email = 'voter1@correo.com'
        u.set_password('123')
        u.save()

        u2 = User(username='admin')
        u2.set_password('admin')
        u2.email = 'admin@admin.com'
        u2.is_superuser = True
        u2.save()

    def tearDown(self):
        self.client = None

    def test_loginNuevoPorUsername(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login-page/', data)

        # Verifica que la redirección fue exitosa (código 302)
        self.assertEqual(response.status_code, 302)

        # Verifica que el usuario está autenticado
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_loginNuevoPorEmail(self):
        data = {'email': 'admin@admin.com', 'password': 'admin'}
        response = self.client.post('/authentication/login-page2/', data)

        # Verifica que la redirección fue exitosa (código 302)
        self.assertEqual(response.status_code, 302)

        # Verifica que el usuario está autenticado
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_failUsername(self):
        data = {'username': 'admin', 'password': 'admin1'}
        response = self.client.post('/authentication/login-page/', data)

        # Verifica que la página de inicio de sesión fue rendereada nuevamente (código 200)
        self.assertEqual(response.status_code, 200)

        # Verifica que el usuario no está autenticado
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_login_failEmail(self):
        data = {'username': 'admin1@us.es', 'password': 'admin'}
        response = self.client.post('/authentication/login-page/', data)

        # Verifica que la página de inicio de sesión fue rendereada nuevamente (código 200)
        self.assertEqual(response.status_code, 200)

        # Verifica que el usuario no está autenticado
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_registerNuevo(self):
        data = {'username': 'pruebaTest', 'email': 'decideuser@gmail.com', 'password1': 'decidepass123', 'password2':'decidepass123'}
        response = self.client.post('/authentication/register/', data)

        # Verifica que la redirección fue exitosa (código 302)
        self.assertEqual(response.status_code, 302)

        # Verifica que el nuevo usuario fue creado
        self.assertTrue(User.objects.filter(username='pruebaTest').exists())

    def test_registerUsuarioYaExistente(self):

        # Verifica que el usuario si esta en la base de datos
        self.assertTrue(User.objects.filter(username='admin').exists())

        data = {'username': 'admin', 'email': 'admin@admin.com', 'password1': 'admin', 'password2':'admin'}

        # Verifica la cantidad de usuarios antes de la solicitud de registro
        usuarios_antes = User.objects.count()

        response = self.client.post('/authentication/register/', data)

        # Verifica que la página de registro fue rendereada nuevamente (código 200)
        self.assertEqual(response.status_code, 200)

        # Verifica que la cantidad de usuarios después de la solicitud de registro sigue siendo la misma
        usuarios_despues = User.objects.count()
        self.assertEqual(usuarios_antes, usuarios_despues)

    def test_registerUsuarioFaltanCampos(self):

        data = {'username': 'UserPruebaTest', 'email': 'admin@admin.com', 'password1': 'decidepass123', 'password2':''}

        # Verifica la cantidad de usuarios antes de la solicitud de registro
        usuarios_antes = User.objects.count()

        response = self.client.post('/authentication/register/', data)

        # Verifica que la página de registro fue rendereada nuevamente (código 200)
        self.assertEqual(response.status_code, 200)

        # Verifica que la cantidad de usuarios después de la solicitud de registro sigue siendo la misma
        usuarios_despues = User.objects.count()
        self.assertEqual(usuarios_antes, usuarios_despues)

        # Verifica que el nuevo usuario no fue creado
        self.assertFalse(User.objects.filter(username='UserPruebaTest').exists())
        
'''
    def test_login(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_fail(self):
        data = {'username': 'voter1', 'password': '321'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user['id'], 1)
        self.assertEqual(user['username'], 'voter1')

    def test_getuser_invented_token(self):
        token = {'token': 'invented'}
        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_getuser_invalid_token(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 0)

    def test_register_bad_permissions(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 401)

    def test_register_bad_request(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_user_already_exist(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update(data)
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1', 'password': 'pwd1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            sorted(list(response.json().keys())),
            ['token', 'user_pk']
        )
'''