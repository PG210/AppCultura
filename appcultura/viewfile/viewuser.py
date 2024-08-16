from audioop import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from appcultura.modelos.avancecompromisos import AvanceCompromisos
from appcultura.modelos.calificacionusuarios import CalificacionUsuarios
from appcultura.modelos.compromisos import Compromisos
from appcultura.modelos.cursos import Curso
from appcultura.modelos.estado_compromisos import EstadoCompromisos
from appcultura.modelos.fechascompromiso import FechasCompromisos
from appcultura.modelos.gruposcursos import GruposCursos
from datetime import datetime, date
from django.contrib import messages
from appcultura.modelos.grupouser import GruposUser
from appcultura.modelos.opcionform import Opciones
from appcultura.modelos.sesionasistencia import SesionAsistencia
from appcultura.modelos.sesioncurso import Sesioncurso # proteger las rutas de accesos
from ..models import UserPerfil, SesionFormulario, RolUser, Preguntas, RespuestaForm, RespuestaOpciones, PersonasCompromisos, Formulario, CalificacionFormador, TemasSesion
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
                calificaciones = CalificacionUsuarios.objects.filter(curso=grupo_curso.idcurso)
                sesiones = Sesioncurso.objects.filter(idcurso=grupo_curso.idcurso)
                #for sesion in sesiones:
                    
    #========= verificar si existe una calificacion ========================
    vercalif = CalificacionUsuarios.objects.filter(idusuario=perfil_usuario)
    tematicas = TemasSesion.objects.all()
    return render(request, 'user/listcursos.html',{'usu':perfil_usuario, 'cursos':grupocurso, 'sesiones':sesiones, 'calificacion':calificaciones, 'asistencias':asistencias, 'vercalif':vercalif, 'tematicas':tematicas})

