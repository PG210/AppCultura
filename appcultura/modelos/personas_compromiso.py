from django.db import models

from appcultura.modelos.compromisos import Compromisos
from appcultura.modelos.perfiluser import UserPerfil

class PersonasCompromisos(models.Model):
    id_compromiso = models.ForeignKey(Compromisos, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(UserPerfil, on_delete=models.CASCADE)