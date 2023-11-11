from django.db import models

class Curso(models.Model):
    nombre = models.CharField(max_length=255)
    descrip = models.TextField() 
    precio = models.DecimalField(max_digits=10, decimal_places=2)

