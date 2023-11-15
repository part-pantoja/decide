import csv
from django.db import migrations
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

def cargar_usuarios(apps, schema_editor):
    with open('usuarios.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            User.objects.create(
                username=row['username'],
                password=row['password'],  # La contraseña ya debe estar cifrada en tu CSV
                email=row['email'],
                # Agrega más campos según sea necesario
            )

class Migration(migrations.Migration):

    

    operations = [
        migrations.RunPython(cargar_usuarios),
    ]