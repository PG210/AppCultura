from django.db import models

class Cargo(models.Model):
    nombre = models.CharField(max_length=255)
    descrip = models.CharField(max_length=255)
