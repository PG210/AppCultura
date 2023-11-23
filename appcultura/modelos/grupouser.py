from django.db import models
from .grupos import Grupos
from .perfiluser import UserPerfil
class GruposUser(models.Model):
    idgrupo = models.ForeignKey(Grupos, on_delete=models.CASCADE)
    iduser = models.ForeignKey(UserPerfil, on_delete=models.CASCADE)
    