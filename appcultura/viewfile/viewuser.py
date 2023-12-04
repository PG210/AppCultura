from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from appcultura.modelos.calificacionusuarios import CalificacionUsuarios
from appcultura.modelos.gruposcursos import GruposCursos

from appcultura.modelos.grupouser import GruposUser
from appcultura.modelos.sesionasistencia import SesionAsistencia
from appcultura.modelos.sesioncurso import Sesioncurso # proteger las rutas de accesos
from ..models import UserPerfil

@login_required
def listar_cursos_usuario(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    asistencias = SesionAsistencia.objects.all()
    grupouser = GruposUser.objects.filter(iduser=perfil_usuario.id)
    for grupo_usuario in grupouser:
        grupocurso = GruposCursos.objects.filter(idgrupo=grupo_usuario.idgrupo)
        for grupo_curso in grupocurso:
            sesiones = Sesioncurso.objects.filter(idcurso=grupo_curso.idcurso)
            for sesion in sesiones:
                calificaciones=CalificacionUsuarios.objects.filter(id_sesiones_curso=sesion)

    return render(request, 'user/listcursos.html',{'usu':perfil_usuario, 'cursos':grupocurso, 'sesiones':sesiones, 'calificacion':calificaciones, 'asistencias':asistencias})

@login_required
def add_calificacion(request, idsesion):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    if request.method == 'POST':
        calificacion = request.POST.get('estrellas')
        sugerencias = request.POST.get('textareasugerencias')
        comentarios = request.POST.get('textareacomentarios')
        valor_curso = request.POST.get('textareavalorcurso')
        sesion = Sesioncurso.objects.get(id=idsesion)

        if CalificacionUsuarios.objects.filter( id_usuario=perfil_usuario, id_sesiones_curso=sesion ):
            mensaje="Tu Calificacion ya se encuentra registrada"
        else:
            dbcalificacion = CalificacionUsuarios(comentario=comentarios, valoracion=calificacion, sugerencia=sugerencias, id_usuario=perfil_usuario, id_sesiones_curso=sesion, estado=False , comentario_valor_curso=valor_curso)
            dbcalificacion.save()
            mensaje = "Gracias por calificar nuestro servicio"

        return render(request, 'user/calificacion.html', {'usu':perfil_usuario, 'idsesion':idsesion, 'mensaje':mensaje})
        

    else:
        return render(request, 'user/calificacion.html', {'usu':perfil_usuario, 'idsesion':idsesion})

