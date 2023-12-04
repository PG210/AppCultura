from django.db import models
from appcultura.modelos.perfiluser import UserPerfil
from appcultura.modelos.sesioncurso import Sesioncurso

class CalificacionUsuarios(models.Model):
    comentario = models.TextField()
    valoracion = models.PositiveIntegerField(choices=[(i, i) for i in range(6)])
    sugerencia = models.TextField()
    comentario_valor_curso = models.TextField(null=True)
    id_usuario = models.ForeignKey(UserPerfil, on_delete=models.CASCADE)
    id_sesiones_curso = models.ForeignKey(Sesioncurso, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    