from django.db import models
from .grupos import Grupos
from .cursos import Curso
class GruposCursos(models.Model):
    idgrupo = models.ForeignKey(Grupos, on_delete=models.CASCADE)
    idcurso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    
   
