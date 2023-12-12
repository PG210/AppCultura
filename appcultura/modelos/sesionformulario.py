from django.db import models
from .sesioncurso import Sesioncurso
from .formulario import Formulario

class SesionFormulario(models.Model):
    fecha = models.DateTimeField()
    estado = models.BooleanField(default=True)
    idform = models.ForeignKey(Formulario, on_delete=models.CASCADE)
    idsesion = models.ForeignKey(Sesioncurso, on_delete=models.CASCADE)