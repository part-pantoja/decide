from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from base.tests import BaseTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class AdminTestCase(StaticLiveServerTestCase):

    def setUp(self):
        #Crea un usuario admin y otro no admin
        self.base = BaseTestCase()
        self.base.setUp()
	
        #Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    #def test_correct_login_selenium(self):
    def test_registroConCuentaExistente(self):
        self.driver.get(self.live_server_url+"/authentication/register")
        time.sleep(5)

        #Busca los campos que rellenar 
        self.driver.find_element(By.ID, 'id_username').send_keys("pruebaCorreo")
        self.driver.find_element(By.ID, 'id_email').send_keys("pruebaCorreo@correo.us")
        self.driver.find_element(By.ID, 'id_password1').send_keys("estoesunaprueba1")
        self.driver.find_element(By.ID, 'id_password2').send_keys("estoesunaprueba1")

        #Boton de registrar
        self.driver.find_element(By.XPATH, '/html/body/div/form/button').click()

        #Redirigir a la pagina inicial
        self.driver.get(f'{self.live_server_url}/')

        #Redirigir a la pagina de registro
        self.driver.get(self.live_server_url+"/authentication/register")
        
        #Busca los campos que rellenar 
        self.driver.find_element(By.ID, 'id_username').send_keys("pruebaCorreo1")
        self.driver.find_element(By.ID, 'id_email').send_keys("pruebaCorreo@correo.us")
        self.driver.find_element(By.ID, 'id_password1').send_keys("estoesunaprueba2")
        self.driver.find_element(By.ID, 'id_password2').send_keys("estoesunaprueba2")

        #Boton de registrar
        self.driver.find_element(By.XPATH, '/html/body/div/form/button').click()

        time.sleep(5)

        

        mensaje = self.driver.find_element(By.XPATH, '/html/body/div/p').text

        #Verifica que el mensaje ha aparecido y es el mismo
        # self.assertEqual(mensaje, "El correo seleccionado ya existe")

        
