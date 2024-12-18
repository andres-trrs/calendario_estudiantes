# Generated by Django 5.1 on 2024-11-16 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendarioApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('fecha', models.DateField()),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('ubicacion', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'eventos',
            },
        ),
    ]
