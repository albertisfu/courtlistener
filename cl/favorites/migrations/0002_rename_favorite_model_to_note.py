# Generated by Django 3.2.16 on 2023-01-17 06:22

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0001_initial'),
        ('search', '0009_alter_court_jurisdiction'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('favorites', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Favorite',
            new_name='Note',
        ),
    ]
