from django.db import models
from appcultura.modelos.estado_compromisos import EstadoCompromisos
from appcultura.modelos.perfiluser import UserPerfil
from appcultura.modelos.sesioncurso import Sesioncurso
from appcultura.modelos.respuestasformulario import RespuestaForm
from django.core.validators import MinValueValidator, MaxValueValidator

class Compromisos(models.Model):
    compromiso = models.TextField()
    prioridad = models.TextField()
    fecha_compromiso = models.DateField(auto_now=True)
    fecha_final = models.DateField()
    puntaje = models.IntegerField(default=0)
    respuesta = models.TextField(null=True)
    id_sesion = models.ForeignKey(Sesioncurso, on_delete=models.CASCADE, null=True)
    id_estado = models.ForeignKey(EstadoCompromisos, on_delete=models.CASCADE, default=2)
    id_usuario = models.ForeignKey(UserPerfil, on_delete=models.CASCADE, null=True)
    idrespuesta = models.ForeignKey(RespuestaForm, on_delete=models.CASCADE, null=True)
    