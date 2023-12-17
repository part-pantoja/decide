from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from base.tests import BaseTestCase
from census.models import Census

from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption


from django.contrib.auth.models import User

class AdminTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.headless = False
        self.driver = webdriver.Chrome(options=options)
        User.objects.create_superuser('admin1', 'admin@example.com', 'admin')
        super().setUp()
    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

class MultipleOptionTestCase(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = False
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

    def testcreateMultipleOptionQuestionSuccess(self):

        self.driver.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        self.driver.get(self.live_server_url+"/admin/voting/question/add/")
        self.driver.find_element(By.ID, "id_id").click()
        self.driver.find_element(By.ID, "id_id").send_keys('12')
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys('TestMultiple')
        select_element = self.driver.find_element(By.ID, "id_type")
        Select(select_element).select_by_visible_text('Multiple Choice') 
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys('1')
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys('test1')
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys('2')
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys('test2')
        self.driver.find_element(By.ID, "id_options-2-number").click()
        self.driver.find_element(By.ID, "id_options-2-number").send_keys('3')
        self.driver.find_element(By.ID, "id_options-2-option").click()
        self.driver.find_element(By.ID, "id_options-2-option").send_keys('test3')
        self.driver.find_element(By.NAME, "_save").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/admin/voting/question/")

        print("Exito al crear multiple option")
        self.base.tearDown()
    
    def test_vote_in_multiple_options_voting(self):
        q = Question(id = '10',desc='test question', type = 'multiple_choice')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
            
        v = Voting( name='test voting')
        v.save()
        v.questions.add(q)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        decide_user = User.objects.create_user(username='usertest', password='usertest')
        decide_user.save()
        c = Census(voting_id=v.id, voter_id= decide_user.id)
        c.save()

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.driver.get(self.live_server_url+"/booth/"+ str(v.id))
        self.driver.set_window_size(1280, 720)
        wait = WebDriverWait(self.driver, 10)

        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").send_keys("usertest")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").send_keys("usertest")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) > .btn").click()
        wait.until(EC.element_to_be_clickable((By.ID, "q2")))
        self.driver.find_element(By.ID, "q2").click()
        self.driver.find_element(By.ID, "q3").click()
        self.driver.find_element(By.CSS_SELECTOR, ".mt-3").click()
        self.base.tearDown()

    def test_tally_in_multiple_options_voting(self):
        q = Question(id = '15',desc='test question', type = 'multiple_choice')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
            
        v = Voting( name='test voting')
        v.save()
        v.questions.add(q)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        decide_user= User.objects.create_user(username='usertest', password='usertest')
        decide_user.save()
        c1 = Census(voter_id= decide_user.id, voting_id=v.id)
        c1.save()

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.driver.get(self.live_server_url+"/booth/"+ str(v.id))
        self.driver.set_window_size(1280, 720)
        wait = WebDriverWait(self.driver, 10)
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").send_keys("usertest")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").send_keys("usertest")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) > .btn").click()
        wait.until(EC.element_to_be_clickable((By.ID, "q2")))
        self.driver.find_element(By.ID, "q2").click()
        self.driver.find_element(By.ID, "q3").click()
        self.driver.find_element(By.CLASS_NAME, 'btn-primary').click()
        
        self.driver.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.get(self.live_server_url+"/admin/voting/voting/")

        checkbox = self.driver.find_element(By.CLASS_NAME, "action-select")
        checkbox.click()

        actions_dropdown = Select(self.driver.find_element(By.NAME, 'action'))
        actions_dropdown.select_by_visible_text('Stop')
        self.driver.find_element(By.NAME, 'index').click()
        time.sleep(10)

        checkbox = self.driver.find_element(By.CLASS_NAME, "action-select")
        checkbox.click()
        actions_dropdown = Select(self.driver.find_element(By.NAME, 'action'))
        actions_dropdown.select_by_visible_text('Tally')
        self.driver.find_element(By.NAME, 'index').click()
        time.sleep(10)

        self.assertTrue(self.driver.current_url == self.live_server_url+"/admin/voting/voting/")
        self.base.tearDown()

class PointsOptionTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = False
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
    
    def testcreatePointsOptionQuestionSuccess(self):

        self.driver.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        self.driver.get(self.live_server_url+"/admin/voting/question/add/")
        self.driver.find_element(By.ID, "id_id").click()
        self.driver.find_element(By.ID, "id_id").send_keys('12')
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys('TestPointsOption')
        self.driver.find_element(By.ID, "id_weight").click()
        self.driver.find_element(By.ID, "id_weight").send_keys('10')
        select_element = self.driver.find_element(By.ID, "id_type")
        Select(select_element).select_by_visible_text('Points Options') 
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys('1')
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys('test1')
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys('2')
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys('test2')
        self.driver.find_element(By.ID, "id_options-2-number").click()
        self.driver.find_element(By.ID, "id_options-2-number").send_keys('3')
        self.driver.find_element(By.ID, "id_options-2-option").click()
        self.driver.find_element(By.ID, "id_options-2-option").send_keys('test3')
        self.driver.find_element(By.NAME, "_save").click()
        self.base.tearDown()
        print("Exito al crear points options")
    
    def test_vote_in_Points_options_voting(self):
        q = Question(id = 20, desc='test question', type = 'points_options', weight = 10)
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
            
        v = Voting( name='test voting')
        v.save()
        v.questions.add(q)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        decide_user = User.objects.create_user(username='usertest', password='usertest')
        decide_user.save()
        c = Census(voter_id= decide_user.id, voting_id=v.id)
        c.save()

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.driver.get(self.live_server_url+"/booth/"+ str(v.id))
        self.driver.set_window_size(1280, 720)
        wait = WebDriverWait(self.driver, 10)

        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").send_keys("usertest")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").send_keys("usertest")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) > .btn").click()
        wait.until(EC.element_to_be_clickable((By.ID, "q2")))

        self.driver.find_element(By.ID, "q2").click()
        self.driver.find_element(By.ID, "q2").send_keys("4")

        self.driver.find_element(By.ID, "q3").click()
        self.driver.find_element(By.ID, "q3").send_keys("6")
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".mt-3")))
        self.driver.find_element(By.CSS_SELECTOR, ".mt-3").click()
        time.sleep(5)
        self.base.tearDown()
    
    def test_tally_in_multiple_options_voting(self):
        q = Question(id = 25,desc='test question', type = 'points_options', weight = 10)
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
            
        v = Voting( name='test voting')
        v.save()
        v.questions.add(q)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        decide_user = User.objects.create_user(username='usertest', password='usertest')
        decide_user.save()

        c1 = Census(voting_id=v.id,voter_id= decide_user.id)
        c1.save()

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.driver.get(self.live_server_url+"/booth/"+ str(v.id))
        self.driver.set_window_size(1280, 720)
        wait = WebDriverWait(self.driver, 10)

        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #username").send_keys("usertest")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) #password").send_keys("usertest")
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) > .btn").click()
        wait.until(EC.element_to_be_clickable((By.ID, "q2")))

        self.driver.find_element(By.ID, "q2").click()
        self.driver.find_element(By.ID, "q2").send_keys("4")

        self.driver.find_element(By.ID, "q3").click()
        self.driver.find_element(By.ID, "q3").send_keys("6")
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".mt-3")))
        self.driver.find_element(By.CSS_SELECTOR, ".mt-3").click()
        
        self.driver.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.driver.set_window_size(1280, 720)

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("decide")

        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.get(self.live_server_url+"/admin/voting/voting/")

        checkbox = self.driver.find_element(By.CLASS_NAME, "action-select")
        checkbox.click()

        actions_dropdown = Select(self.driver.find_element(By.NAME, 'action'))
        actions_dropdown.select_by_visible_text('Stop')
        self.driver.find_element(By.NAME, 'index').click()
        time.sleep(10)

        checkbox = self.driver.find_element(By.CLASS_NAME, "action-select")
        checkbox.click()
        actions_dropdown = Select(self.driver.find_element(By.NAME, 'action'))
        actions_dropdown.select_by_visible_text('Tally')
        self.driver.find_element(By.NAME, 'index').click()
        time.sleep(10)

        self.assertTrue(self.driver.current_url == self.live_server_url+"/admin/voting/voting/")
        self.base.tearDown()