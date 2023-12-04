from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class AdminTestCase(StaticLiveServerTestCase):

    def setUp(self):
        #Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()
	
        #Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
        
    '''
    def test_simpleCorrectLoginNuevoUsername(self):      
       #Abre la ruta del navegador             
        self.driver.get(f'{self.live_server_url}/authentication/login-page/')
       #Busca los elementos y “escribe”
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty",Keys.ENTER)

        
       #Mensaje de bienvenida
        mensaje_bienvenida = self.driver.find_element(By.CSS_SELECTOR, 'h2')

        palabra = 'Bienvenido'

        self.assertTrue(palabra in mensaje_bienvenida.text)

    def test_simpleWrongLoginNuevoUsername(self):

        self.driver.get(f'{self.live_server_url}/authentication/login-page/')
        self.driver.find_element(By.ID,'id_username').send_keys("WRONG")
        self.driver.find_element(By.ID,'id_password').send_keys("WRONG", Keys.ENTER)       
        

       #Mensaje de bienvenida
        mensaje_bienvenida = self.driver.find_element(By.CSS_SELECTOR, 'h2')

        palabra = 'Bienvenido'

        self.assertTrue(palabra not in mensaje_bienvenida.text)
        time.sleep(5)
    
    def test_simpleCorrectLogin(self):      
       #Abre la ruta del navegador             
        self.driver.get(f'{self.live_server_url}/admin/')
       #Busca los elementos y “escribe”
        self.driver.find_element(By.ID,'id_username').send_keys("admin")
        self.driver.find_element(By.ID,'id_password').send_keys("qwerty",Keys.ENTER)
        
       #Verifica que nos hemos logado porque aparece la barra de herramientas superior
        self.assertTrue(len(self.driver.find_elements(By.ID, 'user-tools'))==1)
        
    def test_simpleWrongLogin(self):

        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID,'id_username').send_keys("WRONG")
        self.driver.find_element(By.ID,'id_password').send_keys("WRONG")       
        self.driver.find_element(By.ID,'login-form').submit()

       #Si no, aparece este error
        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME,'errornote'))==1)
        time.sleep(5)
    '''