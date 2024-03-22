from django.db import models
from appcultura.modelos.perfiluser import UserPerfil
from appcultura.modelos.compromisos import Compromisos

class AvanceCompromisos(models.Model):
    fechaini = models.DateField(auto_now=True)
    fechafin = models.DateField()
    actividad = models.TextField()
    estado = models.TextField()
    puntaje = models.IntegerField(default=0)
    respuesta = models.TextField(null=True)
    idusurespuesta = models.ForeignKey(UserPerfil, on_delete=models.CASCADE, null=True)
    idcompromiso = models.ForeignKey(Compromisos, on_delete=models.CASCADE, null=True)