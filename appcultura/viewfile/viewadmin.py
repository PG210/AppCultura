from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #sirve para hacer las peticiones
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.db import IntegrityError #errores de la base de datos
from ..models import UserPerfil
from ..models import Curso #cursos
from ..models import  Sesioncurso #sesiones de cursos
from ..models import ObjetivosCurso


@login_required #proteger la ruta
def registroCursos(request):
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  if request.method == 'POST':
      #=== Get data lists =======
      fechas_inicio = request.POST.getlist('fecha_inicio[]')
      fechas_final = request.POST.getlist('fecha_final[]')
      lugares = request.POST.getlist('lugar[]')
      descripciones = request.POST.getlist('desobj[]')
      competencias = request.POST.getlist('competencias[]')
      nombre_curso = request.POST['nombre']
      
      #================ verify that all variables have data ==============
      if not any(fechas_inicio) or not any(fechas_final) or not any(lugares):
            mensaje = "Error: El curso debe tener al menos una sesión."
            return render(request, 'admin/addcurso.html', {'usu':perfil_usuario, 'msj':mensaje})

      #================= find the name course  =============
      if Curso.objects.filter(nombre=nombre_curso).exists():
            mensaje = "Error: El nombre del curso ya está registrado."
            return render(request, 'admin/addcurso.html', {'usu':perfil_usuario, 'msj':mensaje})
     
      #================= here the courses =============
      regcurso = Curso(nombre=request.POST['nombre'], descrip=request.POST['descrip'], precio=request.POST['precio'])
      regcurso.save()
      idcurso = Curso.objects.get(id=regcurso.id)

      #======= here register of objectives of course ==========
      for description, competencia in zip(descripciones, competencias):
            regobject = ObjetivosCurso(descrip=description, competencias=competencia, idcurso=idcurso)
            regobject.save()

      #==================here save the session of course =================
      for fecha_inicio, fecha_final, lugar in zip(fechas_inicio, fechas_final, lugares):
            regsesion = Sesioncurso(fechainicio=fecha_inicio, fechafin=fecha_final, lugar=lugar, estado=1, idcurso=idcurso)
            regsesion.save()

      #========= send messaje and return the view of courses =================
      mensaje = "Curso registrado exitosamente"
      return render(request, 'admin/addcurso.html', {'usu':perfil_usuario, 'msj':mensaje})
  else:
      return render(request, 'admin/addcurso.html', {'usu':perfil_usuario})
  
#Vista para listar cursos
@login_required #proteger la ruta
def listarcursos(request):
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  if request.method == 'GET':
       cursos = Curso.objects.all()
       sesiones = Sesioncurso.objects.all()
       objetivos = ObjetivosCurso.objects.all()
       return render(request, 'admin/listcursos.html', {'usu':perfil_usuario, 'cursos':cursos, 'sesiones':sesiones, 'objetivos':objetivos})