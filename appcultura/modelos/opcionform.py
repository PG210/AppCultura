from pickle import FALSE
from django.db import models
from .preguntasform import Preguntas

class Opciones(models.Model):
    descrip = models.TextField(null=True)
    correcta = models.BooleanField(default=False)
    idpreg = models.ForeignKey(Preguntas, on_delete=models.CASCADE)
    