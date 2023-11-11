from django.db import models

class GrupoEmpresa(models.Model):
    nombre = models.CharField(max_length=255)
    nit = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    correo = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)

