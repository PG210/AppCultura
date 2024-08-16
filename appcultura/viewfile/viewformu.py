from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #sirve para hacer las peticiones
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate #crea la sesion de un usuario al registrarse
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.db import IntegrityError #errores de la base de datos
from django.utils import timezone
from django.contrib import messages

from appcultura.modelos.grupouser import GruposUser
from appcultura.modelos.sesionasistencia import SesionAsistencia #mensajes para la vista
from ..models import UserPerfil, Formulario, Preguntas, Opciones, Curso, Sesioncurso, SesionFormulario, GruposCursos, RespuestaForm, FormadorEmpresa, Empresa
from django.http import Http404
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from datetime import date
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
    #======== el usuario es gerente =================
    elif perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        formu = Formulario.objects.filter(idempresa=idempresa) #=== filtrar los formularios asociados unicamente a la empresa
        cursos = Curso.objects.filter(idempresa=idempresa) 
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
    #==== formadores pertenecientes a una empresa (gerente) ========
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        formador_ids = FormadorEmpresa.objects.filter(idempresa=idempresa).values_list('idusu', flat=True).distinct()
        formadores = UserPerfil.objects.filter(id__in=formador_ids)
    else:
        formadores = UserPerfil.objects.filter(idrol=4)
    #================================================================
    if request.method == 'POST':
        # Acceder a los datos principales del formulario
        nomform = request.POST.get('nomform')
        desform = request.POST.get('desform')
        formador_select = request.POST.get('formador')
        #========= si es gerente debe tomar la empresa a la que pertenece ======
        if perfil_usuario.idrol.id == 5:
            empresa_select = perfil_usuario.idempresa.id
        else:
            empresa_select = request.POST.get('empresa')
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
    formu = Formulario.objects.get(id=idform)
    preguntas = Preguntas.objects.filter(idform=formu)
    #=========== si el usuario es administrador (gerente)==========0
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        formador_ids = FormadorEmpresa.objects.filter(idempresa=idempresa).values_list('idusu', flat=True).distinct()
        formadores = UserPerfil.objects.filter(id__in=formador_ids)
    else:
        formadores = UserPerfil.objects.filter(idrol=4)
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
    #============ para formador =========0
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        formador_ids = FormadorEmpresa.objects.filter(idempresa=idempresa).values_list('idusu', flat=True).distinct()
        formadores = UserPerfil.objects.filter(id__in=formador_ids)
    else:
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
    #=========== para nuevos formadores =============
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        formador_ids = FormadorEmpresa.objects.filter(idempresa=idempresa).values_list('idusu', flat=True).distinct()
        formadores = UserPerfil.objects.filter(id__in=formador_ids)
    else:
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
     #========== si el usuario es administrador (gerente) ==============
     if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        formador_ids = FormadorEmpresa.objects.filter(idempresa=idempresa).values_list('idusu', flat=True).distinct()
        formadores = UserPerfil.objects.filter(id__in=formador_ids)
     else:
        formadores = UserPerfil.objects.filter(idrol=4)
    #=========== save info =====
     if request.method == 'POST':
        # Acceder a los datos del formulario
        nombre_formulario = request.POST.get('nombre', '')
        descripcion_formulario = request.POST.get('descrip', '')
        formador_select = request.POST.get('formador')
        #========= si es gerente debe tomar la empresa a la que pertenece ======
        if perfil_usuario.idrol.id == 5:
            empresa_select = perfil_usuario.idempresa.id
        else:
            empresa_select = request.POST.get('empresa')
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
            nombre = f"{formulario_original.nombre} (Copia)",
            descrip = formulario_original.descrip,
            fecha = formulario_original.fecha,
            idempresa = formulario_original.idempresa,
            idusu = formulario_original.idusu,
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
    #===== si el usuario es gerente ==============================
    elif perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        formu = Formulario.objects.filter(idempresa=idempresa) #=== filtrar los formularios asociados unicamente a la empresa
        cursos = Curso.objects.filter(idempresa=idempresa) 
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
#====================================================
def porcentajes_totales(nvalor, usuarios_tot_form):
     valores = {}
     for usuario, formularios_data in nvalor.items():
        acum, totacum = 0, 0
        for formulario_data in formularios_data:
            acum += formulario_data['nota']
            totacum += formulario_data['valorform']  # Sumar el valor de cada formulario

        porglobal = round((acum * 100) / usuarios_tot_form[usuario], 1) if usuarios_tot_form.get(usuario) else 0  # Calcular el porcentaje global si el usuario tiene un valor total
        porespuesta = round((acum * 100) / totacum, 1) if totacum != 0 else 0  # Calcular el porcentaje de respuesta si el total acumulado no es cero

        valores[usuario] = {'porglobal': porglobal, 'porespuesta': porespuesta}  # Guardar los porcentajes para el usuario
     return valores
