from django.db import models

class TamEmpresa(models.Model):
    descrip = models.TextField(max_length=255)  # Campo de texto ilimitado
