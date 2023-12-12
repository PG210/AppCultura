from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from appcultura.modelos.calificacionusuarios import CalificacionUsuarios
from appcultura.modelos.compromisos import Compromisos
from appcultura.modelos.cursos import Curso
from appcultura.modelos.gruposcursos import GruposCursos
from datetime import datetime
from django.contrib import messages
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


@login_required
def agregar_compromiso(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    user_all = UserPerfil.objects.all()
    compromises = Compromisos.objects.all()
    grupo_user = GruposUser.objects.filter(iduser=perfil_usuario)
    if grupo_user:
        for user in grupo_user:
            cursos = GruposCursos.objects.filter(idgrupo=user.idgrupo)
    else:
        cursos = ""
    if request.method == 'POST':
        print(request.POST)
        compromiso = request.POST.get('textCompromiso')
        prioridad = request.POST.get('prioridad')
        fecha_str = request. POST.get('fechafinal')
        con_quien_user = request.POST.get('conquien')
        curso_user = request.POST.get('cursos')

        curso = Curso.objects.get(nombre=curso_user)
        #con_quien = UserPerfil.objects.get(nombre=con_quien_user)

        fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
        fecha_final = fecha_obj.strftime("%Y-%m-%d")

        add_compromiso = Compromisos(id_curso=curso, compromiso=compromiso, prioridad=prioridad, fecha_final=fecha_final, con_quien=con_quien_user, id_usuario=perfil_usuario)
        add_compromiso.save()
        message ="Compromiso agragado correctamente"
        return render(request, 'user/compromisos.html',{'usu':perfil_usuario, 'user_all':user_all, 'cursos':cursos, 'mensaje':message})
    else:
        return render(request, 'user/compromisos.html',{'usu':perfil_usuario, 'user_all':user_all, 'cursos':cursos,'compromisos':compromises})

@login_required
def editarcompromiso(request, idcomp):
    if request.method == 'POST':
        compr = request.POST.get('textCompromiso')
        fecha_str = request. POST.get('fechafinal')
        con_quien_user = request.POST.get('conquien')

        if '.' in fecha_str:
            fecha_obj = datetime.strptime(fecha_str, '%b. %d, %Y')
        else:
            fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
        
        fecha_final = fecha_obj.strftime("%Y-%m-%d")

        con_quien = UserPerfil.objects.get(nombre=con_quien_user)

        compromiso = Compromisos.objects.get(id=idcomp)
        compromiso.compromiso = compr
        compromiso.fecha_final = fecha_final
        compromiso.con_quien = con_quien
        compromiso.save()
        return redirect('compromisos')
    else:
        return redirect('compromisos')
    

