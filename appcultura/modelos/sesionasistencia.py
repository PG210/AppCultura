from django.db import models
from appcultura.modelos.sesioncurso import Sesioncurso
from .perfiluser import UserPerfil


class SesionAsistencia(models.Model):
    idsesioncurso = models.ForeignKey(Sesioncurso, on_delete=models.CASCADE)
    idusuario = models.ForeignKey(UserPerfil, on_delete=models.CASCADE)
    fecha_asistencia = models.DateTimeField(auto_now_add=True)