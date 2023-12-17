import random
import itertools
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import time


from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption
from datetime import datetime
from datetime import timedelta


class VotingHTMLTestCase(BaseTestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpassword', is_staff=True)
        self.q = Question.objects.create(id=1000,desc='question', type=Question.TypeChoices.OPEN_RESPONSE)
        self.q.save()
        self.a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        self.a.save()

        self.voting = Voting(id=100000, name='test voting')
        self.voting.save()
        self.voting.questions.add(self.q)
        self.voting.auths.add(self.a)
        self.voting.save()

        
    def test_create_voting(self):

        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('voting:create_voting'))

        response = self.client.post(reverse('voting:create_voting'), data={
            'name': 'Voting Name',
            'desc': 'Voting Description',
            'questions': [self.q.id],
            'auths': [self.a.id],
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Voting.objects.filter(name='Voting Name', desc='Voting Description').exists())

    def test_voting_details(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('voting:voting_details', args=[self.voting.id]))
        self.assertEqual(response.status_code, 200)

    def test_start_voting(self):
        self.client.force_login(self.admin_user)
        self.voting1 = Voting(id=100001, name='test voting')
        self.voting1.save()
        response = self.client.post(reverse('voting:start_voting', args=[self.voting1.id]))
        self.assertEqual(response.status_code, 302)
        self.voting1.refresh_from_db()
        self.assertIsNotNone(self.voting1.start_date)

    def test_stop_voting(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('voting:stop_voting', args=[self.voting.id]))
        self.assertEqual(response.status_code, 302)
        self.voting.refresh_from_db()
        self.assertIsNotNone(self.voting.end_date)

    def test_buttons_display(self):
        self.client.force_login(self.admin_user)
        url = reverse('voting:voting_details', args=[self.voting.id])
        response = self.client.get(url)
        self.assertContains(response, '<a href="/voting/start/100000" class="btn btn-primary">Empezar</a>', html=True)
        self.assertNotContains(response, '<a href="/voting/stop/100000" class="btn btn-primary">Finalizar</a>', html=True)
        self.assertNotContains(response, '<a href="/voting/tally/100000" class="btn btn-primary">Hacer recuento</a>', html=True)
        self.assertContains(response, '<a href="/visualizer/100000/" class="btn btn-primary">Visualizar</a>', html=True)

    def test_stop_button_displayed_after_start(self):
        self.client.force_login(self.admin_user)
        start_time = timezone.now() - timedelta(days=1)
        self.voting.start_date = start_time
        self.voting.save()
                       
        url = reverse('voting:voting_details', args=[self.voting.id])
        response = self.client.get(url)
        self.assertContains(response, '<a href="/voting/stop/100000" class="btn btn-primary">Finalizar</a>', html=True)

    def test_tally_button_displayed_after_stop(self):
        self.client.force_login(self.admin_user)
        start_time = timezone.now() - timedelta(days=2)
        self.voting.start_date = start_time
        self.voting.save()

        end_time = timezone.now()
        self.voting.end_date = end_time
        self.voting.save()
                       
        url = reverse('voting:voting_details', args=[self.voting.id])
        response = self.client.get(url)
        self.assertContains(response, '<a href="/voting/tally/100000" class="btn btn-primary">Hacer recuento</a>', html=True)


class VotingTestCase(BaseTestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpassword', is_staff=True)
        
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)


    def create_voting(self):
        q = Question(id=1222, desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting')
        v.save()
        v.questions.add(q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        

        return v

    def test_create_voting_with_blank_votes(self):
        q = Question(id=1234, desc='test question with blank vote', is_blank_vote_allowed=True)
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting')
        v.save()
        v.questions.add(q)

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                            defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        theres_blank_vote = False
        for questionoption in q.options.all():
            theres_blank_vote = theres_blank_vote or questionoption.option == "Blank Vote"
        if not theres_blank_vote:
            self.fail("There's no blank vote option")
      
        return v

    def test_turning_blank_option_off_removes_option(self):
        q = Question(id=1232, desc='test question with blank vote', is_blank_vote_allowed=True)
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting')
        v.save()
        v.questions.add(q)

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                        defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        q.is_blank_vote_allowed = False
        q.save()
        theres_blank_vote = False
        for questionoption in q.options.all():
            theres_blank_vote = theres_blank_vote or questionoption.option == "Blank Vote"
        if theres_blank_vote:
            self.fail("There still is a blank vote option")
        return v

    
    def create_voting_with_open_response(self):
        q = Question.objects.create(id=2,desc='test question with open response', type=Question.TypeChoices.OPEN_RESPONSE)
        q.save()
        v = Voting.objects.create(name='test voting')
        v.questions.add(q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                        defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    
    def store_votes_open_response(self,v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        respuestas = [3,3,4,1,5,1]
        diccionario_votos={}
        for respuesta in respuestas:
            if respuesta not in diccionario_votos:
                diccionario_votos[respuesta]=0
            a, b = self.encrypt_msg(respuesta, v)
            data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
            user = self.get_or_create_user(voter.voter_id)
            self.login(user=user.username)
            voter = voters.pop()
            mods.post('store', json=data)
            diccionario_votos[respuesta]+=1
        return diccionario_votos
    def store_vote_open_response_no_numeric(self,v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        respuesta = "test"
        diccionario_votos={}
        a, b = self.encrypt_msg(respuesta, v)
        data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                }
        user = self.get_or_create_user(voter.voter_id)
        self.login(user=user.username)
        voter = voters.pop()
        mods.post('store', json=data)
        diccionario_votos[respuesta]=1
        return diccionario_votos
    
    def store_vote_open_response_empty_response(self,v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        respuesta = None
        diccionario_votos={}
        a, b = self.encrypt_msg(respuesta, v)
        data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                }
        user = self.get_or_create_user(voter.voter_id)
        self.login(user=user.username)
        voter = voters.pop()
        mods.post('store', json=data)
        diccionario_votos[respuesta]=1
        return diccionario_votos
    def test_complete_voting_with_open_response(self):

        v = self.create_voting_with_open_response()
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        pregunta=v.questions.first()
        self.assertEqual(pregunta.type, Question.TypeChoices.OPEN_RESPONSE)

        self.create_voters(v)
        dic_votos=self.store_votes_open_response(v)
        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}
        
        for clave in dic_votos:
            self.assertEqual(tally.get(clave, 0), dic_votos.get(clave, 0))

    def test_complete_voting_with_open_response_no_numeric(self):

        v = self.create_voting_with_open_response()
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        pregunta=v.questions.first()
        self.assertEqual(pregunta.type, Question.TypeChoices.OPEN_RESPONSE)

        self.create_voters(v)
        with self.assertRaises(OverflowError):
            self.store_vote_open_response_no_numeric(v)

    def test_complete_voting_with_open_response_empty_response(self):

        v = self.create_voting_with_open_response()
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        pregunta=v.questions.first()
        self.assertEqual(pregunta.type, Question.TypeChoices.OPEN_RESPONSE)

        self.create_voters(v)
        with self.assertRaises(TypeError):
            self.store_vote_open_response_empty_response(v)




    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        opciones= v.questions.first().options.all()
        
        for opt in opciones:
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}
        opciones= v.questions.first().options.all()
        for q in opciones:
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])


    def test_create_voting_with_yesno_response(self):
        

        q = Question(id=82, desc='test yesno question')

        q.save()

        opt = QuestionOption(question=q, option='Si')
        opt.save()

        opt = QuestionOption(question=q, option='No')
        opt.save()


        v = Voting(name='test yesno voting')
        v.save()

        v.questions.add(q)


        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                            defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        
        
        return v



    def test_create_voting_from_api(self):
        
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        
        response = self.client.post(reverse('voting:create_voting'), data={
            'name': 'Example',
            'desc': 'Description example',
            'questions': [
                {
                    'id': 129,
                    'desc': 'I want a ',
                    'options': [
                        'cat',
                        'dog',
                        'horse'
                        
                    ]
                }
            ],
            
        })
        
        if response.status_code != 200:
            print(response.content)
        self.assertEqual(response.status_code, 200)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already tallied')

    def test_to_string(self):
        v = self.create_voting()
        self.assertEquals(str(v),"test voting")
        self.assertEquals(str(v.questions.first()),"test question")
         
    def test_yesNo_to_string(self):
        v = self.test_create_voting_with_yesno_response()
        self.assertEquals(str(v), "test yesno voting")
        self.assertEquals(str(v.questions.first()),"test yesno question")
        
        



    # def test_create_voting_API(self):
    #     self.login()
    #     data = {
    #         'name': 'Example',
    #         'desc': 'Description example',
    #         'questions': ['I want a '],
    #         'question_opt': ['cat', 'dog', 'horse']
    #     }

    #     response = self.client.post('/voting/', data, format='json')
    #     self.assertEqual(response.status_code, 201)

    #     voting = Voting.objects.get(name='Example')
    #     self.assertEqual(voting.desc, 'Description example')
    
    def test_update_voting_405(self):
        v = self.create_voting()
        data = {}  # El campo action es requerido en la request
        self.login()
        response = self.client.post('/voting/{}/'.format(v.pk), data, format='json')
        self.assertEquals(response.status_code, 405)

    

    

class LogInSuccessTests(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_successLogIn(self):
        self.driver.get(self.live_server_url+"/authentication/login-page/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.assertTrue(self.driver.current_url == self.live_server_url+"/")

class LogInErrorTests(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def usernameWrongLogIn(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("usuarioNoExistente")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[2]/div/div[1]/p').
        text == 'Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.')

    def passwordWrongLogIn(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("wrongPassword")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[2]/div/div[1]/p').
        text == 'Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.')


class QuestionsTests(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()

        options.headless = True
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)

        self.decide_user = User.objects.create_user(username='decide', password='decide')
        self.decide_user.is_staff = True
        self.decide_user.is_superuser = True
        self.decide_user.save()

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def createQuestionSuccess(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/voting/question/add/")
        
        self.cleaner.find_element(By.ID, "id_desc").click()
        self.cleaner.find_element(By.ID, "id_desc").send_keys('Test')
        self.cleaner.find_element(By.ID, "id_options-0-number").click()
        self.cleaner.find_element(By.ID, "id_options-0-number").send_keys('1')
        self.cleaner.find_element(By.ID, "id_options-0-option").click()
        self.cleaner.find_element(By.ID, "id_options-0-option").send_keys('test1')
        self.cleaner.find_element(By.ID, "id_options-1-number").click()
        self.cleaner.find_element(By.ID, "id_options-1-number").send_keys('2')
        self.cleaner.find_element(By.ID, "id_options-1-option").click()
        self.cleaner.find_element(By.ID, "id_options-1-option").send_keys('test2')
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/voting/question/")


    def testcreateYesNoQuestionSuccess(self):

        self.driver.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        self.driver.get(self.live_server_url+"/admin/voting/question/add/")
        
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys('YesNo')

        select_element = self.driver.find_element(By.ID, "id_type")

        Select(select_element).select_by_visible_text('YesNo Response')

        self.driver.find_element(By.ID, "id_id").click()
        self.driver.find_element(By.ID, "id_id").send_keys('87')

        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys('1')
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys('testYes')
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys('2')
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys('testNo')
        self.driver.find_element(By.NAME, "_save").click()

        self.driver.get(self.live_server_url + "/admin/voting/question/")
        enlace_testyesno = self.driver.find_element(By.LINK_TEXT, "YesNo")
        self.assertTrue(enlace_testyesno.is_displayed())



    def testYesNoExists(self):

        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        self.driver.get(self.live_server_url + "/admin/voting/question/add/")

        tipos_preguntas = Select(self.driver.find_element(By.ID, "id_type"))
        preguntas = [pregunta.text for pregunta in tipos_preguntas.options]

        self.assertIn("YesNo Response", preguntas)




    def testCreateDescriptionEmptyError(self):

        self.driver.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        self.driver.get(self.live_server_url+"/admin/voting/question/add/")

        select_element = self.driver.find_element(By.ID, "id_type")
        Select(select_element).select_by_visible_text('YesNo Response') 


        self.driver.find_element(By.ID, "id_id").click()
        self.driver.find_element(By.ID, "id_id").send_keys('98')

        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys('1')
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys('testYes')
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys('2')
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys('testNo')
        self.driver.find_element(By.NAME, "_save").click()

        error_noDesc = self.driver.find_element(By.XPATH, "//*[contains(text(), 'This field is required.')]")
        self.assertTrue(error_noDesc.is_displayed())




    def testStartYesNoVoting(self):
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        q = Question(id='92', desc='test yesno', type='yesno_response')
        q.save()


        options_data = [
        {'number': 1, 'option': 'testYes'},
        {'number': 2, 'option': 'testNo'},
            ]

        for data in options_data:
            option = QuestionOption(question=q, **data)
            option.save()

        v = Voting(name='test yesno voting')
        
        v.save()
        v.questions.add(q)

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        
        self.driver.get(self.live_server_url + "/admin/voting/voting/")

        # Seleccionar la casilla de "test voting"
        checkbox = self.driver.find_element(By.CLASS_NAME, "action-select")
        checkbox.click()

        # Seleccionar la acción 'Start' del menú desplegable 'Actions'
        actions_dropdown = Select(self.driver.find_element(By.NAME, 'action'))
        actions_dropdown.select_by_visible_text('Start')

        # Hacer clic en el botón 'Go'
        self.driver.find_element(By.NAME, 'index').click()

        
        v_id = Voting.objects.latest('id').id
        self.driver.get(self.live_server_url + f'/booth/{v_id}/')

        self.assertTrue(self.driver.current_url == self.live_server_url + f'/booth/{v_id}/')


    
    def createCensusEmptyError(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url+"/admin/voting/question/add/")

        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(self.cleaner.find_element_by_xpath('/html/body/div/div[3]/div/div[1]/div/form/div/p').text == 'Please correct the errors below.')
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/admin/voting/question/add/")
        


   
    
class OrderChoiceTests(StaticLiveServerTestCase):


    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()

        options.headless = True
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)

        self.decide_user = User.objects.create_user(username='decide', password='decide')
        self.decide_user.is_staff = True
        self.decide_user.is_superuser = True
        self.decide_user.save()

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    
    def testOrderChoiceVoteUnhautorized(self):
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        q = Question(id='24', desc='test question', type='order_choice')
        q.save()


        options_data = [
        {'number': 1, 'option': 'test1'},
        {'number': 2, 'option': 'test2'},
            ]

        for data in options_data:
            option = QuestionOption(question=q, **data)
            option.save()

        v = Voting(id = '233', name='test voting')
        
        v.save()
        v.questions.add(q)

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        
        self.driver.get(self.live_server_url + "/admin/voting/voting/")
        
        decide_user = User.objects.create_user(username='usertest1', password='usertest1')
        decide_user.save()


        # Seleccionar la casilla de "test voting"
        checkbox = self.driver.find_element(By.CLASS_NAME, "action-select")
        checkbox.click()

        # Seleccionar la acción 'Start' del menú desplegable 'Actions'
        actions_dropdown = Select(self.driver.find_element(By.NAME, 'action'))
        actions_dropdown.select_by_visible_text('Start')

        # Hacer clic en el botón 'Go'
        self.driver.find_element(By.NAME, 'index').click()

        
        v_id = Voting.objects.latest('id').id  
        self.driver.get(self.live_server_url + f'/booth/{v_id}/')  

    
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").send_keys("usertest1")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").send_keys("usertest1")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) > .btn").click()
        time.sleep(2)
        self.driver.find_element(By.ID, "q1").click()
        self.driver.find_element(By.ID, "q1").send_keys("1")
        self.driver.find_element(By.ID, "q2").click()
        self.driver.find_element(By.ID, "q2").send_keys("2")
        self.driver.find_element(By.CSS_SELECTOR, ".mt-3").click()
        wait = WebDriverWait(self.driver, 2)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'alert-danger')))
        
    
    def testOrderChoiceVoteAutorized(self):
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        q = Question(id='27', desc='test question', type='order_choice')
        q.save()


        options_data = [
        {'number': 1, 'option': 'test1'},
        {'number': 2, 'option': 'test2'},
            ]

        for data in options_data:
            option = QuestionOption(question=q, **data)
            option.save()

        v = Voting(id= '244',name='test voting')
        
        v.save()
        v.questions.add(q)
        decide_user = User.objects.create_user(username='usertest33', password='usertest33')
        decide_user.save()
        c = Census(voter_id= decide_user.id, voting_id=v.id)
        c.save()


        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        
        self.driver.get(self.live_server_url + "/admin/voting/voting/")
        

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        
        v_id = Voting.objects.latest('id').id  
        self.driver.get(self.live_server_url + f'/booth/{v_id}/')  

    
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").send_keys("usertest33")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").send_keys("usertest33")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) > .btn").click()
        
        time.sleep(2)
        self.driver.find_element(By.ID, "q1").click()
        self.driver.find_element(By.ID, "q1").send_keys("1")
        self.driver.find_element(By.ID, "q2").click()
        self.driver.find_element(By.ID, "q2").send_keys("2")
        self.driver.find_element(By.CSS_SELECTOR, ".mt-3").click()
        time.sleep(5)

        
    def testOrderChoiceVotingStart(self):
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        q = Question(id='27', desc='test question', type='order_choice')
        q.save()


        options_data = [
        {'number': 1, 'option': 'test1'},
        {'number': 2, 'option': 'test2'},
            ]

        for data in options_data:
            option = QuestionOption(question=q, **data)
            option.save()

        v = Voting(id='23', name='test voting')
        
        v.save()
        v.questions.add(q)

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        
        self.driver.get(self.live_server_url + "/admin/voting/voting/")
        time.sleep(1)
        
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        
        v_id = Voting.objects.latest('id').id  
        self.driver.get(self.live_server_url + f'/booth/{v_id}/')  

        self.assertTrue(self.driver.current_url == self.live_server_url + f'/booth/{v_id}/')


        
    def test_order_choice_voting(self):
        q = Question(id='34', desc='test order_choice question', type=Question.TypeChoices.ORDER_CHOICE)
        q.save()

        
        options = [
            'Option 1',
            'Option 2',
            'Option 3',
            'Option 4',
            'Option 5'
        ]

        for i, option_text in enumerate(options):
            opt = QuestionOption(question=q, option=option_text, number=i + 1)
            opt.save()

        
        v = Voting(id='27', name='test order_choice voting')
        v.save()
        v.questions.add(q)

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        
        return v
        
    def testOrderChoiceVotingExist(self):
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        self.driver.get(self.live_server_url + "/admin/voting/question/add/")

        type_dropdown = Select(self.driver.find_element(By.ID, "id_type"))
        options = [option.text for option in type_dropdown.options]

        self.assertIn("Order Choice", options)
            

            
            
    def testOrderChoiceVotingCreate(self):
        
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        self.driver.get(self.live_server_url+"/admin/voting/question/add/")
        
        type_dropdown = Select(self.driver.find_element(By.ID, "id_type"))
        type_dropdown.select_by_visible_text("Order Choice")
        
        self.driver.find_element(By.ID, "id_id").click()
        self.driver.find_element(By.ID, "id_id").send_keys('23')
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys('Test')
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys('1')
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys('test1')
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys('2')
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys('test2')
        self.driver.find_element(By.NAME, "_save").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/admin/voting/question/")
        
