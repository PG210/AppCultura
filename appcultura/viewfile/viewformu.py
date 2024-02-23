from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #sirve para hacer las peticiones
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate #crea la sesion de un usuario al registrarse
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.db import IntegrityError #errores de la base de datos
from django.utils import timezone
from django.contrib import messages

from appcultura.modelos.sesionasistencia import SesionAsistencia #mensajes para la vista
from ..models import UserPerfil, Formulario, Preguntas, Opciones, Curso, Sesioncurso, SesionFormulario, GruposCursos, RespuestaForm, FormadorEmpresa, Empresa
from django.http import Http404
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
#importar modelos 

from appcultura.viewfile.fadmin.functionadmin import generar_qr

#vista principal de crear formularios
@login_required #proteger la ruta
def listarformu(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    preg = Preguntas.objects.filter()
    agregados = SesionFormulario.objects.filter()
    #==================================================
    if perfil_usuario.idrol.id == 4:
        empselect = FormadorEmpresa.objects.get(idusu=perfil_usuario.id, estado=True) 
        formu = Formulario.objects.filter(idusu=perfil_usuario, idempresa=empselect.idempresa) 
        cursos = Curso.objects.filter(idusu=perfil_usuario, idempresa=empselect.idempresa) 
    else:  
        formu = Formulario.objects.filter()
        cursos = Curso.objects.all()

    # Crear un diccionario para almacenar los cursos y sus sesiones respectivas
    cursos_sesiones = {}
    for curso in cursos:
        sesiones = Sesioncurso.objects.filter(idcurso=curso)
        # Almacenar el curso y sus sesiones en el diccionario
        cursos_sesiones[curso] = sesiones
    context = {'cursos_sesiones': cursos_sesiones, 'usu':perfil_usuario, 'formu':formu, 'preg':preg, 'agregados':agregados}
    #=========================== end sesiones ===============
    return render(request, 'formularios/listarformu.html', context)

#===================== Aqui agregar formularios a una sesion ==========
@login_required
def addsesionform(request, idform):
    if request.method == 'POST':
        # ========== buscar los datos ===========
        formu = Formulario.objects.get(id=idform)
        selec = request.POST.getlist(f'sesionCurso[]')
        agregados = SesionFormulario.objects.filter(idform=formu).values('idsesion')
        # ======== buscar la hora local ===================
        fecha_actual_utc = timezone.now()
        fecha_actual_local = timezone.localtime(fecha_actual_utc)
        # ==================================================
        sesiones_existentes = [agregado['idsesion'] for agregado in agregados]

        sesiones_usuario = [int(id_sesion) for id_sesion in selec]

        sesiones_a_eliminar = set(sesiones_existentes) - set(sesiones_usuario)

        SesionFormulario.objects.filter(idform=formu, idsesion__in=sesiones_a_eliminar).delete()

        # sesiones restantes
        for id_sesion in sesiones_usuario:
            sesiones = Sesioncurso.objects.get(id=id_sesion)

            if SesionFormulario.objects.filter(idform=formu, idsesion=sesiones).exists():
                continue  # Si existe continuar
            # Si no existe, se puede proceder con el registro
            datosformu = SesionFormulario(fecha=fecha_actual_local, idform=formu, idsesion=sesiones)
            datosformu.save()
    
    return redirect('listarformu')


@login_required #proteger la ruta
def crearformu(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    formadores = UserPerfil.objects.filter(idrol=4)
    if request.method == 'POST':
        # Acceder a los datos principales del formulario
        nomform = request.POST.get('nomform')
        desform = request.POST.get('desform')
        empresa_select = request.POST.get('empresa')
        formador_select = request.POST.get('formador')
        
        # Validar que el nombre no se repita
        if Formulario.objects.filter(nombre=nomform).exists():
            msj= 'El nombre del formulario debe ser único.'
            return render(request, 'formularios/crearformu.html', {'usu':perfil_usuario, 'msj':msj})
        # Crear y guardar el formulario principal
        fecha_actual_utc = timezone.now()
        fecha_actual_local = timezone.localtime(fecha_actual_utc)
        #========== validar quien crea el formulario =====================
        if perfil_usuario.idrol.id == 4:
           formador = FormadorEmpresa.objects.get(idusu=perfil_usuario, estado=True)
           id_usuario = formador.idusu
           id_empresa = formador.idempresa
        else:
            if formador_select and empresa_select:
                perfil_formador = UserPerfil.objects.get(id=formador_select)
                empresa_sel = Empresa.objects.get(id=empresa_select)   
                id_usuario = perfil_formador
                id_empresa = empresa_sel 
            else:
                id_usuario = None
                id_empresa = None
        datosformu = Formulario(nombre=nomform, descrip=desform, fecha=fecha_actual_local, idempresa=id_empresa, idusu=id_usuario)
        datosformu.save()

        # Procesar preguntas y tipos de formulario
        preguntas = []
        tipos_formulario = []
        valores = []

        for key, value in request.POST.items():
            if key.startswith('pregunta_fila'):
                preguntas.append(value)
            elif key.startswith('tipoform_fila'):
                tipos_formulario.append(value)
            elif key.startswith('valorpreg_fila'):
                valores.append(value)

        # Crear y guardar las preguntas asociadas al formulario
        for pregunta, tipo_formulario, valor in zip(preguntas, tipos_formulario, valores):
            savepreg = Preguntas(descrip=pregunta, tipo=tipo_formulario, valor=valor, idform=datosformu)
            savepreg.save()

            # Procesar las opciones para preguntas de varias opciones
            if tipo_formulario == '3':
                opciones_key = f'opciones_fila{preguntas.index(pregunta)}[]'
                opciones = request.POST.getlist(opciones_key)
                for opcion in opciones:
                    saveoption = Opciones(descrip=opcion, idpreg=savepreg)
                    saveoption.save()

            #procesar preguntas de tipo varias opciones con unica respuesta
            if tipo_formulario == '4':
                opt_key = f'radioname_fila{preguntas.index(pregunta)}[]'
                optiones = request.POST.getlist(opt_key)

                # Obtener la opción correcta del radio button
                opcion_correcta_key = f'radionum_fila{preguntas.index(pregunta)}'
                opcion_correcta = int(request.POST[opcion_correcta_key][0])

                for i, opcion in enumerate(optiones):
                    goption = Opciones(descrip=opcion, idpreg=savepreg)

                    # Marcar la opción correcta
                    if i == opcion_correcta - 1:
                        goption.correcta = True

                    goption.save()
            #procesar multiples respuestas verdaderas
            if tipo_formulario == '5':
                chec_key = f'cheknom_fila{preguntas.index(pregunta)}[]'
                checks = request.POST.getlist(chec_key)

                check_values_key = f'checkval_fila{preguntas.index(pregunta)}'
                check_values = request.POST.getlist(check_values_key)

                for i, opc in enumerate(checks, start=1):  # Comenzar desde 1
                    gcheck = Opciones(descrip=opc, idpreg=savepreg)

                    # Marcar las opciones correctas
                    if str(i) in check_values:
                        gcheck.correcta = True

                    gcheck.save()
          

        msjsuccess= 'Los datos se han guardado correctamente.'
        return render(request, 'formularios/crearformu.html', {'usu':perfil_usuario, 'msjsuc':msjsuccess, 'formadores':formadores})
    else:
        return render(request, 'formularios/crearformu.html', {'usu':perfil_usuario, 'formadores':formadores})
    # Resto de tu vista...

@login_required #proteger la ruta
def editarform(request, idform):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    formadores = UserPerfil.objects.filter(idrol=4)
    formu = Formulario.objects.get(id=idform)
    preguntas = Preguntas.objects.filter(idform=formu)
    return render(request, 'formularios/editarform.html', {'usu':perfil_usuario, 'formu':formu, 'preguntas':preguntas, 'formadores':formadores})

@login_required #proteger la ruta
def eliminarPregunta(request, idpreg, idformu):
    try:
        pregunta = Preguntas.objects.get(id=idpreg)
        pregunta.delete()
    except Preguntas.DoesNotExist:
        raise Http404("La pregunta no existe")
    msj = "La pregunta se ha eliminado de manera exitosa."
    return redirect(editarform, idform=idformu)

@login_required #proteger la ruta
def addNewPreguntas(request, idform):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    formu = Formulario.objects.get(id=idform)
    preguntasnew = Preguntas.objects.filter(idform=formu)
    formadores = UserPerfil.objects.filter(idrol=4)
    if request.method == 'POST':
        formu = Formulario.objects.get(id=idform) #aqui encuentra el id del formulario
        # Procesar preguntas y tipos de formulario
        preguntas = []
        tipos_formulario = []
        valores = []

        for key, value in request.POST.items():
            if key.startswith('pregunta_fila'):
                preguntas.append(value)
            elif key.startswith('tipoform_fila'):
                tipos_formulario.append(value)
            elif key.startswith('valorpreg_fila'):
                valores.append(value)

        # Crear y guardar las preguntas asociadas al formulario
        for pregunta, tipo_formulario, valor in zip(preguntas, tipos_formulario, valores):
            savepreg = Preguntas(descrip=pregunta, tipo=tipo_formulario, valor=valor, idform=formu)
            savepreg.save()

            # Procesar las opciones para preguntas de varias opciones
            if tipo_formulario == '3':
                opciones_key = f'opciones_fila{preguntas.index(pregunta)}[]'
                opciones = request.POST.getlist(opciones_key)
                for opcion in opciones:
                    saveoption = Opciones(descrip=opcion, idpreg=savepreg)
                    saveoption.save()

            #procesar preguntas de tipo varias opciones con unica respuesta
            if tipo_formulario == '4':
                opt_key = f'radioname_fila{preguntas.index(pregunta)}[]'
                optiones = request.POST.getlist(opt_key)

                # Obtener la opción correcta del radio button
                opcion_correcta_key = f'radionum_fila{preguntas.index(pregunta)}'
                opcion_correcta = int(request.POST[opcion_correcta_key][0])

                for i, opcion in enumerate(optiones):
                    goption = Opciones(descrip=opcion, idpreg=savepreg)

                    # Marcar la opción correcta
                    if i == opcion_correcta - 1:
                        goption.correcta = True

                    goption.save()
            #procesar multiples respuestas verdaderas
            if tipo_formulario == '5':
                chec_key = f'cheknom_fila{preguntas.index(pregunta)}[]'
                checks = request.POST.getlist(chec_key)

                check_values_key = f'checkval_fila{preguntas.index(pregunta)}'
                check_values = request.POST.getlist(check_values_key)

                for i, opc in enumerate(checks, start=1):  # Comenzar desde 1
                    gcheck = Opciones(descrip=opc, idpreg=savepreg)

                    # Marcar las opciones correctas
                    if str(i) in check_values:
                        gcheck.correcta = True

                    gcheck.save()
        seccionform = 'seccionCampos'
        return render(request, 'formularios/editarform.html', {'usu':perfil_usuario, 'formu':formu, 'preguntas':preguntasnew, 'seccionform':seccionform, 'formadores':formadores})

@login_required #proteger la ruta
def eliminarRespuesta(request, idres, idform):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    formu = Formulario.objects.get(id=idform)
    preguntasnew = Preguntas.objects.filter(idform=formu)
    formadores = UserPerfil.objects.filter(idrol=4)
    try:
        opt = Opciones.objects.get(id=idres)
        opt.delete()
        pregunta_id = opt.idpreg.id
        return render(request, 'formularios/editarform.html', {'usu':perfil_usuario, 'formu':formu, 'preguntas':preguntasnew, 'nseccion':pregunta_id, 'formadores':formadores})
    except Opciones.DoesNotExist:
         return redirect(editarform, idform=idform)
   
@login_required #proteger la ruta
def savePreguntas(request, idform):
     perfil_usuario = UserPerfil.objects.get(user=request.user)
     formadores = UserPerfil.objects.filter(idrol=4)
     if request.method == 'POST':
        # Acceder a los datos del formulario
        nombre_formulario = request.POST.get('nombre', '')
        descripcion_formulario = request.POST.get('descrip', '')
        empresa_select = request.POST.get('empresa')
        formador_select = request.POST.get('formador')
        # Crear el formulario
        #========== validar quien crea el formulario =====================
        if perfil_usuario.idrol.id == 4:
           formador = FormadorEmpresa.objects.get(idusu=perfil_usuario, estado=True)
           id_usuario = formador.idusu
           id_empresa = formador.idempresa
        else:
            if formador_select and empresa_select:
                perfil_formador = UserPerfil.objects.get(id=formador_select)
                empresa_sel = Empresa.objects.get(id=empresa_select)   
                id_usuario = perfil_formador
                id_empresa = empresa_sel 
            else:
                id_usuario = None
                id_empresa = None
        Formulario.objects.filter(id=idform).update(nombre=nombre_formulario, descrip=descripcion_formulario, idempresa=id_empresa, idusu=id_usuario) 
        # Iterar sobre los datos del formulario
        pregunta_id = None  # Inicializa la variable fuera del bucle
        if request.POST.items():
            for key, value in request.POST.items():
                if key.startswith('pregunta') and value:
                       pregunta_id = key.split('pregunta')[1]
                       puntaje = request.POST.get(f'puntaje{pregunta_id}', '') #puntaje actual que llega
                       pregunta_ask = request.POST.get(f'pregunta{pregunta_id}', '') # pregunta que llega desde el front
                       # Obtener la pregunta existente
                    
                       pregunta = Preguntas.objects.get(id=pregunta_id)
                       pregunta.descrip = pregunta_ask
                       pregunta.valor = puntaje
                       pregunta.save()

                       if pregunta.tipo == '3':
                            # Obtener las opciones múltiples asociadas a la pregunta
                            opciones = request.POST.getlist(f'opcionesmul_{pregunta_id}[]')
                            # Crear las opciones
                            for opcion_texto in opciones:
                                opcion = Opciones(descrip=opcion_texto, idpreg=pregunta)
                                opcion.save()
                       elif pregunta.tipo == '4':
                            oponemarcada = request.POST.getlist(f'radionum_{pregunta_id}')
                            print(oponemarcada)
                            try:
                                opcion_one_correcta = int(oponemarcada[0])
                            except (ValueError, IndexError):
                                # Manejar errores de conversión a entero o índice fuera de rango
                                opcion_one_correcta = None
                            
                            if opcion_one_correcta is not None:
                                oponesvar = request.POST.getlist(f'radioname_{pregunta_id}[]')

                                for i, opcion_seleccionada in enumerate(oponesvar):
                                    goneopc = Opciones(descrip=opcion_seleccionada, idpreg=pregunta)

                                    # Marcar la opción correcta
                                    if i == opcion_one_correcta - 1:
                                        goneopc.correcta = True

                                    goneopc.save()

                            #============= guardar respuestas de multiples respuestas ==========
                       elif pregunta.tipo == '5':
                            opcionvar = request.POST.getlist(f'cheknom_{pregunta_id}[]')
                            checkmarcados =  request.POST.getlist(f'checkval_{pregunta_id}')

                            for i, texto_opcionvar in enumerate(opcionvar, start=1):
                                opcionv = Opciones(descrip=texto_opcionvar, idpreg=pregunta)
                                
                                if str(i) in checkmarcados:
                                    opcionv.correcta = True
                                
                                opcionv.save()
                    # si la pregunta no existe
        formu = Formulario.objects.get(id=idform)
        preguntasnew = Preguntas.objects.filter(idform=formu)
        return render(request, 'formularios/editarform.html', {'usu':perfil_usuario, 'formu':formu, 'preguntas':preguntasnew, 'nseccion':pregunta_id, 'formadores':formadores})

@login_required #proteger la ruta
def copiarform(request, idform): #copiar o duplicar el formulario con todos los atributos
    formulario_original = get_object_or_404(Formulario, id=idform)
    with transaction.atomic():
        # Duplicar el formulario
        formulario_nuevo = Formulario.objects.create(
            nombre=f"{formulario_original.nombre} (Copia)",
            descrip=formulario_original.descrip,
            fecha=formulario_original.fecha,
        )
        # Duplicar las preguntas asociadas
        # Duplicar las preguntas asociadas
        for pregunta_original in Preguntas.objects.filter(idform=formulario_original):
            pregunta_nueva = Preguntas.objects.create(
                descrip=pregunta_original.descrip,
                tipo=pregunta_original.tipo,
                valor=pregunta_original.valor,
                idform=formulario_nuevo,
            )
            # Duplicar las opciones asociadas a la pregunta
            for opcion_original in Opciones.objects.filter(idpreg=pregunta_original):
                    Opciones.objects.create(
                        descrip=opcion_original.descrip,
                        correcta=opcion_original.correcta,
                        idpreg=pregunta_nueva,
                    )  
    return redirect(listarformu)
    
#eliminar el formulario por completo
@login_required #proteger la ruta
def eliminarForm(request, idform):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    try:
        formudelete = Formulario.objects.get(id=idform)
        formudelete.delete()
        newmensaje = "Formulario eliminado de manera exitosa."
    except Formulario.DoesNotExist:
        newmensaje = "Error al eliminar el formulario."
    #==================== validar =========================
    if perfil_usuario.idrol.id == 4:
        empselect = FormadorEmpresa.objects.get(idusu=perfil_usuario.id, estado=True) 
        formu = Formulario.objects.filter(idusu=perfil_usuario, idempresa=empselect.idempresa) 
        cursos = Curso.objects.filter(idusu=perfil_usuario, idempresa=empselect.idempresa) 
    else:  
        formu = Formulario.objects.filter()
        cursos = Curso.objects.all()
    #==============================================================
    cursos_sesiones = {}
    for curso in cursos:
        sesiones = Sesioncurso.objects.filter(idcurso=curso)
        # Almacenar el curso y sus sesiones en el diccionario
        cursos_sesiones[curso] = sesiones
    #=====================================
    preg = Preguntas.objects.filter()
    agregados = SesionFormulario.objects.filter()
    return render(request, 'formularios/listarformu.html', {'usu':perfil_usuario, 'formu':formu, 'newmensaje':newmensaje, 'cursos_sesiones': cursos_sesiones, 'preg':preg, 'agregados':agregados})

#listar los formularios completados de los usuarios
@login_required #proteger la ruta
def usersFomularios(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    if perfil_usuario.idrol.id == 4:
          empselect = FormadorEmpresa.objects.get(idusu=perfil_usuario.id, estado=True) 
          cursosvin = Curso.objects.filter(idusu=perfil_usuario, idempresa=empselect.idempresa) 
    else:  
          cursosvin = Curso.objects.all()
    return render(request, 'formularios/listcurso.html', {'usu':perfil_usuario, 'cursosvin':cursosvin })

@login_required #proteger la ruta
def verFomrsesion(request, idsesion):
    mensajeExito = ''
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    formulario_sesion = SesionFormulario.objects.filter(idsesion=idsesion)
    usuarios_en_sesion = UserPerfil.objects.filter(respuestaform__idsesion_id=idsesion).distinct()
    #==============================================
    usuarios_asistencia = SesionAsistencia.objects.filter(idsesioncurso__id=idsesion, asistencia_pendiente=False)
    usuarios_confirmar = SesionAsistencia.objects.filter(idsesioncurso__id=idsesion, asistencia_pendiente=True)
    #=======================
    usuarios_con_formularios = {}
    formularios_del_usuario = {}
    for usuid in usuarios_en_sesion:
        formularios_del_usuario = Formulario.objects.filter(
            preguntas__respuestaform__iduser_id=usuid
        ).distinct()
        # Agregar el usuario y sus formularios al diccionario
        usuarios_con_formularios[usuid] = list(formularios_del_usuario)
    #========================= guardar comentarios del formulario ===========
    if request.method == 'POST':
        #print(request.POST)
        comentarios_dict = dict(request.POST.lists())
        for key, value in comentarios_dict.items():
            if key.startswith('comentario_'):
                respuesta_id = int(key.split('_')[1])
                comentario = value[0]
                #actualizar la respuesta
                RespuestaForm.objects.filter(id=respuesta_id).update(comentario=comentario, estado=False)
        mensajeExito = "Comentarios agregados de manera exitosa."
    return render(request, 'formularios/formucompletos.html', {'usu':perfil_usuario, 'users':usuarios_en_sesion, 'formularios':formulario_sesion, 'usuarios_con_formularios':usuarios_con_formularios, 'idsesion':idsesion, 'mensajeExito':mensajeExito, 'usuarios_asistencia':usuarios_asistencia, 'usuarios_confirmar':usuarios_confirmar})

# Qr para compartir formulario
def qr_formulario(request, idsesion):
    data = f'http://localhost:8000/evaluar/test/{idsesion}/'
    relative_path = generar_qr(data,idsesion)
    return render(request, 'admin/codigoqr.html',{"qr_code_url":relative_path, 'idsesion':idsesion, 'data':data})

#============== cambiar pendiente desde los formularios ===============
login_required    
def cambiar_pendiente_formulario(request, idsesion, iduser):
    usuario = UserPerfil.objects.get(id=iduser)
    usuario.pendiente = False
    usuario.save()
    asistencia = SesionAsistencia.objects.get(idusuario=usuario, idsesioncurso=idsesion)
    asistencia.asistencia_pendiente = False
    asistencia.save()
    return redirect('verFomrsesion', idsesion=idsesion)