#======================nvalor===============================
def datos_nvalor(usuarios_con_formularios):
    nvalor = {}
    for usuario, formularios in usuarios_con_formularios.items():
        for formu in formularios:
            valor_total, valor_total_nota = 0, 0
            valor = Preguntas.objects.filter(idform=formu.id).aggregate(total=Sum('valor'))['total'] #=== valor del formulario
            valor_total += valor
            valor_nota = RespuestaForm.objects.filter(idpreg__idform=formu.id, iduser=usuario.id).aggregate(total_puntaje=Sum('valores'))['total_puntaje']
            valor_total_nota += valor_nota
            fecha_unica = RespuestaForm.objects.filter(idpreg__idform=formu.id, iduser=usuario.id).values_list('fechaenvio', flat=True).first()
            #====== porcentaje ========
            porcentaje = round((valor_total_nota * 100) / valor_total, 1)
            datos_form = {
                'form': formu,
                'fecha': fecha_unica,
                'nota': valor_total_nota,
                'valorform': valor_total,
                'porcentaje': porcentaje
            }
            # Aquí deberías agregar los datos a una lista, no convertir el diccionario a lista
            if usuario in nvalor:
                nvalor[usuario].append(datos_form)
            else:
                nvalor[usuario] = [datos_form]
    return nvalor   
