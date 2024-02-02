from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #sirve para hacer las peticiones
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate #crea la sesion de un usuario al registrarse
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.db import IntegrityError #errores de la base de datos

from ..models import UserPerfil, Formulario, Preguntas, Opciones, Curso, Sesioncurso, SesionFormulario, GruposCursos, RespuestaForm
from django.http import Http404

def viewhome(request):
    if request.method == 'POST':
        email = request.POST['username']
        if 'password' in request.POST:
            estado = 1
            passw = request.POST['password']
            user = authenticate(request, username=email, password=passw)
            usercom  = get_object_or_404(User, username=user)
            perfilusu = get_object_or_404(UserPerfil, user=usercom)
            if user is None:
                return render(request, 'formador/home.html', {
                    'error': 'Tu usuario ya esta registrado, te invitamos a iniciar sesión.',
                    'estado': estado
                })
            else:
                if perfilusu.idrol.id == 4:
                   login(request, user) #crear la sesion
                   return redirect('administracion') # redirecciona a otra vista
                else:
                   return render(request, 'formador/home.html', {
                          'error': 'Tu usuario no es formador.',
                          'estado': estado  })
        else:
            buscar = User.objects.filter(username=email).exists()
            estado = ''
            if buscar:
                estado = 1
                return render(request, 'formador/home.html', {
                    'error': "Tu usuario ya esta registrado, te invitamos a iniciar sesión.",
                    'estado': estado
                    })  
            else:
                estado = 0
                return render(request, 'formador/home.html', {
                        'error': "El formador no esta registrado, te invitamos a crear tu cuenta.",
                        'estado': estado
                        })  
        #user = authenticate(request, username=request.POST['username'], password=request.POST['pass'])
        #password=request.POST['password']
    return render(request, 'formador/home.html')

def registerTrainer(request):
    print('nueva vista')