from django.db import models
from .cursos import Curso
from .competencias import Competencias
class CompetenciaCurso(models.Model):
    idcurso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    idcompetencia = models.ForeignKey(Competencias, on_delete=models.CASCADE)