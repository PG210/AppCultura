from django.db import models
from .empresa import Empresa
from .perfiluser import UserPerfil

class FormadorEmpresa(models.Model):
    idusu = models.ForeignKey(UserPerfil, on_delete=models.CASCADE, null=True) 
    idempresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True)
    estado = models.BooleanField(default=False)