from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from django.contrib.auth.models import User

class AdminTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        User.objects.create_superuser('admin1', 'admin@example.com', 'admin')
        super().setUp()            
     
    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def test_preguntaconvotoenblanco(self):
        self.driver.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.driver.set_window_size(1850, 1016)
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin1")
        self.driver.find_element(By.ID, "id_password").send_keys("admin")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("pregunta con voto en blanco")
        self.driver.find_element(By.CSS_SELECTOR, ".vCheckboxLabel").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) > .field-__str__ > a").click()
        self.driver.find_element(By.ID, "id_options-0-DELETE").click()
        self.driver.find_element(By.ID, "id_options-0-DELETE").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Delete selected questions']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.CSS_SELECTOR, "input:nth-child(4)").click()