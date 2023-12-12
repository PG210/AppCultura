from asyncio.windows_events import NULL
from tkinter.tix import Tree
from django.db import models
from appcultura.modelos.cursos import Curso
from appcultura.modelos.estado_compromisos import EstadoCompromisos
from appcultura.modelos.perfiluser import UserPerfil
from appcultura.modelos.sesioncurso import Sesioncurso
from django.core.validators import MinValueValidator, MaxValueValidator

class Compromisos(models.Model):
    id_curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    id_estado = models.ForeignKey(EstadoCompromisos, on_delete=models.CASCADE, default=2)
    id_usuario = models.ForeignKey(UserPerfil, on_delete=models.CASCADE, null=True)
    compromiso = models.TextField()
    prioridad = models.TextField()
    fecha_compromiso = models.DateField(auto_now=True)
    fecha_final = models.DateField()
    puntaje = models.IntegerField(default=0)
    con_quien = models.TextField(null=True)
    respuesta = models.TextField(null=True)