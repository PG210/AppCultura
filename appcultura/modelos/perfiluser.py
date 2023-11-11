from django.db import models
from django.contrib.auth.models import User
from .roluser import RolUser
from .cargo import Cargo
from .empresa_areas import EmpresaAreas

class UserPerfil(models.Model):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    cedula =  models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    estado = models.IntegerField(default=1)
    idrol = models.ForeignKey(RolUser, on_delete=models.CASCADE)  # Permitir múltiples usuarios con el mismo rol
    idcargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    idempresa = models.ForeignKey(EmpresaAreas, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
