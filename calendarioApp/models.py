from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
    correo = models.EmailField(max_length=60, unique=True)
    contrasena = models.CharField(max_length=30)
    fecha_nacimiento = models.DateField()

    class Meta:
        db_table = 'usuarios'  # Esto asegura que el modelo se mapee a la tabla existente

class Evento(models.Model):
    titulo = models.CharField(max_length=100)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    ubicacion = models.CharField(max_length=100, blank=True, null=True)
    correo = models.EmailField(max_length=60, null=True, blank=True)

    class Meta:
        db_table = 'eventos'