#===========================================
def usuariosFormulario(usuarios_en_sesion, idcurso):
    usuarios_con_formularios = {}
    usuarios_cursos = {}
    formularios_del_usuario = {}
    nformu = {}
    usuarios_sesiones = {}
    fecha_hoy = date.today()
    formu_ids = ''
    tformu = 0
    #============= buscar las sesiones vinculadas al curso ========
    if idcurso != 0:
      idcursob = Curso.objects.get(id=idcurso)
      formu_ids = SesionFormulario.objects.filter(idsesion__idcurso=idcursob).values_list('idform', flat=True)
    #=======================
    if idcurso != 0:
        for usuid in usuarios_en_sesion:
            formularios_del_usuario = Formulario.objects.filter(preguntas__respuestaform__iduser=usuid, id__in=formu_ids).distinct()
            #==========================================
            cursos_usuario = Curso.objects.filter(id=idcursob.id).distinct()
            # Agregar el usuario y sus formularios al diccionario
            usuarios_con_formularios[usuid] = list(formularios_del_usuario)
            if cursos_usuario:
               usuarios_cursos[usuid] = list(cursos_usuario) # alamacena los cursos de los usuarios
    else:
        for usuid in usuarios_en_sesion:
            formularios_del_usuario = Formulario.objects.filter(preguntas__respuestaform__iduser=usuid).distinct()
            #==========================================
            cursos_usuario = Curso.objects.filter(sesioncurso__respuestaform__iduser=usuid).distinct()
            # Agregar el usuario y sus formularios al diccionario
            usuarios_con_formularios[usuid] = list(formularios_del_usuario)
            if cursos_usuario:
               usuarios_cursos[usuid] = list(cursos_usuario) # alamacena los cursos de los usuarios
    #================ hacer el calculo de los datos para los contestados ======================
    for usuario, formularios in usuarios_con_formularios.items():
        nformu[usuario] = len(formularios)
    #======  obtener la nota por cada formulario ====================
    nvalor = datos_nvalor(usuarios_con_formularios)
    #=============================================================
    #==== aqui se obtiene todos las sesiones asociadas a un curso del usuario =====
    usuarios_sesiones = {}
    usuarios_total_forms = {}
    for user, cursos in usuarios_cursos.items():
        sesiones_por_usuario = []
        for curso in cursos:
            sesiones = Sesioncurso.objects.filter(idcurso=curso.id, fechainicio__lt=fecha_hoy) #=== solo obtiene las sesiones anteriores a la fecha de hoy
            sesiones_por_usuario.extend(list(sesiones))
        usuarios_sesiones[user] = sesiones_por_usuario
    #========== obtiene las sesiones de los cursos asignados ================
    n_formularios = {}
    for user, sesiones in usuarios_sesiones.items():
        total_forms = 0
        lista_formularios = []
        for sesion in sesiones:
            n_forms_sesion = Formulario.objects.filter(sesionformulario__idsesion_id=sesion.id).count()
            total_forms += n_forms_sesion
            formu_usuario = Formulario.objects.filter(sesionformulario__idsesion_id=sesion.id)
            lista_formularios.extend(list(formu_usuario))
        usuarios_total_forms[user] = total_forms
        n_formularios[user] =lista_formularios
    
    #========== sumar los valores de formularios ====
    usuarios_tot_form = {}
    for user_perfil, formularios_u in n_formularios.items():
        total_contador = 0
        for formulario_n in formularios_u:
            valor_f = Preguntas.objects.filter(idform=formulario_n.id).aggregate(total=Sum('valor'))['total'] #=== valor del formulario
            total_contador += valor_f
            usuarios_tot_form[user_perfil] = total_contador 

    #======== sumar los formularios asignados  ==============
    if(idcurso != 0):
       tformu = SesionFormulario.objects.filter(idsesion__idcurso=idcurso).count()
    #print("Datos", usuarios_tot_form) # == total de valor que debe tener cada usuario
    #print('datos', usuarios_total_forms) #== numero de formularios que debe tener cada usuario
    #=======================porcentaje de formularios completados====================
    valores = porcentajes_totales(nvalor, usuarios_tot_form)
    #====================================================================
    info = {
        'usuarios_con_formularios':usuarios_con_formularios,
        'users':usuarios_en_sesion,
        'nformu': nformu,
        'nvalor': nvalor,
        'valores': valores,
        'formutotal': usuarios_total_forms,
        'tformu':tformu
    }
    #print('datos', info)
    return info
