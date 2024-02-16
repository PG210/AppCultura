from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from appcultura.modelos.calificacionusuarios import CalificacionUsuarios
from appcultura.modelos.compromisos import Compromisos
from appcultura.modelos.cursos import Curso
from appcultura.modelos.gruposcursos import GruposCursos
from datetime import datetime, date
from django.contrib import messages
from appcultura.modelos.grupouser import GruposUser
from appcultura.modelos.opcionform import Opciones
from appcultura.modelos.sesionasistencia import SesionAsistencia
from appcultura.modelos.sesioncurso import Sesioncurso # proteger las rutas de accesos
from ..models import UserPerfil, SesionFormulario, RolUser, Preguntas, RespuestaForm, RespuestaOpciones, PersonasCompromisos, Formulario
from django.contrib.auth.models import User
from django.db import IntegrityError

@login_required
def listar_cursos_usuario(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    asistencias = SesionAsistencia.objects.all()
    grupouser = GruposUser.objects.filter(iduser=perfil_usuario.id)
    #=================================================================
    grupocurso = ''
    sesiones = ''
    calificaciones = ''
    if grupouser:
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
    fecha_actual = date.today()
    perfil_usuario = get_object_or_404(UserPerfil, user=request.user)
    formulario_sesion = SesionFormulario.objects.filter(idsesion=idsesion)
    usuarios = UserPerfil.objects.filter(idrol=2).exclude(id=perfil_usuario.id)
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
        return render(request, 'user/listaformu.html', {'usuarios': usuarios, 'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntas, 'datoscurso':datoscurso, 'mensajeInfo':mensajeInfo, 'respuestasForm':respuestasForm, 'formcompleto':formu_completos, 'fecha_actual':fecha_actual})
    else:
       return render(request, 'user/listaformu.html', {'usuarios': usuarios, 'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntas, 'datoscurso':datoscurso, 'respuestasForm':respuestasForm, 'formcompleto':formu_completos, 'fecha_actual':fecha_actual})

#========================== guardar las respuestas del user =====================
@login_required
def saveRespuestas(request, idsesion, idformu):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    formulario_sesion = SesionFormulario.objects.filter(idsesion=idsesion)
    preguntasnew = Preguntas.objects.all()
    datoscurso = Sesioncurso.objects.get(id=idsesion)
    usuarios = UserPerfil.objects.filter(idrol=2).exclude(id=perfil_usuario.id)
    formu_completos = []
    respuestasForm = []
     # Obtén la fecha actual
    fecha_actual = date.today()
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
                       # si la pregunta es tipo 6 debe guardar el compromiso
                       elif pregunta.tipo == '6':
                            comentario = request.POST.get(f'compromiso{pregunta_id}')  # aqui llegan todas las respuestas de tipo texto largo y corto
                            prioridad = request.POST.get(f'prioridad{pregunta_id}') # aqui llega la prioridad
                            fecha = request.POST.get(f'fecha{pregunta_id}') # aqui llega la fecha final
                            personas_seleccionadas = request.POST.getlist(f'opcionesPersonas{pregunta_id}')
                            valorpreg = 0
                            existe_compromiso = RespuestaForm.objects.filter(iduser=perfil_usuario, idpreg=pregunta_id, idsesion=datoscurso).exists() #evaluar si existe
                            if not existe_compromiso:
                               rescompromiso = RespuestaForm(respuesta=comentario, tipores=pregunta.tipo, valores=valorpreg, idpreg=pregunta, iduser=perfil_usuario, idsesion=datoscurso)
                               rescompromiso.save()
                               # guardar los datos 
                               savecompromiso = Compromisos(compromiso=comentario, prioridad=prioridad, fecha_final=fecha, id_sesion=datoscurso, id_usuario=perfil_usuario, idrespuesta=rescompromiso)
                               savecompromiso.save()
                               #guardar las opciones de personas requeridas
                               if personas_seleccionadas:
                                  for perid in personas_seleccionadas:
                                      obtenerusu = UserPerfil.objects.get(id=perid)
                                      savePersonas = PersonasCompromisos(id_compromiso=savecompromiso, id_usuario=obtenerusu)
                                      savePersonas.save()
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
            return render(request, 'user/listaformu.html', {'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntasnew, 'datoscurso':datoscurso, 'mensajeInfo':mensajeInfo, 'puntaje':puntaje_total, 'respuestasForm':respuestasForm, 'formcompleto':formu_completos, 'fecha_actual':fecha_actual, 'usuarios':usuarios})
       
       mensajeInfo = "Por favor complete todos los campos"
       puntaje_total = puntaje_total if puntaje_total is not None else 0
    return render(request, 'user/listaformu.html', {'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntasnew, 'datoscurso':datoscurso, 'mensajeInfo':mensajeInfo, 'fecha_actual':fecha_actual, 'usuarios':usuarios})

@login_required
def agregar_compromiso(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    compromises = Compromisos.objects.all()
    grupo_user = GruposUser.objects.filter(iduser=perfil_usuario)
    user_all = UserPerfil.objects.filter(idrol=2).exclude(id=perfil_usuario.id)
    fecha_actual = date.today()
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
        return render(request, 'user/compromisos.html',{'usu':perfil_usuario, 'user_all':user_all, 'cursos':cursos, 'mensaje':message, 'compromisos':compromises})
    else:
        return render(request, 'user/compromisos.html',{'usu':perfil_usuario, 'user_all':user_all, 'cursos':cursos,'compromisos':compromises, 'fechamin':fecha_actual})

@login_required
def editarcompromiso(request, idcomp):
    if request.method == 'POST':
        compromiso = request.POST.get('textCompromiso')
        fecha = request. POST.get('fechafinal')
        personas = request.POST.getlist('idpersona')
        # guardar la informacion de personas compromiso
        personasActuales = PersonasCompromisos.objects.filter(id_compromiso=idcomp)
        # buscar el objeto compromiso por el id
        updateCompromiso = get_object_or_404(Compromisos, id=idcomp)
        updateCompromiso.compromiso =  compromiso
        updateCompromiso.fecha_final = fecha
        updateCompromiso.save()
        # registrar los usuarios
        deletePersonas = PersonasCompromisos.objects.filter(id_compromiso=idcomp)
        deletePersonas.delete()
        # guardar la informacion
        for userper in personas:
            buscaruser = get_object_or_404(UserPerfil, id=userper)
            addPersonas = PersonasCompromisos(id_compromiso=updateCompromiso, id_usuario=buscaruser)
            addPersonas.save()
        return redirect('compromisos')
    else:
        return redirect('compromisos')
    

#=============== aqui evaluar formularios del QR
# crear la ruta que permite ver el formulario en linea
def verFormuQR(request, idsesion):
    return render(request, 'user/formularioqr.html', {'idsesion':idsesion})

# validar que el usuario este registrado 
def validarasistenciaform(request, idsesion):
    #=================================================
    fecha_actual = date.today()
    preguntas = Preguntas.objects.all()
    formulario_sesion = SesionFormulario.objects.filter(idsesion=idsesion)
    datoscurso = Sesioncurso.objects.get(id=idsesion)
    #=====================================================
    if request.method == 'POST':
            verificar = True

            texto = request.POST.get("inputUser")
            if '@' in texto:
                if User.objects.filter(username=texto).exists():
                    usuario = User.objects.get(username=texto)
                    user = UserPerfil.objects.get(user=usuario)
   
                else:
                    mensaje = f"El usuario {texto} no se encuentra registrado en el sistema, lo invito a inscribirse"
                    return render(request, 'user/formularioqr.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':True})
            else:
                if UserPerfil.objects.filter(cedula=texto).exists():
                    user = UserPerfil.objects.get(cedula=texto)
                    
                else:
                    mensaje = f"El usuario {texto} no se encuentra registrado en el sistema, lo invito a inscribirse"
                    return render(request, 'user/formularioqr.html',{'idsesion':idsesion, 'mensaje':mensaje, 'estado':True})
            
            if Sesioncurso.objects.filter(id=idsesion).exists():
                sesion = Sesioncurso.objects.get(id=idsesion)
                cursos = GruposCursos.objects.filter(idcurso=sesion.idcurso)
                grupos = GruposUser.objects.filter(iduser=user)
                

                if SesionAsistencia.objects.filter(idsesioncurso=sesion, idusuario=user).exists():
                    mensaje="El usuario ya se encuentra registrado a esta sesión"
                    #=================================================================
                    usuarios = UserPerfil.objects.filter(idrol=2).exclude(id=user.id)
                    return render(request, 'user/listformuqr.html', {'idsesion':sesion, 'usu':user, 'usuarios': usuarios, 'formularios': formulario_sesion, 'preguntas': preguntas, 'datoscurso':datoscurso, 'fecha_actual':fecha_actual})
                    #return render(request, 'user/formularioqr.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':False})
  
                if verificar:
                    asistencia = SesionAsistencia(idsesioncurso=sesion, idusuario=user, asistencia_pendiente=True)
                    asistencia.save()
                    mensaje="Asistencia verificada"
                    #Aqui debe permitir redirigir y mostrar el formulario
                    usuarios = UserPerfil.objects.filter(idrol=2).exclude(id=user.id)
                    return render(request, 'user/listformuqr.html', {'idsesion':sesion, 'usu':user, 'usuarios': usuarios, 'formularios': formulario_sesion, 'preguntas': preguntas, 'datoscurso':datoscurso, 'fecha_actual':fecha_actual})
            else:
                mensaje = f'la sesion {idsesion} no existe'
                return render(request, 'user/formularioqr.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':False}) 
    else:    
        return render(request, 'user/formularioqr.html',{'idsesion':idsesion, 'estado':False})


#registrar al usuario si esta pendiente
def inscribirasistenteform(request, idsesion):
    #=================================================
    fecha_actual = date.today()
    preguntas = Preguntas.objects.all()
    formulario_sesion = SesionFormulario.objects.filter(idsesion=idsesion)
    datoscurso = Sesioncurso.objects.get(id=idsesion)
    #=====================================================
    if request.method == 'POST':
        try: 
            user = User.objects.create_user(username=request.POST['correo'], 
            password=request.POST['cedula'])
            user.save()
            rol_user = RolUser.objects.get(id=2)
            #id_cargo = request.POST['cargo']
            #id_empresa =  request.POST['empresa']
            #empresa_user = EmpresaAreas.objects.get(id=1)
            userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['apellido'], telefono=request.POST['telefono'], cedula=request.POST['cedula'], idrol=rol_user, cargo=None, idepart=None, user=user, pendiente=True )
            userper.save()
            sesion = Sesioncurso.objects.get(id=idsesion)
            grupo = GruposCursos.objects.filter(idcurso=sesion.idcurso).first()
            ingreso_grupo = GruposUser(idgrupo=grupo.idgrupo, iduser=userper, )
            ingreso_grupo.save()

            asistencia = SesionAsistencia(idsesioncurso=sesion, idusuario=userper, asistencia_pendiente=True)
            asistencia.save()
            usuarios = UserPerfil.objects.filter(idrol=2).exclude(id=user.id)
            return render(request, 'user/listformuqr.html', {'idsesion':sesion, 'usu':userper, 'usuarios': usuarios, 'formularios': formulario_sesion, 'preguntas': preguntas, 'datoscurso':datoscurso, 'fecha_actual':fecha_actual})
        except IntegrityError:
            messages.error(request, "Error al guardar el usuario")
            return redirect('validarasistenciaform', idsesion=idsesion)
    #end guardar usuario
    else:
        return redirect('validarasistenciaform', idsesion=idsesion)

#==================== aqui mostrar los formularios =======================
def listformuqr(request, idsesion, idusuario):
    print("Hola")

#============================ aqui guarda las respuestas del formulario sin logearse =======
def saveRespuestasFormu(request, idsesion, idformu, idusu):
    perfil_usuario = UserPerfil.objects.get(id=idusu)
    usuarios = UserPerfil.objects.filter(idrol=2).exclude(id=idusu)
    formulario_sesion = SesionFormulario.objects.filter(idsesion=idsesion)
    preguntasnew = Preguntas.objects.all()
    datoscurso = Sesioncurso.objects.get(id=idsesion)
    formu_completos = []
    respuestasForm = []
     # Obtén la fecha actual
    fecha_actual = date.today()
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
                       # si la pregunta es tipo 6 debe guardar el compromiso
                       elif pregunta.tipo == '6':
                            comentario = request.POST.get(f'compromiso{pregunta_id}')  # aqui llegan todas las respuestas de tipo texto largo y corto
                            prioridad = request.POST.get(f'prioridad{pregunta_id}') # aqui llega la prioridad
                            fecha = request.POST.get(f'fecha{pregunta_id}') # aqui llega la fecha final
                            personas_seleccionadas = request.POST.getlist(f'opcionesPersonas{pregunta_id}')
                            valorpreg = 0
                            existe_compromiso = RespuestaForm.objects.filter(iduser=perfil_usuario, idpreg=pregunta_id, idsesion=datoscurso).exists() #evaluar si existe
                            if not existe_compromiso:
                               rescompromiso = RespuestaForm(respuesta=comentario, tipores=pregunta.tipo, valores=valorpreg, idpreg=pregunta, iduser=perfil_usuario, idsesion=datoscurso)
                               rescompromiso.save()
                               # guardar los datos 
                               savecompromiso = Compromisos(compromiso=comentario, prioridad=prioridad, fecha_final=fecha, id_sesion=datoscurso, id_usuario=perfil_usuario, idrespuesta=rescompromiso)
                               savecompromiso.save()
                               #guardar las opciones de personas requeridas
                               if personas_seleccionadas:
                                  for perid in personas_seleccionadas:
                                      obtenerusu = UserPerfil.objects.get(id=perid)
                                      savePersonas = PersonasCompromisos(id_compromiso=savecompromiso, id_usuario=obtenerusu)
                                      savePersonas.save()
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
            return render(request, 'user/listformuqr.html', {'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntasnew, 'datoscurso':datoscurso, 'mensajeInfo':mensajeInfo, 'puntaje':puntaje_total, 'respuestasForm':respuestasForm, 'formcompleto':formu_completos, 'fecha_actual':fecha_actual, 'usuarios':usuarios})
       
       mensajeInfo = "Por favor complete todos los campos"
       puntaje_total = puntaje_total if puntaje_total is not None else 0
    return render(request, 'user/listformuqr.html', {'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntasnew, 'datoscurso':datoscurso, 'mensajeInfo':mensajeInfo, 'fecha_actual':fecha_actual, 'usuarios':usuarios})

