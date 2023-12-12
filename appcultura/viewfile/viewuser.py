from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from appcultura.modelos.calificacionusuarios import CalificacionUsuarios
from appcultura.modelos.compromisos import Compromisos
from appcultura.modelos.cursos import Curso
from appcultura.modelos.gruposcursos import GruposCursos
from datetime import datetime
from django.contrib import messages
from appcultura.modelos.grupouser import GruposUser
from appcultura.modelos.opcionform import Opciones
from appcultura.modelos.sesionasistencia import SesionAsistencia
from appcultura.modelos.sesioncurso import Sesioncurso # proteger las rutas de accesos
from ..models import UserPerfil, SesionFormulario, Preguntas, RespuestaForm, RespuestaOpciones, Formulario


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

#============== ver formularios de la sesion =====
@login_required
def verformusesion(request, idsesion):
    perfil_usuario = get_object_or_404(UserPerfil, user=request.user)
    formulario_sesion = SesionFormulario.objects.filter(idsesion=idsesion)
    respuestasForm = ''
    #formulario_sesion = get_object_or_404(SesionFormulario, idsesion=idsesion)
    preguntas = Preguntas.objects.all()
    datoscurso = Sesioncurso.objects.get(id=idsesion)
    # evaluar si el formulario y el usuario ya estan en la tabla 
    formu_completos = []
    
    for formulario in formulario_sesion:
        existe_formu = RespuestaForm.objects.filter(idpreg__idform=formulario.idform, iduser=perfil_usuario).exists()
        # Si ya está registrado, quítalo de la variable formulario_sesion
        if existe_formu:
            # obtener los formularios completos para este usuario
            formu_completos.append(formulario.idform) # aggrega al ultimo elememto un formulario
            formulario_sesion = formulario_sesion.exclude(pk=formulario.pk)

    formulario_sesion_vacia = not formulario_sesion.exists()
    #============== buscar formularios terminados ===============
    for formuterminados in formu_completos:
        respuestasForm = RespuestaForm.objects.filter(idpreg__idform=formuterminados, iduser=perfil_usuario, idsesion=datoscurso)
    #============= end buscar =================
    if formulario_sesion_vacia:
        mensajeInfo = "No tiene Formularios disponibles"
        return render(request, 'user/listaformu.html', {'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntas, 'datoscurso':datoscurso, 'mensajeInfo':mensajeInfo, 'respuestasForm':respuestasForm, 'formcompleto':formu_completos})
    else:
       return render(request, 'user/listaformu.html', {'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntas, 'datoscurso':datoscurso, 'respuestasForm':respuestasForm, 'formcompleto':formu_completos})

#========================== guardar las respuestas del user =====================
@login_required
def saveRespuestas(request, idsesion, idformu):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    formulario_sesion = SesionFormulario.objects.filter(idsesion=idsesion)
    preguntasnew = Preguntas.objects.all()
    datoscurso = Sesioncurso.objects.get(id=idsesion)
    formu_completos = []
    respuestasForm = []
    #===========================================================
    if request.method == 'POST':
       if request.POST.items():
            for key, value in request.POST.items():
                if key.startswith('pregunta') and value:
                       pregunta_id = key.split('pregunta')[1] #Aqui obtiene el id de cada preguntas
                       pregunta = Preguntas.objects.get(id=pregunta_id) # aqui busca el id de cada pregunta
                    
                       if pregunta.tipo == '1' or pregunta.tipo == '2':
                            opciontexto = request.POST.get(f'respuesta{pregunta_id}')  # aqui llegan todas las respuestas de tipo texto largo y corto
                            existe_respuesta = RespuestaForm.objects.filter(iduser=perfil_usuario, idpreg=pregunta_id, idsesion=datoscurso).exists() #evaluar si existe
                            if not existe_respuesta:
                               restexto = RespuestaForm(respuesta=opciontexto, tipores=pregunta.tipo, valores=pregunta.valor, idpreg=pregunta, iduser=perfil_usuario, idsesion=datoscurso)
                               restexto.save()
                           
                       elif pregunta.tipo == '3':
                            # Obtener las opciones múltiples asociadas a la pregunta escoge cualquiera y le va adar el valor
                            opcionesmul = request.POST.getlist(f'opcionesmul{pregunta_id}')
                            existe_res = RespuestaForm.objects.filter(iduser=perfil_usuario, idpreg=pregunta_id, idsesion=datoscurso).exists() #evaluar si existe
                            if not existe_res:  
                                resmul = RespuestaForm(tipores=pregunta.tipo, valores=pregunta.valor, idpreg=pregunta, iduser=perfil_usuario, idsesion=datoscurso)
                                resmul.save()
                                for opmul in opcionesmul:
                                    buscarop = Opciones.objects.get(id=opmul) #buscar los objects
                                    resop = RespuestaOpciones(idres=resmul, idopcion=buscarop)  #guardar opciones de respuesta
                                    resop.save()
                            
                       elif pregunta.tipo == '4':
                                opciones_marcadas = request.POST.getlist(f'opcionradio{pregunta_id}')
                                for opcion_id in opciones_marcadas:  # Itera sobre las opciones marcadas
                                    opcion_seleccionada = Opciones.objects.get(id=opcion_id) # buscar el object
                                    # Verifica si ya existe una respuesta para esta pregunta y usuario
                                    existe_respuesta_unica = RespuestaForm.objects.filter(idpreg=pregunta, iduser=perfil_usuario, idsesion=datoscurso).exists()
                                    if not existe_respuesta_unica:
                                        valor_respuesta = pregunta.valor if opcion_seleccionada.correcta else 0  # Si la respuesta es correcta, asigna el valor de la pregunta, de lo contrario, asigna 0
                                        # Crea una nueva respuesta
                                        nueva_respuesta = RespuestaForm(tipores=pregunta.tipo, valores=valor_respuesta, idpreg=pregunta, iduser=perfil_usuario, idsesion=datoscurso)
                                        nueva_respuesta.save()
                                        # Guarda la relación entre la respuesta y la opción seleccionada
                                        respuesta_opcion_one = RespuestaOpciones(idres=nueva_respuesta, idopcion=opcion_seleccionada, correcta=opcion_seleccionada.correcta)
                                        respuesta_opcion_one.save()

                       elif pregunta.tipo == '5':
                                opciones_seleccionadas = request.POST.getlist(f'opcionesUnico{pregunta_id}')
                                existe_respuesta_multiple = RespuestaForm.objects.filter(idpreg=pregunta, iduser=perfil_usuario, idsesion=datoscurso).exists() # Verifica si ya existe una respuesta para esta pregunta y usuario
                                if not existe_respuesta_multiple:
                                    opciones_correctas = Opciones.objects.filter(idpreg=pregunta, correcta=True)  # Busca todas las opciones asociadas a la pregunta que son correctas
                                    valor_respuesta_multiple = 0  # Variable para acumular el valor de la respuesta múltiple

                                    # Verifica que todas las opciones seleccionadas sean correctas
                                    todas_correctas = True
                                    # Convierte las opciones seleccionadas a objetos Opciones mediante una lista
                                    #opciones_seleccionadas_objetos = Opciones.objects.filter(id__in=opciones_seleccionadas)
                                    for opcsel in opciones_seleccionadas:
                                        obtenersel = Opciones.objects.get(id=opcsel)
                                        if obtenersel not in opciones_correctas:
                                           todas_correctas = False
                                           break  # No es necesario seguir verificando, al menos una es incorrecta               
                                    #todas_correctas = all(opcion_idmul in opciones_correctas.values_list('id', flat=True) for opcion_idmul in opciones_seleccionadas)
                                   
                                    print(todas_correctas)
                                    # Asigna el valor de la respuesta múltiple si todas las opciones son correctas
                                    if todas_correctas:
                                        valor_respuesta_multiple = pregunta.valor

                                    # Crea una nueva respuesta múltiple
                                    nueva_respuesta_multiple = RespuestaForm(tipores=pregunta.tipo, valores=valor_respuesta_multiple, idpreg=pregunta, iduser=perfil_usuario, idsesion=datoscurso)
                                    nueva_respuesta_multiple.save()
                                    
                                    # Itera sobre las opciones seleccionadas y guarda la relación con la respuesta múltiple
                                    for opcion_id in opciones_seleccionadas:
                                        opcion_seleccionada = Opciones.objects.get(id=opcion_id)
                                        respuesta_opcion_one = RespuestaOpciones(idres=nueva_respuesta_multiple, idopcion=opcion_seleccionada, correcta=opcion_seleccionada.correcta)
                                        respuesta_opcion_one.save()
            #====== mensaje de exito =============
            mensajeInfo = "La información se ha registrado éxitosamente"
            #tot = RespuestaForm.objects.filter(idpreg__idform=idformu, iduser=perfil_usuario).aggregate(Sum('valores'))
            puntaje_total = RespuestaForm.objects.filter(idpreg__idform=idformu, iduser=perfil_usuario).aggregate(total_puntaje=Sum('valores'))['total_puntaje']
            puntaje_total = puntaje_total if puntaje_total is not None else 0
            #========== validar si ya esta lleno el formulario ===============
            for formulario in formulario_sesion:
                existe_formu = RespuestaForm.objects.filter(idpreg__idform=formulario.idform, iduser=perfil_usuario).exists()
                # Si ya está registrado, quítalo de la variable formulario_sesion
                if existe_formu:
                    formu_completos.append(formulario.idform) # aggrega al ultimo elememto un formulario
                    formulario_sesion = formulario_sesion.exclude(pk=formulario.pk)
             #============== buscar formularios terminados ===============
           
            #for formuterminados in formu_completos:
            respuestasForm = RespuestaForm.objects.filter(iduser=perfil_usuario, idsesion=datoscurso)
            #print(respuestasForm)
            return render(request, 'user/listaformu.html', {'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntasnew, 'datoscurso':datoscurso, 'mensajeInfo':mensajeInfo, 'puntaje':puntaje_total, 'respuestasForm':respuestasForm, 'formcompleto':formu_completos})
       
       mensajeInfo = "Por favor complete todos los campos"
       puntaje_total = puntaje_total if puntaje_total is not None else 0
    return render(request, 'user/listaformu.html', {'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntasnew, 'datoscurso':datoscurso, 'mensajeInfo':mensajeInfo})

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
    