#======================================================
@login_required #proteger la ruta
def usersFomularios(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    cursos = ''
    nomcurso, datos = '', ''
    idcurso = ''
    if perfil_usuario.idrol.id == 4: #=== datos para el formador
        formador = FormadorEmpresa.objects.get(idusu=perfil_usuario, estado=True)
        idemp = formador.idempresa #=== id de la empresa que esta ubicado el usuario
        cursos = Curso.objects.filter(idusu=perfil_usuario.id)
        grupos_cursos = GruposCursos.objects.filter(idcurso__in=cursos).values('idgrupo').distinct()
        usuarios_grupo = GruposUser.objects.filter(idgrupo__in=grupos_cursos).values('iduser').distinct()
        #======= usuarios del formador ========
        usuarios_en_sesion = UserPerfil.objects.filter(Q(idarea__idempresa=idemp) | Q(idepart__idarea__idempresa=idemp), id__in=usuarios_grupo).exclude(idrol__in=[1, 4, 5])
        #=== filtrar datos por ultimo curso =======
        ultimo_registro = RespuestaForm.objects.filter(idsesion__idcurso__idempresa__id=idemp.id).order_by('-id').first()
        if ultimo_registro:
         idcurso = ultimo_registro.idsesion.idcurso.id
    #==== datos para el admin =======================
    elif perfil_usuario.idrol.id == 1: 
          usuarios_en_sesion = UserPerfil.objects.all().exclude(idrol__in=[1, 4, 5])
          cursos = Curso.objects.all()
          #=== filtra los datos por el ultimo curso ===========
          ultimo_registro = RespuestaForm.objects.order_by('-id').first()
          idcurso = ultimo_registro.idsesion.idcurso.id
    #=== si el usuario es jefe ============
    elif perfil_usuario.idrol.id == 3: 
          areajefe = perfil_usuario.idarea.id
          usuarios_en_sesion = UserPerfil.objects.filter(Q(idarea=areajefe) | Q(idepart__idarea=areajefe)).exclude(idrol__in=[1, 4, 5])
          #========= el curso debe pertenecer a la misma empresa =====
          idemp_id = perfil_usuario.idarea.idempresa.id
          ultimo_registro = RespuestaForm.objects.filter(idsesion__idcurso__idempresa__id=idemp_id).order_by('-id').first()
          if ultimo_registro:
             idcurso = ultimo_registro.idsesion.idcurso.id
    #=========== informacion para el usuario administrador 
    elif perfil_usuario.idrol.id == 5: 
          idempresa = perfil_usuario.idempresa.id
          usuarios_en_sesion = UserPerfil.objects.filter(Q(idarea__idempresa=idempresa) | Q(idepart__idarea__idempresa=idempresa)).exclude(idrol__in=[1, 4, 5])
          cursos = Curso.objects.filter(idempresa=idempresa)
          #========= el curso debe pertenecer a la misma empresa =====
          ultimo_registro = RespuestaForm.objects.filter(idsesion__idcurso__idempresa__id=idempresa).order_by('-id').first()
          if ultimo_registro:
             idcurso = ultimo_registro.idsesion.idcurso.id
    #=================================================  
    #=== obtener la informacion del ultino curso registrado ====
    if ultimo_registro:
       nomcurso = ultimo_registro.idsesion.idcurso.nombre
    if idcurso:
        datos = usuariosFormulario(usuarios_en_sesion, idcurso)
    return render(request, 'formularios/totalformu.html', {'usu':perfil_usuario, 'datos':datos, 'cursos':cursos, 'nomcurso':nomcurso})
#======================filtrar curso================================
#============================ funcion para filtrar datos por usuario ==============
def usuariosPorCurso(idcurso):
    cursos_sesiones = Sesioncurso.objects.filter(idcurso=idcurso)
    usuarios_con_formularios, usuarios_cursos,  formularios_del_usuario, nformu, usuarios_sesiones,   = {}, {}, {}, {}, {}
    fecha_hoy = date.today()
    usuarios_en_sesion = UserPerfil.objects.all()
    #=======================
    for sesiones in cursos_sesiones:
        usuarios_en_sesion = UserPerfil.objects.filter

    for usuid in usuarios_en_sesion:
        formularios_del_usuario = Formulario.objects.filter(preguntas__respuestaform__iduser_id=usuid).distinct()
        usuarios_con_formularios[usuid] = list(formularios_del_usuario)
    #================ hacer el calculo de los datos ======================
    for usuario, formularios in usuarios_con_formularios.items():
        nformu[usuario] = len(formularios)
    #======  obtener la nota por cada formulario ====================
    nvalor = datos_nvalor(usuarios_con_formularios)
    #=============================================================
    #==== aqui se obtiene todos las sesiones asociadas a un curso del usuario =====
    usuarios_sesiones = {}
    usuarios_total_forms = {}
    for user, cursos in usuarios_cursos.items():
        sesiones_por_usuario = []
        for curso in cursos:
            sesiones = Sesioncurso.objects.filter(idcurso=curso.id, fechainicio__lt=fecha_hoy) #=== solo obtiene las sesiones anteriores a la fecha de hoy
            sesiones_por_usuario.extend(list(sesiones))
        usuarios_sesiones[user] = sesiones_por_usuario
    
    n_formularios = {}
    for user, sesiones in usuarios_sesiones.items():
        total_forms = 0
        lista_formularios = []
        for sesion in sesiones:
            n_forms_sesion = Formulario.objects.filter(sesionformulario__idsesion_id=sesion.id).count()
            total_forms += n_forms_sesion
            formu_usuario = Formulario.objects.filter(sesionformulario__idsesion_id=sesion.id)
            lista_formularios.extend(list(formu_usuario))
        usuarios_total_forms[user] = total_forms
        n_formularios[user] =lista_formularios
    
    #========== sumar los valores de formularios ====
    usuarios_tot_form = {}
    for user_perfil, formularios_u in n_formularios.items():
        total_contador = 0
        for formulario_n in formularios_u:
            valor_f = Preguntas.objects.filter(idform=formulario_n.id).aggregate(total=Sum('valor'))['total'] #=== valor del formulario
            total_contador += valor_f
            usuarios_tot_form[user_perfil] = total_contador
    #print("Datos", usuarios_tot_form) # == total de valor que debe tener cada usuario
    #print('datos', usuarios_total_forms) #== numero de formularios que debe tener cada usuario
    #=======================porcentaje de formularios completados====================
    valores = porcentajes_totales(nvalor, usuarios_tot_form)
    #====================================================================
    info = {
        'usuarios_con_formularios':usuarios_con_formularios,
        'users':usuarios_en_sesion,
        'nformu': nformu,
        'nvalor': nvalor,
        'valores': valores,
        'formutotal': usuarios_total_forms
    }
    return info

@login_required
def filtroCurso(request, idcurso):
     curso = Curso.objects.get(id=idcurso)
     perfil_usuario = UserPerfil.objects.get(user=request.user)
     #========= informacion del usuario administrador (gerente)
     if perfil_usuario.idrol.id == 5:
         idempresa = perfil_usuario.idempresa.id
         cursos = Curso.objects.filter(idempresa=idempresa)
     else:
        cursos = Curso.objects.all()
     #datos_users = usuariosPorCurso(idcurso)
     #============ datos de usuarios ===========
     grupoasociado = GruposCursos.objects.filter(idcurso=idcurso)
     users_com = GruposUser.objects.none() 
     users_total = UserPerfil.objects.none()
     for grup in grupoasociado:
        users = GruposUser.objects.filter(idgrupo=grup.idgrupo.id).values('iduser').distinct()
        users_com = users_com.union(users)  # Unir los conjuntos de usuarios
     #============== usuario administrador (gerente) =================
     if perfil_usuario.idrol.id == 5: 
        idemp = perfil_usuario.idempresa.id
        for user in users_com:
            usu = UserPerfil.objects.filter(Q(idarea__idempresa=idemp) | Q(idepart__idarea__idempresa=idemp), id=user['iduser']).exclude(idrol__in=[1, 4, 5])
            users_total = users_total.union(usu)
     #========0 si el usuario es formador ==============
     if perfil_usuario.idrol.id == 4: 
         formador = FormadorEmpresa.objects.get(idusu=perfil_usuario, estado=True)
         idemp = formador.idempresa
         curso_n = Curso.objects.filter(id=curso.id, idusu=perfil_usuario.id)
         grupos_cursos = GruposCursos.objects.filter(idcurso__in=curso_n).values('idgrupo').distinct()
         usuarios_grupo = GruposUser.objects.filter(idgrupo__in=grupos_cursos).values('iduser').distinct()
         users_total = UserPerfil.objects.filter(Q(idarea__idempresa=idemp) | Q(idepart__idarea__idempresa=idemp), id__in=usuarios_grupo).exclude(idrol__in=[1, 4, 5])
         #======== cursos para el filtro ==========
         cursos = Curso.objects.filter(idusu=perfil_usuario.id)
     else:
        for user in users_com:
            usu = UserPerfil.objects.filter(id=user['iduser'])
            users_total = users_total.union(usu)
     #================= end datos usuarios ===========
     datos = usuariosFormulario(users_total, idcurso)
     nomcurso = curso.nombre
     return render(request, 'formularios/totalformu.html', {'usu':perfil_usuario, 'datos':datos, 'cursos':cursos, 'curso_ac':curso, 'nomcurso':nomcurso })

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

#============== gruardar el comentarios desdes el admin =============0
@login_required
def savecomentarioadmin(request):
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
    return redirect('usersFomularios')

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


