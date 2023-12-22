from django.db import models

class Competencias(models.Model):
    nombre = models.CharField(max_length=255)