from django.db import migrations, models
import csv

def cargar_censos(apps, schema_editor):
    Census = apps.get_model('census', 'Census')

    with open('censo.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Census.objects.create(
                voting_id=row['voting_id'],
                voter_id=row['voter_id'],
                # Agrega más campos según sea necesario
            )

class Migration(migrations.Migration):

    dependencies = [
        ('census', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(cargar_censos),
    ]