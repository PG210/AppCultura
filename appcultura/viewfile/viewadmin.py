from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #sirve para hacer las peticiones
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.contrib import messages #mensajes para la vista
from django.db import IntegrityError #errores de la base de datos
from ..models import UserPerfil
from ..models import Curso #cursos
from ..models import  Sesioncurso #sesiones de cursos
from ..models import ObjetivosCurso
from ..models import TamEmpresa, SectorEmpresa, Empresa, GrupoEmpresa


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

#Rergistro de Empresas
@login_required
def registroEmpresa(request):
    grupem = Empresa.objects.all()
    sec = SectorEmpresa.objects.all()
    varible = TamEmpresa.objects.all()
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    if request.method == 'POST':
        #=== Get data lists =======
        nombre = request.POST['nameEmp']
        nit = request.POST['nit']
        direction = request.POST['direccion']
        email = request.POST['correo']
        phone = request.POST['telefono']
        #groupEmp = request.POST['groupEmp']
        sector = request.POST['sector']
        tamanio = request.POST['tamanioEmp']
        #grpEmp = GrupoEmpresa.objects.get(pk=groupEmp)
        tmp = TamEmpresa.objects.get(pk=tamanio)
        sc = SectorEmpresa.objects.get(pk=sector)
        
        if not any(nombre) or not any(nit) or not any(direction) or not any(email) or not any(phone):
            mensaje = "Los campos no pueden quedar vacios"
            return render(request, 'admin/addempresa.html', {'usu':perfil_usuario, 'tamempresa':varible, 'secEmp':sec, 'grp':grupem, 'mensaje':mensaje})
        
        if Empresa.objects.filter(nit=nit).exists():
            mensaje = "La empresa ya se encuentra registrada"
            return render(request, 'admin/addempresa.html', {'usu':perfil_usuario, 'tamempresa':varible, 'secEmp':sec, 'grp':grupem, 'mensaje':mensaje})
        
        regEmpresa = Empresa(nombre=nombre, nit=nit, direccion=direction, correo=email, telefono=phone, idtam=tmp, idsector=sc)
        regEmpresa.save()
        mensaje = "Datos guardados exitosamente"
        return render(request, 'admin/addempresa.html', {'usu':perfil_usuario, 'tamempresa':varible, 'secEmp':sec, 'grp':grupem, 'mensaje':mensaje})
    else:
        return render(request, 'admin/addempresa.html', {'usu':perfil_usuario, 'tamempresa':varible, 'secEmp':sec, 'grp':grupem})

#Vista para listar cursos
@login_required #proteger la ruta
def listarcursos(request):
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  if request.method == 'GET':
       cursos = Curso.objects.all()
       sesiones = Sesioncurso.objects.all()
       objetivos = ObjetivosCurso.objects.all()
       return render(request, 'admin/listcursos.html', {'usu':perfil_usuario, 'cursos':cursos, 'sesiones':sesiones, 'objetivos':objetivos})
   
#Vista para listar Empresas
@login_required
def listarempresa(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    emp = Empresa.objects.all()
    return render(request, 'admin/listempresas.html', {'usu':perfil_usuario,'emp':emp})

@login_required
def eliminarempresa(request, idempresa):
    try:
        emp = Empresa.objects.get(id=idempresa)
        emp.delete()
        messages.success(request, 'Empresa eliminada exitosamente.')
    except Empresa.DoesNotExist:
        messages.error(request, 'La empresa no Existe')
    return redirect('listarempresa')

@login_required #proteger la ruta
def modificarempresa(request, idempresa):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    empresa = Empresa.objects.get(id=idempresa)
    grpEmp = GrupoEmpresa.objects.all()
    sector = SectorEmpresa.objects.all()
    tamint = TamEmpresa.objects.all()
    if request.method == 'POST':
        empresa.nombre = request.POST.get('nameEmp')
        empresa.nit = request.POST.get('nit')
        empresa.direccion = request.POST.get('direccion')
        empresa.correo = request.POST.get('correo')
        empresa.telefono = request.POST.get('telefono')
        empresa.idgrupoem_id = request.POST.get('groupEmp')
        empresa.idsector_id = request.POST.get('sector')
        empresa.idtam_id = request.POST.get('tamanioEmp')
        empresa.save()
        messages.success(request, 'Empresa actualizada exitosamente.')
        return redirect('listarempresa')
    else:
        return render(request, 'admin/updateempresa.html', {'usu':perfil_usuario, 'empresa':empresa, 'sector':sector, 'grpEmp':grpEmp, 'tamint':tamint})