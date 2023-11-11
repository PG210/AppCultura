from django.db import models

class Area(models.Model):
    nombre = models.CharField(max_length=255)
    descrip = models.TextField()  
    
