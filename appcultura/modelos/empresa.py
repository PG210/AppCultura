from django.db import models
from .sectorempresa import SectorEmpresa
from .grupoempresa import GrupoEmpresa
from .tamanioempresa import TamEmpresa

class Empresa(models.Model):
    nombre = models.CharField(max_length=255)
    nit = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    correo = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    idtam = models.ForeignKey(TamEmpresa, on_delete=models.CASCADE)
    idsector = models.ForeignKey(SectorEmpresa, on_delete=models.CASCADE)
    idgrupoem = models.ForeignKey(GrupoEmpresa, on_delete=models.CASCADE, null=True)
    




