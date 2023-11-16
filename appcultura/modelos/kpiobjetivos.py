from django.db import models
from .kpiarea import Kpiarea

class Kpiobjetivos(models.Model):
    objtivo =  models.TextField() 
    meta = models.TextField() 
    indicador = models.TextField()
    idkpi = models.ForeignKey(Kpiarea, on_delete=models.CASCADE)
    

