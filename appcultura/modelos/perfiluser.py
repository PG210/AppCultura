from django.db import models
from django.contrib.auth.models import User

from appcultura.modelos.area import Area
from .roluser import RolUser
from .departamento import Departamento
from .empresa import Empresa

class UserPerfil(models.Model):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    cedula =  models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    cargo = models.CharField(max_length=255, null=True, blank=True)
    vpass = models.CharField(max_length=255, null=True, blank=True)
    estado = models.IntegerField(default=1)
    idrol = models.ForeignKey(RolUser, on_delete=models.CASCADE)  # Permitir múltiples usuarios con el mismo rol
    idepart = models.ForeignKey(Departamento, on_delete=models.CASCADE,  null=True)
    idarea = models.ForeignKey(Area, on_delete=models.CASCADE,  null=True)
    idempresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pendiente = models.BooleanField(null=True)
