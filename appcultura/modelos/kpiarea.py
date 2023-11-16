from django.db import models
from .empresa_areas import EmpresaAreas

class Kpiarea(models.Model):
    nombre =  models.TextField() 
    descrip = models.TextField() 
    fechaini = models.DateTimeField()
    fechafin = models.DateTimeField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.BooleanField(default=True)
    idemparea = models.ForeignKey(EmpresaAreas, on_delete=models.CASCADE)
    

