from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #sirve para hacer las peticiones
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.db import IntegrityError #errores de la base de datos
from ..models import UserPerfil, Curso, Sesioncurso, ObjetivosCurso, Area, Departamento, Kpiarea, Kpiobjetivos, EmpresaAreas
from django.contrib import messages #mensajes para la vista


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
  
#eliminar curso
@login_required #proteger la ruta
def eliminarcurso(request, idcurso):
    try:
        curso = Curso.objects.get(id=idcurso)
        curso.delete()
        messages.success(request, 'Curso eliminado exitosamente.')
    except Curso.DoesNotExist:
        messages.error(request, 'El curso no existe.')
    return redirect('listarcursos')

#editar curso
@login_required #proteger la ruta
def editarcurso(request, idcurso):
     perfil_usuario = UserPerfil.objects.get(user=request.user)
     curso = Curso.objects.get(id=idcurso)
     sesiones = Sesioncurso.objects.filter(idcurso=curso)
     objetivos = ObjetivosCurso.objects.filter(idcurso=curso)
     if request.method == 'POST':
        curso.nombre = request.POST.get('nombre')
        curso.descrip = request.POST.get('descrip')
        curso.precio = request.POST.get('precio')
        curso.save()
     
        for objetivo in objetivos:
            # Obtener los valores actualizados del formulario
            descripobj = request.POST.get(f'descripobj_{objetivo.id}')
            competencias = request.POST.get(f'competencias_{objetivo.id}')

            # Aplicar los cambios a la sesión actual
            objetivo.descrip = descripobj
            objetivo.competencias = competencias
            objetivo.save()

        for sesion in sesiones:
            # Obtener los valores actualizados del formulario
            nueva_fecha_inicio = request.POST.get(f'fechainicio_{sesion.id}')
            nueva_fecha_fin = request.POST.get(f'fechafin_{sesion.id}')
            nuevo_lugar = request.POST.get(f'lugar_{sesion.id}')

            # Aplicar los cambios a la sesión actual
            sesion.fechainicio = nueva_fecha_inicio
            sesion.fechafin = nueva_fecha_fin
            sesion.lugar = nuevo_lugar
            sesion.save()
        messages.success(request, 'Curso actualizado exitosamente.')
        return redirect('listarcursos')
     else:
         return render(request, 'admin/updatecurso.html', {'usu':perfil_usuario, 'curso': curso, 'sesiones': sesiones, 'objetivos': objetivos})
     
#crear funcion para crear kpi de area o departamento  
@login_required #proteger la ruta
def kpiarea(request):
    try:
        perfil_usuario = UserPerfil.objects.get(user=request.user)
        if request.method == 'POST':
            # ================= here the KPI of areas =============
            objetivos = request.POST.getlist('objetivos[]')
            metas = request.POST.getlist('metas[]')
            indicadores = request.POST.getlist('indicadores[]')
            idem = perfil_usuario.idempresa  # aquí se obtiene la empresa a la cual pertenece
            idemp = idem.idempresa  # se obtiene el idempresa
            idarea = request.POST.get('area')
            iddepartamento = request.POST.get('depar')
            print('res', iddepartamento)
            #=========== validar si es nulo para aplicar a toda el area ===============
            try:
                if iddepartamento == 'none':
                    empresa_area = EmpresaAreas.objects.get(idempresa=idemp, idarea=idarea, idepar__isnull=True)
                else:
                    empresa_area = EmpresaAreas.objects.get(idempresa=idemp, idarea=idarea, idepar=iddepartamento)
            except EmpresaAreas.DoesNotExist:
                    messages.error(request, 'No se encontró la empresa o área especificada.')
                    return redirect('kpiarea')
            
            # ========= guardar la info en la tabla de kpis area =========
            regkpi = Kpiarea(nombre=request.POST['nombre'], descrip=request.POST['descrip'],
                             fechaini=request.POST['fechaini'], fechafin=request.POST['fechafin'],
                             valor=request.POST['valor'], idemparea=empresa_area)
            regkpi.save()
            
            # ================ guardar los objetivos de kpi ==============
            idkpi = Kpiarea.objects.get(id=regkpi.id)
            
            # ======= here register of objectives of course ============
            for objetivo, meta, indicador in zip(objetivos, metas, indicadores):
                regobjkpi = Kpiobjetivos(objtivo=objetivo, meta=meta, indicador=indicador, idkpi=idkpi)
                regobjkpi.save()
            
            messages.success(request, 'KPI registrado exitosamente.')
            return redirect('kpiarea')
    except UserPerfil.DoesNotExist:
        messages.error(request, 'No se encontró el perfil de usuario asociado.')
    except Exception as e:
        messages.error(request, f'Ocurrió un error: {e}')
    
    area = Area.objects.all()
    depart = Departamento.objects.all()
    return render(request, 'admin/kpiareasdep.html', {'usu': perfil_usuario, 'area': area, 'depart': depart})

