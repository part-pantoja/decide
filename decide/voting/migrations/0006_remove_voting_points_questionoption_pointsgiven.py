# Generated by Django 4.1 on 2023-11-14 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0005_question_type_question_weight_voting_points'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voting',
            name='points',
        ),
        migrations.AddField(
            model_name='questionoption',
            name='points_given',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]