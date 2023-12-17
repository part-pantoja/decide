import json
import requests
import random
import string
from locust import HttpUser, task, between


HOST = "http://localhost:8000"
USER = "decideuser"
PASS = "2329"

class UserRegistration(HttpUser):
    wait_time = between(3,5)
    host = HOST

    @task
    def register_user(self):
        self.client.get(HOST+ '/authentication/register/')
        #Generar datos aleatorios para el registro
        username = self.generate_random_string()
        email = f"{username}@example.com"
        password = "pruebadecarga1"
        #Enviar solicitud de registro
        response = self.client.post(HOST+'/authentication/register/', data={
            "username": username,
            "email":email,
            "password1":password,
            "password2":password,
        }
        )
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            print(f"Registro exitoso!, el usuario {username} se ha registrado, solo falta que verifique su cuenta")
        else:
            print("El usuario no se ha registrado y ha dado fallos")



    def generate_random_string(self,lenght=8):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for _ in range(lenght))
