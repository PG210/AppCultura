from django.db import models
from .area import Area

class Departamento(models.Model):
    nombre = models.CharField(max_length=255)
    descrip = models.TextField()  
    idarea = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