#================ guardar informacioncalificaciones al curso y formador =================
@login_required
def add_calificacion(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    id_curso = request.POST.get('idcurso')
    curso = Curso.objects.get(id=id_curso) #=== esto lo recibe por post
    #============== datos de la sesion del curso =================
    relevancia_curso = request.POST.get('relevancia')
    claridadpres_curso = request.POST.get('claridadpres')
    aplicabilidad_curso = request.POST.get('aplicabilidad')
    fortalezasesion_curso = request.POST.get('fortalezasesion')
    mejorasesion_curso = request.POST.get('mejorasesion')
        
    #=================== datos del formador =========================
    claridad_formador = request.POST.get('claridad')
    capacidad_formador = request.POST.get('capacidad')
    dominio_formador = request.POST.get('dominio')
    aspectos_formador = request.POST.get('aspectos')
    #=========== guardar la info =====================================
    if relevancia_curso is not None: #=== validar y que controle los post
        if CalificacionUsuarios.objects.filter( idusuario=perfil_usuario, curso=curso).exists():
            return redirect('calificacionCurso', idcurso=curso.id) #== si ya esta lleno debe retornar a la vista de datos completos
        else:
            dbcalificacion = CalificacionUsuarios(relevancia=relevancia_curso, claridad=claridadpres_curso, aplicabilidad=aplicabilidad_curso, fortalezas=fortalezasesion_curso, areasmejora=mejorasesion_curso,  idusuario=perfil_usuario, curso=curso, estado=False)
            dbcalificacion.save()
            #========= guardar la info del formador ==================
            dbformador = CalificacionFormador(claridad=claridad_formador, capacidad=capacidad_formador, dominio=dominio_formador, aspectosrescatar=aspectos_formador, usuario=perfil_usuario, formador=curso.idusu, curso=curso, estado=False)
            dbformador.save()
            mensaje = "Gracias por calificar nuestro servicio"
            return redirect('calificacionCurso', idcurso=curso.id)
    else:
        if CalificacionUsuarios.objects.filter(idusuario=perfil_usuario, curso=curso).exists():
           return redirect('calificacionCurso', idcurso=curso.id)
        else:
           return render(request, 'user/calificacion.html', {'usu':perfil_usuario, 'curso':curso})
#===========================================
#==============listar las respuestas de la calificacion ==========
@login_required
def calificacionCurso(request, idcurso):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    curso = Curso.objects.get(id=idcurso)
    #=== buscar todas las respuestas ==============
    rescurso = [] 
    recursos_sesion = CalificacionUsuarios.objects.filter(curso=curso, idusuario=perfil_usuario)
    rescurso.extend(recursos_sesion)
    #=========== buscar las calificaciones del formador ===============
    resformador = []
    resformador_sesion = CalificacionFormador.objects.filter(curso=curso, usuario=perfil_usuario)
    resformador.extend(resformador_sesion)
    #=======================
    return render(request, 'user/sesioncalif.html', {'usu':perfil_usuario, 'curso':curso, 'rescurso':rescurso, 'resformador':resformador, 'curso':curso})
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

#========== funcion para convertir las fechas ==========
@login_required
def cambiarEstadoCompromisos(perfil_usuario):
    fecha_actual = date.today()
    grupo_user = GruposUser.objects.filter(iduser=perfil_usuario)
    noterminado = EstadoCompromisos.objects.filter(descripcion__icontains="no cumplido").first()
    compromisos_anteriores = Compromisos.objects.filter(id_usuario=perfil_usuario, id_estado=2, fecha_final__lt=fecha_actual)  
    for comp in compromisos_anteriores:
        comp.id_estado = noterminado
        comp.save() 
    #===================================================================
    compromises = Compromisos.objects.filter(id_usuario=perfil_usuario) #=== aqui retorna los compromisos del user logueado
    if grupo_user:
        for user in grupo_user:
            cursos = GruposCursos.objects.filter(idgrupo=user.idgrupo)
    else:
        cursos = ""
    return fecha_actual, compromises, cursos
#=====================================
@login_required
def agregar_compromiso(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    user_all = UserPerfil.objects.filter(idrol=2).exclude(id=perfil_usuario.id)
    estadocom = EstadoCompromisos.objects.all()
    idcom = ""
    #==== modificar los compromisos que estan con la fecha vencida =====
    fecha_actual, compromises, cursos = cambiarEstadoCompromisos(perfil_usuario) #== informacion que retorna de la funcion
    if request.method == 'POST':
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
        message ="Compromiso agregado correctamente"
        return render(request, 'user/compromisos.html',{'usu':perfil_usuario, 'user_all':user_all, 'cursos':cursos, 'mensaje':message, 'compromisos':compromises, 'fechamin':fecha_actual, 'estadocom':estadocom, 'idcom':idcom})
    else:
        return render(request, 'user/compromisos.html',{'usu':perfil_usuario, 'user_all':user_all, 'cursos':cursos,'compromisos':compromises, 'fechamin':fecha_actual, 'estadocom':estadocom, 'idcom':idcom})

#============= funcion para dar clic desde el dashboard y lleve a compromisos
@login_required
def detalleCompromisoUser(request, idcom):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    user_all = UserPerfil.objects.filter(idrol=2).exclude(id=perfil_usuario.id)
    estadocom = EstadoCompromisos.objects.all()
    fecha_actual, compromises, cursos = cambiarEstadoCompromisos(perfil_usuario) 
    return render(request, 'user/compromisos.html',{'usu':perfil_usuario, 'user_all':user_all, 'cursos':cursos,'compromisos':compromises, 'fechamin':fecha_actual, 'estadocom':estadocom, 'idcom':idcom})


@login_required
def editarcompromiso(request, idcomp):
    if request.method == 'POST':
        compromiso = request.POST.get('textCompromiso')
        fecha = request. POST.get('fechafinal')
        personas = request.POST.getlist('idpersona')
        idestado = request.POST.get('estadoCom')
        # guardar la informacion de personas compromiso
        #personasActuales = PersonasCompromisos.objects.filter(id_compromiso=idcomp)
        estadopen = EstadoCompromisos.objects.get(id=2)
        estadoactual = EstadoCompromisos.objects.get(id=idestado)
        # buscar el objeto compromiso por el id
        updateCompromiso = get_object_or_404(Compromisos, id=idcomp)
        #==== validar si la fecha es mayor a la anterior =====
        updateCompromiso.compromiso =  compromiso
        fechafin = updateCompromiso.fecha_final
        fechanew = datetime.strptime(fecha, '%Y-%m-%d').date() #type str a date
        if fechafin<fechanew:
           updateCompromiso.fecha_final = fecha
           updateCompromiso.id_estado = estadopen
           addfecha = FechasCompromisos(fechadd=fecha, idcompromiso=updateCompromiso)
           addfecha.save()
        else:
           updateCompromiso.id_estado = estadoactual
        updateCompromiso.save()
        # registrar los usuarios
        if 'noaplica' in request.POST:
            deletePersonas = PersonasCompromisos.objects.filter(id_compromiso=idcomp)
            deletePersonas.delete()
        else:
            # guardar la informacion
            deletePersonas = PersonasCompromisos.objects.filter(id_compromiso=idcomp)
            deletePersonas.delete()
            for userper in personas:
                buscaruser = get_object_or_404(UserPerfil, id=userper)
                addPersonas = PersonasCompromisos(id_compromiso=updateCompromiso, id_usuario=buscaruser)
                addPersonas.save()
        return redirect('compromisos')
    else:
        return redirect('compromisos')

#================ agregar avances al compromisos============
@login_required
def craeteAvance(request):
    if request.method == 'POST':
        fechaini = request.POST.get('fecini', '')
        fechafin = request.POST.get('fecfin', '')
        estado = request.POST.get('estado', '')
        activ = request.POST.get('actividad', '')
        idcom = request.POST.get('idcom')
        compromiso = get_object_or_404(Compromisos, id=idcom)
        addavance = AvanceCompromisos(fechaini=fechaini, fechafin=fechafin, actividad=activ, estado=estado, idcompromiso=compromiso)
        addavance.save()
        messages.error(request, 'Actividad agregada de manera exitosa.')
        return redirect('compromisos')
    
#============ actualizar los avances ==========  
@login_required
def updateAvance(request, idavance):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    print('id del avance', idavance)
    if request.method == 'POST':
       updateavance = get_object_or_404(AvanceCompromisos, id=idavance)
       updateavance.fechaini = request.POST.get('fechainiavance', '')
       updateavance.fechafin = request.POST.get('fechafinavance', '')
       updateavance.actividad = request.POST.get('actividad', '')
       updateavance.estado = request.POST.get('estadoavance', '')
       updateavance.puntaje = request.POST.get('puntos', '')
       updateavance.respuesta = request.POST.get('respuesta', '')
       updateavance.idusurespuesta = perfil_usuario
       updateavance.save()
       messages.success(request, 'Actividad actualizada exitosamente.')
       return redirect('compromisos')
      

# ============== eliminar los avances =========
@login_required
def deleteAvance(request, idavance):
    elim = get_object_or_404(AvanceCompromisos, id=idavance)
    elim.delete()
    messages.success(request, 'Actividad eliminada exitosamente.')
    return redirect('compromisos') 
#=============== aqui evaluar formularios del QR
# crear la ruta que permite ver el formulario en linea
def verFormuQR(request, idsesion):
    return render(request, 'user/formularioqr.html', {'idsesion':idsesion})

#======== buscar los usuarios por empresa ==============
def usuariosEmpresa(user):
    try:
        idempresa_1 = user.idarea.idempresa
    except AttributeError:
        idempresa_1 = None

    try:
        idempresa_2 = user.idepart.idarea.idempresa
    except AttributeError:
        idempresa_2 = None
        #=========== asignar el valor que no sea nulo=========
    idemp = idempresa_1 if idempresa_1 is not None else idempresa_2
    usuarios = UserPerfil.objects.filter(Q(idarea__idempresa=idemp) | Q(idepart__idarea__idempresa=idemp)).exclude(idrol__in=[1, 4, 5]).exclude(id=user.id).order_by('nombre')
    return usuarios

# validar que el usuario este registrado 
def validarasistenciaform(request, idsesion):
    #=================================================
    fecha_actual = date.today()
    preguntas = Preguntas.objects.all()
    formulario_sesion = SesionFormulario.objects.filter(idsesion=idsesion)
    datoscurso = Sesioncurso.objects.get(id=idsesion)
    estado = False #=== este estado es para controlar la ultima sesion
    buscar = False
    #=====================================================
    if request.method == 'POST':
            #verificar = True
            mensaje="Tu asistencia ha sido verificada. Por favor, completa los formularios de evaluación si están disponibles"
            texto = request.POST.get("inputUser").lower()
           
            if User.objects.filter(username=texto).exists():
                usuario = User.objects.get(username=texto)
                user = UserPerfil.objects.get(user=usuario)
            else:
                mensaje = f"El usuario {texto} no se encuentra registrado en el sistema, lo invito a inscribirse"
                return render(request, 'user/formularioqr.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':True})

            if Sesioncurso.objects.filter(id=idsesion).exists():
                sesion = Sesioncurso.objects.get(id=idsesion)
                #== contar la ultima sesion del curso sesion del curso ==========
                curso = sesion.idcurso
                sesiones = Sesioncurso.objects.filter(idcurso=sesion.idcurso).latest('fechafin')
                if sesiones.id == sesion.id:
                    estado = True
                #================================================================================
                if SesionAsistencia.objects.filter(idsesioncurso=sesion, idusuario=user).exists():
                    #========================= buscar la empresa para obtener los usuarios========================================
                    usuarios = usuariosEmpresa(user)
                    print('mensaje', mensaje)
                    #=== si la asistencia ya esta verificada debe ver si tiene o no formularios =========
                    return render(request, 'user/listformuqr.html', {'idsesion':sesion, 'usu':user, 'usuarios': usuarios, 'formularios': formulario_sesion, 'preguntas': preguntas, 'datoscurso':datoscurso, 'fecha_actual':fecha_actual, 'estado':estado, 'curso':curso, 'buscar':buscar, 'mensaje':mensaje})
                else:
                    asistencia = SesionAsistencia(idsesioncurso=sesion, idusuario=user, asistencia_pendiente=False)
                    asistencia.save()
                    #========== buscar a que empresa pertenece este usuario ========
                    print('mensaje', mensaje)
                    usuarios = usuariosEmpresa(user)
                    return render(request, 'user/listformuqr.html', {'idsesion':sesion, 'usu':user, 'usuarios': usuarios, 'formularios': formulario_sesion, 'preguntas': preguntas, 'datoscurso':datoscurso, 'fecha_actual':fecha_actual, 'estado':estado, 'curso':curso, 'buscar':buscar, 'mensaje':mensaje})
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
            userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['apellido'], telefono=request.POST['telefono'], cedula=request.POST['cedula'], idrol=rol_user, user=user, pendiente=True )
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
def saveRespuestasFormu(request):
    #============ obtener datos ================
    idsesion = request.POST.get('idsesion', '')
    idformu = request.POST.get('idformu', '')
    idusu = request.POST.get('idusu', '')
    valorform = request.POST.get('valorformu', '')
    #===========================================
    perfil_usuario = UserPerfil.objects.get(id=idusu)
    usuarios = UserPerfil.objects.filter(idrol=2).exclude(id=idusu)
    formulario_sesion = SesionFormulario.objects.filter(idsesion=idsesion)
    preguntasnew = Preguntas.objects.all()
    datoscurso = Sesioncurso.objects.get(id=idsesion)
    formu_completos = []
    respuestasForm = []
    mensajeInfo, puntaje_total = '', ''
    buscar = False
    estado = False
     # Obtén la fecha actual
    fecha_actual = date.today()
    #== contar la ultima sesion del curso sesion del curso ==========
    lastsesiones = Sesioncurso.objects.filter(idcurso=datoscurso.idcurso).latest('fechafin')
    if lastsesiones.id == datoscurso.id:
        estado = True
    #=============================Formulario ==============================
    if request.method == 'POST':
       if request.POST.items():
          if valorform == '1':
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
                               
                               if 'noaplica' not in request.POST:
                                    if personas_seleccionadas:
                                        for perid in personas_seleccionadas:
                                            obtenerusu = UserPerfil.objects.get(id=perid)
                                            savePersonas = PersonasCompromisos(id_compromiso=savecompromiso, id_usuario=obtenerusu)
                                            savePersonas.save()
            #====== mensaje de exito =============
            mensajeInfo = "La información se ha registrado éxitosamente"
            puntaje_total = RespuestaForm.objects.filter(idpreg__idform=idformu, iduser=perfil_usuario).aggregate(total_puntaje=Sum('valores'))['total_puntaje']
            puntaje_total = puntaje_total if puntaje_total is not None else 0
            #============== validar el formulario de encuesta ==============
            buscar = CalificacionUsuarios.objects.filter(idusuario=perfil_usuario, curso=datoscurso.idcurso).exists()
            if buscar:
               buscar = True #=== debe cambiar a verdadero
          #================= validar el else para agregar un formulario de evaluacion de cursos =========
          elif valorform == '2':
            #=== variables del formulario 2 ======
            id_curso = request.POST.get('idcurso')
            curso = Curso.objects.get(id=id_curso) #=== esto lo recibe por post
            #============== datos de la sesion del curso =================
            relevancia_curso = request.POST.get('relevancia')
            claridadpres_curso = request.POST.get('claridadpres')
            aplicabilidad_curso = request.POST.get('aplicabilidad')
            fortalezasesion_curso = request.POST.get('fortalezasesion')
            mejorasesion_curso = request.POST.get('mejorasesion')
            #=================== datos del formador =========================
            claridad_formador = request.POST.get('claridad')
            capacidad_formador = request.POST.get('capacidad')
            dominio_formador = request.POST.get('dominio')
            aspectos_formador = request.POST.get('aspectos')
            #============== calificación del curso =======================
            buscar = CalificacionUsuarios.objects.filter( idusuario=perfil_usuario, curso=curso).exists()
            if not buscar:
               dbcalificacion = CalificacionUsuarios(relevancia=relevancia_curso, claridad=claridadpres_curso, aplicabilidad=aplicabilidad_curso, fortalezas=fortalezasesion_curso, areasmejora=mejorasesion_curso,  idusuario=perfil_usuario, curso=curso, estado=False)
               dbcalificacion.save()
               #========= guardar la info del formador ==================
               dbformador = CalificacionFormador(claridad=claridad_formador, capacidad=capacidad_formador, dominio=dominio_formador, aspectosrescatar=aspectos_formador, usuario=perfil_usuario, formador=curso.idusu, curso=curso, estado=False)
               dbformador.save()
               buscar = True #=== debe cambiar a verdadero
            pass
          #========== validar si ya esta lleno el formulario ===============
          for formulario in formulario_sesion:
              existe_formu = RespuestaForm.objects.filter(idpreg__idform=formulario.idform, iduser=perfil_usuario).exists()
              # Si ya está registrado, quítalo de la variable formulario_sesion
              if existe_formu:
                 formu_completos.append(formulario.idform) # aggrega al ultimo elememto un formulario
                 formulario_sesion = formulario_sesion.exclude(pk=formulario.pk)
            #============== buscar formularios terminados ===============
          respuestasForm = RespuestaForm.objects.filter(iduser=perfil_usuario, idsesion=datoscurso)
          return render(request, 'user/listformuqr.html', {'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntasnew, 'datoscurso':datoscurso, 'mensajeInfo':mensajeInfo, 'puntaje':puntaje_total, 'respuestasForm':respuestasForm, 'formcompleto':formu_completos, 'fecha_actual':fecha_actual, 'usuarios':usuarios, 'curso':datoscurso.idcurso, 'buscar':buscar, 'estado':estado})
       
       mensajeInfo = "Por favor complete todos los campos"
       puntaje_total = puntaje_total if puntaje_total is not None else 0
    return render(request, 'user/listformuqr.html', {'usu': perfil_usuario, 'formularios': formulario_sesion, 'preguntas': preguntasnew, 'datoscurso':datoscurso, 'mensajeInfo':mensajeInfo, 'fecha_actual':fecha_actual, 'usuarios':usuarios})

#==================== mostrar todos los formularios pertenecientes a un curso ==================
@login_required
def formulariosCurso(request, idcurso):
    print(idcurso)