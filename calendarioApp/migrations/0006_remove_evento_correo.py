# Generated by Django 5.1 on 2024-11-16 19:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calendarioApp', '0005_evento_correo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evento',
            name='correo',
        ),
    ]
