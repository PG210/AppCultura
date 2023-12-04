from django.db import models

class Formulario(models.Model):
    nombre = models.CharField(max_length=255)
    descrip = models.TextField(null=True)
    estado = models.BooleanField(default=True)
    fecha = models.DateTimeField()
    

