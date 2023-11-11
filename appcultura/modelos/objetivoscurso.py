from django.db import models
from .cursos import Curso

class ObjetivosCurso(models.Model):
    descrip= models.TextField()
    competencias = models.TextField()
    idcurso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    