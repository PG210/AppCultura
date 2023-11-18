from django.db import models
from .sesioncurso import Sesioncurso

class TemasSesion(models.Model):
    descrip= models.TextField(null=True)
    competencias = models.TextField(null=True)
    recursos = models.TextField(null=True)
    ruta = models.CharField(max_length=255, null=True)
    idsesion = models.ForeignKey(Sesioncurso, on_delete=models.CASCADE)