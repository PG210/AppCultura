from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #sirve para hacer las peticiones
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate #crea la sesion de un usuario al registrarse
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.db import IntegrityError #errores de la base de datos

#importar modelos 
from ..models import UserPerfil

#vista principal de crear formularios
@login_required #proteger la ruta
def crearformu(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    if request.method == 'POST':
       print(request.POST)
       # Acceder a los datos del formulario utilizando el objeto request.POST
       nomform = request.POST.get('nomform')
       desform = request.POST.get('desform')

        # Procesar otras entradas, por ejemplo, preguntas y tipos de formulario
       preguntas = []
       tipos_formulario = []

       for key, value in request.POST.items():
          if key.startswith('pregunta_fila'):
              preguntas.append(value)
          elif key.startswith('tipoform_fila'):
              tipos_formulario.append(value)

        # Procesar preguntas y tipos de formulario según tus necesidades
       for pregunta, tipo_formulario in zip(preguntas, tipos_formulario):
            print(f'Pregunta: {pregunta}, Tipo de formulario: {tipo_formulario}')

        # También puedes procesar las opciones para preguntas de varias opciones
       for key, value in request.POST.items():
            if key.startswith('opciones_fila'):
                opciones = request.POST.getlist(key)
                print(f'Opciones para {key}: {opciones}')

        # Aquí puedes realizar el procesamiento adicional que necesites
        # ...
    else:
     return render(request, 'formularios/crearformu.html', {'usu':perfil_usuario})

@login_required #proteger la ruta
def listarformu(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    return render(request, 'formularios/listarformu.html', {'usu':perfil_usuario})


