from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #sirve para hacer las peticiones
from .models import RolUser
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate #crea la sesion de un usuario al registrarse
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.db import IntegrityError #errores de la base de datos
from .models import UserPerfil




# Create your views here.
#vista para home
def home(request):
 return render(request, 'home.html') # retorma la vista competa

#vista para login 
def loginuser(request):
    if request.method == 'POST':
         user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
         if user is None:
            return render(request, 'layoutsinicio/login.html', {
                  'error': "Usuario o contraseña no valido",
               })
         else:
              #======= validar que no este desactivado =============
              usercom  = get_object_or_404(User, username=user)
              perfilusu = get_object_or_404(UserPerfil, user=usercom)
             
              if perfilusu.estado == 1:
                  login(request, user) #crear la sesion
                  return redirect('administracion') # redirecciona a otra vista
              else:
                 print('El usuario esta desactivado:', perfilusu.estado)
                 return render(request, 'layoutsinicio/login.html', {
                  'error': "el usuario esta desactivado, contacte al administrador.",
                })  
    else:
         return render(request, 'layoutsinicio/login.html') 

#funcion para cerrar la sesion
def singout(request):
    logout(request) #Aqui destruye la sesion
    return redirect('home')

#vista para registro
def reguser(request):
 rol = RolUser.objects.all()
 if request.method == 'POST':
     #print(request.POST)
     if request.POST['pass1'] == request.POST['pass2']:
          try: 
              user = User.objects.create_user(username=request.POST['email'], 
              password=request.POST['pass1'])
              user.save()
              login(request, user) #crear la sesion
              user_id = User.objects.latest('id').id
              user_n = User.objects.get(id=user_id)
              id_rol = request.POST['rol']
              rol_user = RolUser.objects.get(id=id_rol)
              cargo_em = request.POST.get('cargo', '')
              id_empresa =  request.POST['empresa']
              #empresa_user = EmpresaAreas.objects.get(id=id_empresa)
              userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['ape'], cedula=request.POST['ced'], idrol=rol_user, cargo=cargo_em, idepart=None, user=user_n )
              userper.save()
              return redirect('administracion') # redirecciona a otra vista
          except IntegrityError:
                return render(request, 'layoutsinicio/registro.html', {'error': 'Usuario ya existe', 'rol':rol})
     return render(request, 'layoutsinicio/registro.html',  {'rol': rol, 'error': 'La contraseña no es igual'})
 #end guardar usuario
 else:
      return render(request, 'layoutsinicio/registro.html',  {'rol': rol}) 
 
 #vista para iniciar el admin
@login_required #proteger la ruta
def administracion(request):
  #usuario_logeado = request.user #obtener el usuario logeado
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  nombre_cargo = perfil_usuario.cargo
  return render(request, 'admin/inicio.html', {'usu':perfil_usuario, 'cargo':nombre_cargo})


 
  