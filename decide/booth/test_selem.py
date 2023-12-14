from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase

from selenium.common.exceptions import NoSuchElementException

from selenium import webdriver
from selenium.webdriver.common.by import By

class BoothHomeSeleniumTests(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        super().setUp()
    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    def test_booth_home_no_voting(self):
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
        self.driver.get(self.live_server_url)
        #self.driver.get("http://127.0.0.1:8000/")
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