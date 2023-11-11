from django.db import models
from .cargo import Cargo

class ObjCargo(models.Model):
    nombre = models.CharField(max_length=255)
    descrip = models.TextField()  # Campo de texto ilimitado
    idcargo = models.OneToOneField(Cargo, on_delete=models.CASCADE)

