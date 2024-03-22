from django.db import models
from appcultura.modelos.compromisos import Compromisos

class FechasCompromisos(models.Model):
    fechadd = models.DateField()
    idcompromiso = models.ForeignKey(Compromisos, on_delete=models.CASCADE, null=True)