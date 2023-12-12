from django.db import models
from .preguntasform import Preguntas
from .perfiluser import UserPerfil
from .sesioncurso import Sesioncurso

class RespuestaForm(models.Model):
    respuesta = models.TextField(null=True)
    tipores = models.CharField(max_length=255)
    valores = models.IntegerField(null=True)
    comentario = models.TextField(null=True)
    estado = models.BooleanField(default=True)
    fechaenvio = models.DateTimeField(auto_now_add=True, null=True)
    fecharevision = models.DateTimeField(null=True)
    idpreg = models.ForeignKey(Preguntas, on_delete=models.CASCADE)
    iduser = models.ForeignKey(UserPerfil, on_delete=models.CASCADE)
    idsesion = models.ForeignKey(Sesioncurso, on_delete=models.CASCADE, null=True)