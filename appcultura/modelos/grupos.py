from django.db import models

class Grupos(models.Model):
    nombre = models.CharField(max_length=255)
    descrip = models.TextField(null=True)
