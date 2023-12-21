from django.test import TestCase
from django.contrib.auth.models import User
from voting.models import Voting, Question
from census.models import Census
from request.models import Request, RequestStatus
from django.shortcuts import reverse
# Create your tests here.

class CreateRequestTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpassword', is_staff=True)
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        q = Question(id=1001, desc='test question')
        q.save()
        self.votacion = Voting(name='test voting')
        self.votacion.save()
        self.votacion.questions.add(q)
        self.votacion.save()

    def test_create_request_success(self):
        # Prueba crear una solicitud con éxito
        self.client.force_login(self.user)
        response = self.client.get(reverse('request:create_request', args=[self.votacion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Solicitud creada con éxito.')

        # Verifica que la solicitud realmente se ha creado
        self.assertTrue(Request.objects.filter(voter_id=self.user.id, voting_id=self.votacion.id).exists())

    def test_create_request_already_in_census(self):
        # Prueba crear una solicitud cuando el usuario ya está en el censo
        Census.objects.create(voter_id=self.user.id, voting_id=self.votacion.id)

        self.client.force_login(self.user)
        response = self.client.get(reverse('request:create_request', args=[self.votacion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ya estás en el censo de esta votación.')

        # Verifica que la solicitud no se ha creado
        self.assertFalse(Request.objects.filter(voter_id=self.user.id, voting_id=self.votacion.id).exists())

    def test_create_request_pending_request(self):
        # Prueba crear una solicitud cuando ya hay una solicitud pendiente
        Request.objects.create(voter_id=self.user.id, voting_id=self.votacion.id, status=RequestStatus.PENDING.value)

        self.client.force_login(self.user)
        response = self.client.get(reverse('request:create_request', args=[self.votacion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ya tienes una request para esta votación.')

    def test_create_request_declined_request(self):
        # Prueba crear una solicitud cuando ya hay una solicitud rechazada
        Request.objects.create(voter_id=self.user.id, voting_id=self.votacion.id, status=RequestStatus.DECLINED.value)

        self.client.force_login(self.user)
        response = self.client.get(reverse('request:create_request', args=[self.votacion.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lo sentimos, tu solicitud ha sido rechazada.')

    def doble_veri(self):
        self.assertTrue()

class ManageRequestTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpassword', email='decidepartpantoja@gmail.com', is_staff=True)
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='decidepartpantoja@gmail.com')
        q = Question(id=423, desc='test question')
        q.save()
        self.votacion = Voting(name='test voting')
        self.votacion.save()
        self.votacion.questions.add(q)
        self.votacion.save()
        self.request_pending = Request.objects.create(voter_id=self.user.id, voting_id=self.votacion.id, status=RequestStatus.PENDING.value)

    def test_manage_request_accept_request(self):
        self.client.force_login(self.admin_user)

        # Prueba aceptar una solicitud pendiente
        response = self.client.post(reverse('request:manage_request'), {'aceptar': self.request_pending.id})
        self.assertEqual(response.status_code, 302)  # Se espera redirección después de procesar la solicitud
        self.assertRedirects(response, reverse('request:manage_request'))

        # Verifica que el estado de la solicitud se ha actualizado
        self.request_pending.refresh_from_db()
        self.assertEqual(self.request_pending.status, RequestStatus.ACCEPTED.value)

        # Verifica que se ha creado una entrada en el censo
        self.assertTrue(Census.objects.filter(voting_id=self.votacion.id, voter_id=self.user.id).exists())

    def test_manage_request_decline_request(self):
        self.client.force_login(self.admin_user)

        # Prueba declinar una solicitud pendiente
        response = self.client.post(reverse('request:manage_request'), {'declinar': self.request_pending.id})
        self.assertEqual(response.status_code, 302)  # Se espera redirección después de procesar la solicitud
        self.assertRedirects(response, reverse('request:manage_request'))

        # Verifica que el estado de la solicitud se ha actualizado
        self.request_pending.refresh_from_db()
        self.assertEqual(self.request_pending.status, RequestStatus.DECLINED.value)
