from django.db import models
from .cursos import Curso

class Sesioncurso(models.Model):
    fechainicio = models.DateTimeField()
    fechafin = models.DateTimeField()
    lugar = models.CharField(max_length=255) 
    estado = models.BooleanField(default=True)  # Puedes cambiar el valor predeterminado según tus necesidades
    idcurso = models.ForeignKey(Curso, on_delete=models.CASCADE)