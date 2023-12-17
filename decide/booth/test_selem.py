from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from django.contrib.auth.models import User
from base.tests import BaseTestCase
from voting.models import Voting, Question, QuestionOption
from census.models import Census
from django.utils import timezone

from selenium.common.exceptions import NoSuchElementException

from selenium import webdriver
from selenium.webdriver.common.by import By

class BoothHomeSeleniumTests(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.headless = False
        self.driver = webdriver.Chrome(options=options)
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    def test_booth_home_no_voting(self):
        User.objects.create_user(username='andres', password='Cuaderno1')
        self.driver.get(self.live_server_url)
        self.driver.set_window_size(1061, 904)
        self.driver.find_element(By.LINK_TEXT, "Sign In").click()
        self.driver.find_element(By.ID, "id_username").send_keys("andres")
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("Cuaderno1")
        self.driver.find_element(By.CSS_SELECTOR, "button").click()
        self.driver.find_element(By.LINK_TEXT, "Booth").click()
        self.driver.find_element(By.NAME, "filtro").click()

        try:
            etiqueta = self.driver.find_element(By.TAG_NAME, "h2")
            self.assertFalse(etiqueta.is_displayed())
        except NoSuchElementException:
            self.assertTrue(True)

    def test_booth_home_with_votings(self):
        usuario = User.objects.create_user(username='andres', password='Cuaderno1')
        q = Question(desc='test question')
        q.save()
        q = Question(desc='test question')
        q.save()

        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i))
            opt.save()

        v1 = Voting(name='test voting 1', question=q)
        v1.save()
        v1.start_date = timezone.now()
        v1.save()

        censo1 = Census(voting_id=v1.id, voter_id=usuario.id)
        censo1.save()

        self.driver.get(self.live_server_url)
        self.driver.set_window_size(1480, 904)
        self.driver.find_element(By.LINK_TEXT, "Sign In").click()
        self.driver.find_element(By.ID, "id_username").send_keys("andres")
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("Cuaderno1")
        self.driver.find_element(By.CSS_SELECTOR, "button").click()
        self.driver.find_element(By.LINK_TEXT, "Booth").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(2)").click()
        etiqueta = self.driver.find_element(By.TAG_NAME, "h2")
        self.assertTrue(etiqueta.is_displayed())