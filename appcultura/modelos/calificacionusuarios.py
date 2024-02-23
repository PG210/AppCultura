from django.db import models
from appcultura.modelos.perfiluser import UserPerfil
from appcultura.modelos.sesioncurso import Sesioncurso

class CalificacionUsuarios(models.Model):
    relevancia = models.PositiveIntegerField(choices=[(i, i) for i in range(6)], default=0)
    claridad = models.PositiveIntegerField(choices=[(i, i) for i in range(6)], default=0)
    aplicabilidad = models.PositiveIntegerField(choices=[(i, i) for i in range(6)], default=0)
    fortalezas = models.TextField(null=True)
    areasmejora = models.TextField(null=True)
    idusuario = models.ForeignKey(UserPerfil, on_delete=models.CASCADE, null=True)
    id_sesiones_curso = models.ForeignKey(Sesioncurso, on_delete=models.CASCADE, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    