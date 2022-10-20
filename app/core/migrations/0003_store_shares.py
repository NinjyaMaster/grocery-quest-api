# Generated by Django 3.2.16 on 2022-10-20 18:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_grocery_store'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='shares',
            field=models.ManyToManyField(related_name='shares', to=settings.AUTH_USER_MODEL),
        ),
    ]
