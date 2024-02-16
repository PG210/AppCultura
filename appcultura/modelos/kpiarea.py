from django.db import models
from appcultura.modelos.departamento import Departamento
from .area import Area

class Kpiarea(models.Model):
    nombre =  models.TextField() 
    descrip = models.TextField() 
    fechaini = models.DateTimeField()
    fechafin = models.DateTimeField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.BooleanField(default=True)
    idarea = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
    idepar = models.ForeignKey(Departamento, on_delete=models.CASCADE, null=True)

