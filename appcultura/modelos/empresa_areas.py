from django.db import models
from .empresa import Empresa
from .area import Area
from .departamento import Departamento

class EmpresaAreas(models.Model):
      idempresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
      idarea = models.ForeignKey(Area, on_delete=models.CASCADE)
      idepar = models.ForeignKey(Departamento, on_delete=models.CASCADE, null=True)
      
