from django.db import models
from .respuestasformulario import RespuestaForm
from .opcionform import Opciones

class RespuestaOpciones(models.Model):
    idres = models.ForeignKey(RespuestaForm, on_delete=models.CASCADE)
    idopcion = models.ForeignKey(Opciones, on_delete=models.CASCADE)
    correcta = models.BooleanField(default=False)