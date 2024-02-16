from django.db import models
from .empresa import Empresa

class Area(models.Model):
    nombre = models.CharField(max_length=255)
    descrip = models.TextField()  
    idempresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True)
