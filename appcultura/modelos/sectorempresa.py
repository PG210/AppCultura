from django.db import models

class SectorEmpresa(models.Model):
    nombre = models.CharField(max_length=255)
    descrip = models.TextField()  # Campo de texto ilimitado
