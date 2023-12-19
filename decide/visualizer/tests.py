from django.test import TestCase

from django.test import TestCase
from base.tests import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from voting.models import Voting, Question

from selenium import webdriver
from selenium.webdriver.common.by import By

import time

class VisualizerTestCase(StaticLiveServerTestCase):

    def setUp(self):
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


    def test_simpleVisualizer(self):        
        q = Question(id= 123, desc='test question')
        q.save()
        v = Voting(name='test voting')
        v.save()
        v.questions.add(q)
        v.save()
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState, "Votación no comenzada")

    def test_traducirDE_ES(self):
        options = webdriver.FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get("http://localhost:8000/visualizer/1/")
        driver.set_window_size(1294, 704)
        driver.find_element(By.ID, "de").click()
        assert driver.find_element(By.CSS_SELECTOR, ".navbar-brand").text == "Decide"

    def test_traducirEN_ES(self):
        options = webdriver.FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get("http://localhost:8000/visualizer/1/")
        driver.set_window_size(1294, 704)
        driver.find_element(By.ID, "en").click()
        assert driver.find_element(By.CSS_SELECTOR, ".navbar-brand").text == "Decide"