class VotingWithQuestionsTests(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)
        self.decide_user = User.objects.create_user(username='decide', password='decide')
        self.decide_user.is_staff = True
        self.decide_user.is_superuser = True
        self.decide_user.save()

        super().setUp()
        
        

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

    def testCreateSimpleQuestionsSuccess(self):
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)
        self.driver.find_element(By.ID, "id_username").send_keys("decide")
        self.driver.find_element(By.ID, "id_password").send_keys("decide")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_id").send_keys("123")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("simple")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("a")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("b")
        self.driver.find_element(By.ID, "id_options-2-option").click()
        self.driver.find_element(By.ID, "id_options-2-option").send_keys("c")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_id").send_keys("124")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("simple2")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("1")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("2")
        self.driver.find_element(By.NAME, "_save").click()
    
    def testCreateSimpleQuestionsFailure(self):
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)
        self.driver.find_element(By.ID, "id_username").send_keys("decide")
        self.driver.find_element(By.ID, "id_password").send_keys("decide")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_id").send_keys("123")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("a")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("b")
        self.driver.find_element(By.ID, "id_options-2-option").click()
        self.driver.find_element(By.ID, "id_options-2-option").send_keys("c")
        self.driver.find_element(By.NAME, "_save").click()
        error_noDesc = self.driver.find_element(By.XPATH, "//*[contains(text(), 'This field is required.')]")
        self.assertTrue(error_noDesc.is_displayed())

    
    def test_create_voting_with_questions_response(self):
        
        q = Question(id=82, desc='Simple question')
        q.save()

        opt = QuestionOption(question=q, option='simple a')
        opt.save()

        opt = QuestionOption(question=q, option='simple b')
        opt.save()

        q2 = Question(id=83, desc='Simple question 2')
        q2.save()

        opt = QuestionOption(question=q2, option='simple a')
        opt.save()

        opt = QuestionOption(question=q2, option='simple b')
        opt.save()

        v = Voting(name='test questions voting')
        v.save()

        v.questions.add(q)
        v.questions.add(q2)

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                            defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        
        
        return v
        
       
    def test_questions_to_string(self):
        v = self.test_create_voting_with_questions_response()
        self.assertEquals(str(v), "test questions voting")
        questions_set = v.questions.all()
        self.assertEquals(str(v.questions.first()),"Simple question")
            

    def test_Creation_Mulitple_questions_voting(self):
        q = Question(id=82, desc='simple')
        q.save()

        opt = QuestionOption(question=q, option='simple a')
        opt.save()

        opt = QuestionOption(question=q, option='simple b')
        opt.save()

        q2 = Question(id=83, desc='simple2')
        q2.save()

        opt = QuestionOption(question=q2, option='simple a')
        opt.save()

        opt = QuestionOption(question=q2, option='simple b')
        opt.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        self.driver.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)
        self.driver.find_element(By.ID, "id_username").send_keys("decide")
        self.driver.find_element(By.CSS_SELECTOR, ".form-row:nth-child(3)").click()
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, "li > .addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Multiple questions")
        dropdown = self.driver.find_element(By.ID, "id_questions")
        dropdown.find_element(By.XPATH, "//option[. = 'simple']").click()
        dropdown = self.driver.find_element(By.ID, "id_questions")
        dropdown.find_element(By.XPATH, "//option[. = 'simple2']").click()
        dropdown = self.driver.find_element(By.ID, "id_auths")
        dropdown.find_element(By.XPATH, "/html/body/div/div[3]/div/div[1]/div/form/div/fieldset/div[4]/div/div[1]/select/option[1]").click()
        self.driver.find_element(By.NAME, "_save").click()



   

