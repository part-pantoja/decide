from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from base.tests import BaseTestCase


# Create your tests here.

class BoothTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
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

    def testCheckLogin(self):
        options = webdriver.FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get("http://127.0.0.1:8000/booth/1/")
        driver.set_window_size(1294, 704)
        driver.find_element(By.ID, "username").click()
        driver.find_element(By.ID, "username").send_keys("bogste")
        driver.find_element(By.ID, "password").click()
        driver.find_element(By.ID, "password").send_keys("bogstedecide")
        driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(3)").click()
        elements = driver.find_elements(By.LINK_TEXT, "logout")
        assert len(elements) > 0