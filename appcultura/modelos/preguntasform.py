from django.db import models
from .formulario import Formulario

class Preguntas(models.Model):
    descrip = models.TextField(null=True)
    tipo = models.CharField(max_length=255)
    valor = models.IntegerField(null=True)
    estado = models.BooleanField(default=True)
    idform = models.ForeignKey(Formulario, on_delete=models.CASCADE)
    