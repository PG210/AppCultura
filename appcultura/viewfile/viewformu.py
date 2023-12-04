from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #sirve para hacer las peticiones
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate #crea la sesion de un usuario al registrarse
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.db import IntegrityError #errores de la base de datos
from django.utils import timezone
from django.contrib import messages #mensajes para la vista
from ..models import UserPerfil, Formulario, Preguntas, Opciones
from django.http import Http404
from django.http import JsonResponse
#importar modelos 

#vista principal de crear formularios
@login_required #proteger la ruta
def listarformu(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    formu = Formulario.objects.filter()
    preg = Preguntas.objects.filter()
    return render(request, 'formularios/listarformu.html', {'usu':perfil_usuario, 'formu':formu, 'preg':preg})

@login_required #proteger la ruta
def crearformu(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    if request.method == 'POST':
        # Acceder a los datos principales del formulario
        print(request.POST)
        nomform = request.POST.get('nomform')
        desform = request.POST.get('desform')
        
        # Validar que el nombre no se repita
        if Formulario.objects.filter(nombre=nomform).exists():
            msj= 'El nombre del formulario debe ser único.'
            return render(request, 'formularios/crearformu.html', {'usu':perfil_usuario, 'msj':msj})
        # Crear y guardar el formulario principal
        fecha_actual_utc = timezone.now()
        fecha_actual_local = timezone.localtime(fecha_actual_utc)
        datosformu = Formulario(nombre=nomform, descrip=desform, fecha=fecha_actual_local)
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
        return render(request, 'formularios/crearformu.html', {'usu':perfil_usuario, 'msjsuc':msjsuccess})
    else:
        return render(request, 'formularios/crearformu.html', {'usu':perfil_usuario})
    # Resto de tu vista...

@login_required #proteger la ruta
def editarform(request, idform):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    formu = Formulario.objects.get(id=idform)
    preguntas = Preguntas.objects.filter(idform=formu)
    return render(request, 'formularios/editarform.html', {'usu':perfil_usuario, 'formu':formu, 'preguntas':preguntas})

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
        return redirect(editarform, idform=idform)

@login_required #proteger la ruta
def eliminarRespuesta(request, idres, idform):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    formu = Formulario.objects.get(id=idform)
    preguntasnew = Preguntas.objects.filter(idform=formu)
    try:
        opt = Opciones.objects.get(id=idres)
        print('valor de opt', opt)
        opt.delete()
        pregunta_id = opt.idpreg.id
        return render(request, 'formularios/editarform.html', {'usu':perfil_usuario, 'formu':formu, 'preguntas':preguntasnew, 'nseccion':pregunta_id})
    except Opciones.DoesNotExist:
         return redirect(editarform, idform=idform)
   
@login_required #proteger la ruta
def savePreguntas(request, idform):
     perfil_usuario = UserPerfil.objects.get(user=request.user)
     formu = Formulario.objects.get(id=idform)
     preguntasnew = Preguntas.objects.filter(idform=formu)
     if request.method == 'POST':
        # Acceder a los datos del formulario
        nombre_formulario = request.POST.get('nombre', '')
        descripcion_formulario = request.POST.get('descrip', '')

        # Crear el formulario
        formulario = Formulario.objects.get(id=idform)
        formulario.nombre = nombre_formulario
        formulario.descrip = descripcion_formulario
        formulario.save()
        
        # Iterar sobre los datos del formulario
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
        return render(request, 'formularios/editarform.html', {'usu':perfil_usuario, 'formu':formu, 'preguntas':preguntasnew, 'nseccion':pregunta_id})
                    
        