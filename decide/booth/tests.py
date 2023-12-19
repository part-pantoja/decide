from django.test import TestCase
from base.tests import BaseTestCase
from django.contrib.auth.models import User
from voting.models import Voting, Question, QuestionOption
from census.models import Census
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

# Create your tests here.

class BoothTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        super().login()
    def tearDown(self):
        super().tearDown()
    def testBoothNotFound(self):
        
        # Se va a probar con el numero 10000 pues en las condiciones actuales en las que nos encontramos no parece posible que se genren 10000 votaciones diferentes
        response = self.client.get('/booth/10000/')
        self.assertEqual(response.status_code, 404)
    
    def testBoothRedirection(self):
        
        # Se va a probar con el numero 10000 pues en las condiciones actuales en las que nos encontramos no parece posible que se genren 10000 votaciones diferentes
        response = self.client.get('/booth/10000')
        self.assertEqual(response.status_code, 301)
    
    def test_booth_no_votings(self):
        super().login(user='noadmin')
        response = self.client.get(reverse('booth:booth_home'), {'filtro': 'todas'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['votings'], [])

    def test_booth_home_all_user_votings(self):
        u = User.objects.get(username='noadmin')
        super().login(user='noadmin')
        # Crear votaciones de prueba
        q = Question(id=1234, desc='test question')
        q.save()

        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i))
            opt.save()

        v1 = Voting(name='test voting 1')
        v1.save()
        v1.questions.add(q)
        v1.start_date = timezone.now() - timedelta(days=1)
        v1.end_date = timezone.now()
        v1.save()

        v2 = Voting(name='test voting 2')
        v2.save()
        v2.questions.add(q)
        v2.start_date = timezone.now() - timedelta(days=2)
        v2.end_date = timezone.now() - timedelta(days=1)
        v2.save()

        v3 = Voting(name='test voting 3')
        v3.save()
        v3.questions.add(q)
        v3.start_date = timezone.now()
        v3.save()

        v4 = Voting(name='test voting 4')
        v4.save()
        v4.questions.add(q)
        v4.start_date = timezone.now()
        v4.save()

        votings = [v1, v2, v3]
    
        # Crear censos de prueba
        censo1 = Census(voting_id=v1.id, voter_id=u.id)
        censo1.save()

        censo2 = Census(voting_id=v2.id, voter_id=u.id)
        censo2.save()

        censo3 = Census(voting_id=v3.id, voter_id=u.id)
        censo3.save()

        # Llamar a la vista booth_home
        response = self.client.get(reverse('booth:booth_home'), {'filtro': 'todas'})
        self.assertEqual(response.status_code, 200)

        # Obtener los nombres de las votaciones en la respuesta
        voting_ids_in_response = [v['name'] for v in response.context['votings']]

        # Obtener los nombres de las votaciones creadas en la prueba
        voting_ids_in_test = [v.name for v in votings]

        # Comprobar que se devuelven todas las votaciones
        self.assertCountEqual(voting_ids_in_response, voting_ids_in_test)

    def test_booth_home_just_available_user_votings(self):
        u = User.objects.get(username='noadmin')
        super().login(user='noadmin')
        # Crear votaciones de prueba
        q = Question(id= 12, desc='test question')
        q.save()

        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i))
            opt.save()

        v1 = Voting(name='test voting 1')
        v1.save()
        v1.questions.add(q)
        v1.start_date = timezone.now() - timedelta(days=1)
        v1.end_date = timezone.now()
        v1.save()

        v2 = Voting(name='test voting 2')
        v2.save()
        v2.questions.add(q)
        v2.start_date = timezone.now() - timedelta(days=2)
        v2.end_date = timezone.now() - timedelta(days=1)
        v2.save()

        v3 = Voting(name='test voting 3')
        v3.save()
        v3.questions.add(q)
        v3.start_date = timezone.now()
        v3.save()

        v4 = Voting(name='test voting 4')
        v4.save()
        v4.questions.add(q)
        v4.start_date = timezone.now()
        v4.save()

        votings = [v3, v4]
    
        # Crear censos de prueba
        censo1 = Census(voting_id=v1.id, voter_id=u.id)
        censo1.save()

        censo2 = Census(voting_id=v2.id, voter_id=u.id)
        censo2.save()

        censo3 = Census(voting_id=v3.id, voter_id=u.id)
        censo3.save()

        censo4 = Census(voting_id=v4.id, voter_id=u.id)
        censo4.save()

        # Llamar a la vista booth_home
        response = self.client.get(reverse('booth:booth_home'), {'filtro': 'disponibles'})
        self.assertEqual(response.status_code, 200)

        # Obtener los nombres de las votaciones en la respuesta
        voting_ids_in_response = [v['name'] for v in response.context['votings']]

        # Obtener los nombres de las votaciones creadas en la prueba
        voting_ids_in_test = [v.name for v in votings]

        # Comprobar que se devuelven todas las votaciones
        self.assertCountEqual(voting_ids_in_response, voting_ids_in_test)

    def test_booth_home_not_initialized_user_votings(self):
        u = User.objects.get(username='noadmin')
        super().login(user='noadmin')
        # Crear votaciones de prueba
        q = Question(id=13, desc='test question')
        q.save()

        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i))
            opt.save()

        v1 = Voting(name='test voting 1')
        v1.save()
        v1.questions.add(q)
        v1.save()

        v2 = Voting(name='test voting 2')
        v2.save()
        v2.questions.add(q)
        v2.start_date = timezone.now() - timedelta(days=1)
        v2.end_date = timezone.now()
        v2.save()

        v3 = Voting(name='test voting 3')
        v3.save()
        v3.questions.add(q)
        v3.start_date = timezone.now()
        v3.save()

        v4 = Voting(name='test voting 4')
        v4.save()
        v4.questions.add(q)
        v4.save()

        votings = [v1, v4]
    
        # Crear censos de prueba
        censo1 = Census(voting_id=v1.id, voter_id=u.id)
        censo1.save()

        censo2 = Census(voting_id=v2.id, voter_id=u.id)
        censo2.save()

        censo3 = Census(voting_id=v3.id, voter_id=u.id)
        censo3.save()

        censo4 = Census(voting_id=v4.id, voter_id=u.id)
        censo4.save()

        # Llamar a la vista booth_home
        response = self.client.get(reverse('booth:booth_home'), {'filtro': 'no_iniciadas'})
        self.assertEqual(response.status_code, 200)

        # Obtener los nombres de las votaciones en la respuesta
        voting_ids_in_response = [v['name'] for v in response.context['votings']]

        # Obtener los nombres de las votaciones creadas en la prueba
        voting_ids_in_test = [v.name for v in votings]

        # Comprobar que se devuelven todas las votaciones
        self.assertCountEqual(voting_ids_in_response, voting_ids_in_test)

    def test_booth_home_other_users_votings(self):
        u = User.objects.get(username='noadmin')
        super().login(user='noadmin')
        # Crear votaciones de prueba
        q = Question(id=15, desc='test question')
        q.save()

        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i))
            opt.save()

        v1 = Voting(name='test voting 1')
        v1.save()
        v1.questions.add(q)
        v1.start_date = timezone.now()
        v1.save()

        v2 = Voting(name='test voting 2')
        v2.save()
        v2.questions.add(q)
        v2.start_date = timezone.now()
        v2.save()

        v3 = Voting(name='test voting 3')
        v3.save()
        v3.questions.add(q)
        v3.start_date = timezone.now()
        v3.save()

        v4 = Voting(name='test voting 4')
        v4.save()
        v4.questions.add(q)
        v4.start_date = timezone.now()
        v4.save()

        votings = [v4]
    
        # Crear censos de prueba
        censo1 = Census(voting_id=v1.id, voter_id=2)
        censo1.save()

        censo2 = Census(voting_id=v2.id, voter_id=1)
        censo2.save()

        censo3 = Census(voting_id=v3.id, voter_id=1)
        censo3.save()

        censo4 = Census(voting_id=v4.id, voter_id=u.id)
        censo4.save()

        # Llamar a la vista booth_home
        response = self.client.get(reverse('booth:booth_home'), {'filtro': 'todas'})
        self.assertEqual(response.status_code, 200)

        # Obtener los nombres de las votaciones en la respuesta
        voting_ids_in_response = [v['name'] for v in response.context['votings']]

        # Obtener los nombres de las votaciones creadas en la prueba
        voting_ids_in_test = [v.name for v in votings]

        # Comprobar que se devuelven todas las votaciones
        self.assertCountEqual(voting_ids_in_response, voting_ids_in_test)