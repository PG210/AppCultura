from django.db import models
from .empresa import Empresa
from .area import Area
from .departamento import Departamento

class EmpresaAreas(models.Model):
      idempresa = models.OneToOneField(Empresa, on_delete=models.CASCADE)
      idarea = models.OneToOneField(Area, on_delete=models.CASCADE)
      idepar = models.OneToOneField(Departamento, on_delete=models.CASCADE, null=True)
      
