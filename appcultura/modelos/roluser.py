from django.db import models

class RolUser(models.Model):
    descrip = models.CharField(max_length=100)
