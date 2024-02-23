from django.db import models
from appcultura.modelos.perfiluser import UserPerfil
from appcultura.modelos.sesioncurso import Sesioncurso

class CalificacionFormador(models.Model):
    claridad = models.PositiveIntegerField(choices=[(i, i) for i in range(6)], default=0)
    capacidad = models.PositiveIntegerField(choices=[(i, i) for i in range(6)], default=0)
    dominio = models.PositiveIntegerField(choices=[(i, i) for i in range(6)], default=0)
    aspectosrescatar = models.TextField(null=True)
    usuario = models.ForeignKey(UserPerfil, on_delete=models.CASCADE, related_name='calificaciones_recibidas', null=True)
    formador = models.ForeignKey(UserPerfil, on_delete=models.CASCADE, related_name='calificaciones_emitidas', null=True)
    sesion_curso = models.ForeignKey(Sesioncurso, on_delete=models.CASCADE, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    