#listar KPIs de cada area
def listarkpiarea(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    kparea = Kpiarea.objects.all()
    kpobj = Kpiobjetivos.objects.all()
    return render(request, 'admin/listkpi.html', {'usu': perfil_usuario, 'kpareas':kparea, 'kpobjs':kpobj})

#editar kpi de cada area
def editarkpi(request, idkpi):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    datoskpi = Kpiarea.objects.get(id=idkpi)
    objetivos = Kpiobjetivos.objects.filter(idkpi=datoskpi)
    if request.method == 'POST':
        #=======validar el id de la empresa ==================
        idem = perfil_usuario.idempresa  # aquí se obtiene la empresa a la cual pertenece
        idemp = idem.idempresa  # se obtiene el idempresa
        idarea = request.POST.get('area')
        iddepartamento = request.POST.get('depar')
        try:
            empresa_area = EmpresaAreas.objects.get(idempresa=idemp, idarea=idarea, idepar=iddepartamento)
        except EmpresaAreas.DoesNotExist:
            messages.error(request, 'No se encontró la empresa o área especificada.')
            return redirect('kpiarea')
        #====================================================
        datoskpi.nombre = request.POST.get('nombre')
        datoskpi.descrip = request.POST.get('descrip')
        datoskpi.fechaini = request.POST.get('fecini')
        datoskpi.fechafin = request.POST.get('fecfin')
        datoskpi.valor = request.POST.get('valor')
        datoskpi.estado = request.POST.get('estado')
        datoskpi.idemparea = empresa_area
        datoskpi.save()

        for objetivo in objetivos:
                # Obtener los valores actualizados del formulario
                descripobj = request.POST.get(f'descripobj_{objetivo.id}')
                metas = request.POST.get(f'meta_{objetivo.id}')
                indicador = request.POST.get(f'indicador_{objetivo.id}')

                # Aplicar los cambios a la sesión actual
                objetivo.objtivo = descripobj
                objetivo.meta = metas
                objetivo.indicador = indicador
                objetivo.save() 
        messages.success(request, 'Curso actualizado exitosamente.')
        return redirect('listarkpiarea')
    else:
        infokpi = Kpiarea.objects.get(id=idkpi)
        obkpi = Kpiobjetivos.objects.filter(idkpi=idkpi)
        area = Area.objects.all()
        depart = Departamento.objects.all()
        return render(request, 'admin/updatekpi.html', {'usu': perfil_usuario, 'infokpis':infokpi, 'obkpis':obkpi, 'area':area, 'depart':depart})

#eliminar kpi de un area
@login_required #proteger la ruta
def eliminarkpi(request, idkpi):
    try:
        kpi = Kpiarea.objects.get(id=idkpi)
        kpi.delete()
        messages.success(request, 'Kpi eliminado exitosamente.')
    except Kpiarea.DoesNotExist:
        messages.error(request, 'El Kpi no existe.')
    return redirect('listarkpiarea')
