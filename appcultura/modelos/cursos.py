from django.db import models
from .empresa import Empresa
from .perfiluser import UserPerfil

class Curso(models.Model):
    nombre = models.CharField(max_length=255)
    descrip = models.TextField() 
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    idusu = models.ForeignKey(UserPerfil, on_delete=models.CASCADE, null=True) #esta refrencia es para saber quien lo creo
    idempresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True) #esta referencia es para saber aque empresa pertenece

