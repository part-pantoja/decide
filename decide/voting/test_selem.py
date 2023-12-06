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
        options.add_argument("--no-sandbox")
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        User.objects.create_superuser('admin1', 'admin@example.com', 'admin')
        super().setUp()            
     
    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
