from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from appcultura.modelos.gruposcursos import GruposCursos

from appcultura.modelos.grupouser import GruposUser # proteger las rutas de accesos
from ..models import UserPerfil

@login_required
def listar_cursos_usuario(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    grupouser = GruposUser.objects.get(iduser=perfil_usuario.id)
    grupocurso = GruposCursos.objects.filter(idgrupo=grupouser.idgrupo)
    return render(request, 'user/listcursos.html',{'usu':perfil_usuario, 'cursos':grupocurso})