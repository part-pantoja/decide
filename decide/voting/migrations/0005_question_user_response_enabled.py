# Generated by Django 4.1 on 2023-11-13 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_alter_voting_postproc_alter_voting_tally'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='user_response_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
