from ast import Delete
from email import message
import json
import os
import mimetypes
from pdb import post_mortem
import select
from turtle import back
from urllib import request, response
from django.conf import settings
from django.core.files.storage import FileSystemStorage, default_storage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect #sirve para hacer las peticiones
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.contrib import messages #mensajes para la vista
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.db import transaction
from django.utils import timezone
from numpy import append
import pandas as pd
from appcultura.modelos import estado_compromisos
from appcultura.modelos.calificacionformador import CalificacionFormador

from appcultura.modelos.calificacionusuarios import CalificacionUsuarios
from appcultura.modelos.compromisos import Compromisos
from appcultura.modelos.estado_compromisos import EstadoCompromisos
from appcultura.modelos.formador_empresa import FormadorEmpresa
from appcultura.modelos.sesionformulario import SesionFormulario #errores de la base de datos
from ..models import UserPerfil, Curso, Sesioncurso, ObjetivosCurso, Area, Departamento, Kpiarea, Kpiobjetivos
from django.contrib import messages #mensajes para la vista
from ..models import TemasSesion, Grupos, GruposCursos, GruposUser, Competencias, CompetenciaCurso
from ..models import TamEmpresa, SectorEmpresa, Empresa, GrupoEmpresa
from django.db.models import Subquery, OuterRef, Q
from ..models import TamEmpresa, SectorEmpresa, Empresa, GrupoEmpresa, SesionAsistencia, RolUser
from django.db.models import Subquery, OuterRef

#Codigo Jhon
from django.views import View
from django.http import JsonResponse
from django.core.serializers import serialize
from django.urls import reverse
from io import BytesIO

from appcultura.viewfile.fadmin.functionadmin import generar_qr
#from appcultura.viewfile.fadmin.timesesion import tiempo #=== para contar el tiempo de sesion
#Fin Codigo Jhon

@login_required #proteger la ruta
def registroCursos(request):
  #====== datos =============
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  comp = Competencias.objects.all()
  formadores = UserPerfil.objects.filter(idrol=4)
  grupos = Grupos.objects.all()
  empresa = Empresa.objects.all()
  if perfil_usuario.idrol.id == 4: 
      pformador = FormadorEmpresa.objects.get(idusu=perfil_usuario, estado=True)
      grupos = Grupos.objects.filter(idempresa=pformador.idempresa)
  elif perfil_usuario.idrol.id == 5:
      idemp = perfil_usuario.idempresa.id
      empresa = Empresa.objects.filter(id=idemp)
      grupos = Grupos.objects.filter(idempresa=idemp)
  #==== add user =============
  rol = RolUser.objects.all()
  sectores = SectorEmpresa.objects.all()
  tamanios = TamEmpresa.objects.all()
  if request.method == 'POST':
      #=== Get data lists =======
      fechas_inicio = request.POST.getlist('fecha_inicio[]')
      fechas_final = request.POST.getlist('fecha_final[]')
      lugares = request.POST.getlist('lugar[]')
      descripciones = request.POST.getlist('desobj[]')
      #competencias = request.POST.getlist('competencias[]')
      compe = request.POST.getlist('compe')
      nombre_curso = request.POST['nombre']
      formador_select = request.POST.get('formador', '')
      empresa_select = request.POST.get('empresa', '')
      precio = 0
      
      #================ verify that all variables have data ==============
      if not any(fechas_inicio) or not any(fechas_final) or not any(lugares):
            mensaje = "Error: El curso debe tener al menos una sesión."
            return render(request, 'admin/addcurso.html', {'usu':perfil_usuario, 'msj':mensaje})

      #================= find the name course  =============
      if Curso.objects.filter(nombre=nombre_curso).exists():
            mensaje = "Error: El nombre del curso ya está registrado."
            return render(request, 'admin/addcurso.html', {'usu':perfil_usuario, 'msj':mensaje})
     
      #================= here the courses =============
      #====== look on the rol =========================
      if perfil_usuario.idrol.id == 4: 
          #buscar a que empresa y el formador para guardarlo en la tabla
          idformador = FormadorEmpresa.objects.get(idusu=perfil_usuario, estado=True)
          id_formador = idformador.idusu
          id_empresa = idformador.idempresa
      else:
          if formador_select and empresa_select:
              perfil_formador = UserPerfil.objects.get(id=formador_select)
              empresa_sel = Empresa.objects.get(id=empresa_select)   
              #==== vincular el formador con la empresa ==========
              if not FormadorEmpresa.objects.filter(idempresa=empresa_sel, idusu=perfil_formador).exists():
                 saveFormador = FormadorEmpresa(idempresa=empresa_sel, idusu=perfil_formador)
                 saveFormador.save()
              #===================================
              id_formador = perfil_formador
              id_empresa = empresa_sel 
          else:
              id_formador = None
              id_empresa = None

      regcurso = Curso(nombre=request.POST['nombre'], descrip=request.POST['descrip'], precio=precio, idempresa=id_empresa, idusu=id_formador)
      regcurso.save()
      idcurso = Curso.objects.get(id=regcurso.id)

      #=========== registers of competences =================
      for com in compe:
          idcom = Competencias.objects.get(id=com)
          regcom = CompetenciaCurso(idcompetencia=idcom, idcurso=idcurso)
          regcom.save()
      #======= here register of objectives of course ==========
      for description in descripciones:
            regobject = ObjetivosCurso(descrip=description, competencias="", idcurso=idcurso)
            regobject.save()

      #==================here save the session of course =================
      contador=1
      for fecha_inicio, fecha_final, lugar in zip(fechas_inicio, fechas_final, lugares):
            #obtener las variables
            tema = request.POST.get(f'tematicaInput_{contador}')
            destema = request.POST.get(f'desInput_{contador}')
            recur = request.POST.get(f'recur_{contador}')
            archivo = request.FILES.get(f'archivo_{contador}')
            #guardar la sesion
            regsesion = Sesioncurso(fechainicio=fecha_inicio, fechafin=fecha_final, lugar=lugar, estado=1, idcurso=regcurso)
            regsesion.save()
            #=========guarda el archivo
            if archivo:
                nombre_archivo = archivo.name
                ruta_destino = f"archivos/{nombre_archivo}"
                ruta_guardada = default_storage.save(ruta_destino, archivo)
                ruta_destino = settings.MEDIA_URL + ruta_guardada
            else:
                ruta_destino = None
            #========guarda los temas
            regtema = TemasSesion(descrip=tema, competencias=destema, recursos=recur, ruta=ruta_destino, idsesion=regsesion)
            regtema.save()
      #========= send messaje and return the view of courses =================
      if request.POST.getlist('grupo'):
            gruposn = request.POST.getlist('grupo','')
            if gruposn and any(gruposn):  
               for gr in gruposn:
                  grupo_objeto = Grupos.objects.get(id=gr)
                  grupo_cur = GruposCursos(idgrupo=grupo_objeto, idcurso=idcurso) #======= guardar el curso a un grupo seleccionado
                  grupo_cur.save() 
      mensaje = "Curso registrado exitosamente"
      idcom = 1
      context = {
          'usu':perfil_usuario, 
          'msj':mensaje,
          'competencias':comp, 
          'idcom':idcom, 
          'formadores':formadores,
          'grupos':grupos,
          'roles':rol,
          'empresa':empresa,
          'sectores': sectores,
          'tamanios': tamanios
      }
  else:
      context = {
          'usu':perfil_usuario,
          'competencias':comp,
          'formadores':formadores, 
          'grupos':grupos,
          'roles':rol,
          'empresa':empresa,
          'sectores': sectores,
          'tamanios': tamanios
      }
  return render(request, 'admin/addcurso.html', context)

#Rergistro de Empresas
@login_required
def registroEmpresa(request):
    grupoEmpresarial = GrupoEmpresa.objects.all() # llama a los grupos empresariales 
    grupem = Empresa.objects.all()
    sec = SectorEmpresa.objects.all()
    varible = TamEmpresa.objects.all()
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    if request.method == 'POST':
        #=== Get data lists =======
        print('datos empresa', request.POST)
        grupoEm = request.POST.get('grupoEm', '') #== llega el select de grupo empresarial
        #Guardar Empresa Sucursal
        nameSuc = request.POST.getlist('nameSucursal[]')
        nitSuc = request.POST.getlist('nameNit[]')
        dirSuc = request.POST.getlist('nameDireccion[]')
        correoSuc = request.POST.getlist('nameCorreo[]')
        telSuc = request.POST.getlist('nameTelefono[]')
        secSuc = request.POST.getlist('nameSector[]')
        tamSuc = request.POST.getlist('nameTamanio[]')
        tmint = list(map(int, tamSuc))
        scint = list(map(int,secSuc))
        tmp = TamEmpresa.objects.filter(pk__in=tmint)
        sc = SectorEmpresa.objects.filter(pk__in=scint)

        if not grupoEm: #== si no existe significa que no existe un grupo empresarial
            idempresa = None
        else: 
            idempresa = GrupoEmpresa.objects.get(id=grupoEm)
        #================== registro de la sucursal ==================
        if any(nameSuc) or any(nitSuc) or any(dirSuc) or any(correoSuc) or any(telSuc) or any(secSuc) or any(tamSuc):
            empresas_sucursales = []
            for i in range(len(nameSuc)):
                empresa_sucursal = Empresa(
                    nombre=nameSuc[i],
                    nit=nitSuc[i],
                    direccion=dirSuc[i],
                    correo=correoSuc[i],
                    telefono=telSuc[i],
                    idsector=sc[i],
                    idtam=tmp[i],
                    idgrupoem=idempresa
                )
                empresas_sucursales.append(empresa_sucursal)
            Empresa.objects.bulk_create(empresas_sucursales)
            mensaje = f"Datos de la empresa registrados de manera exitosa."
        return render(request, 'admin/addempresa.html', {'usu':perfil_usuario, 'tamempresa':varible, 'secEmp':sec, 'grp':grupem, 'mensaje':mensaje})
    else:
        return render(request, 'admin/addempresa.html', {'usu':perfil_usuario, 'tamempresa':varible, 'secEmp':sec, 'grp':grupem, 'grupoEmpresarial': grupoEmpresarial})

#================== registro de empresa a traves de jquery =======
def createEmpresa(request):
    if request.method == 'POST':
        try:
            entidad = request.POST['entidad']
            nit= request.POST['nit']
            email = request.POST['email']
            tel = request.POST['tel']
            dir = request.POST['dir']
            sector =  request.POST.get('sector', '')
            tam =  request.POST.get('tam', '')
            #=== buscar los datos de sector y tam para save
            tmp = TamEmpresa.objects.get(id=tam)
            sc = SectorEmpresa.objects.get(id=sector)
            empresa = Empresa(nombre=entidad, nit=nit, direccion=dir, correo=email, telefono=tel, idsector=sc, idtam=tmp)
            empresa.save()
            return JsonResponse({'mensaje': 'Empresa registrada de manera exitosa.', 'id':empresa.id, 'nombre':empresa.nombre})
        except Exception as e:
            return JsonResponse({'mensaje': 'Ocurrió un error al crear la empresa.'})
#Fin Guardar Empresa Sucursal
#===================== funcion para crear el grupo empresarial =================
@login_required 
def grupoempresa(request):
    if request.method == 'POST':
        #Guardar empresa principal
        nombre = request.POST['nameEmp']
        nit = request.POST['nit']
        direction = request.POST['direccion']
        email = request.POST['correo']
        phone = request.POST['telefono']
        #======== registrar la empresa ============
        buscar = GrupoEmpresa.objects.filter(nombre=nombre) | GrupoEmpresa.objects.filter(nit=nit)
        if buscar.exists():
            mensaje_grupo = f"Ya existe una empresa con el mismo nombre:  {nombre} o NIT: {nit}."
        else:
            regEmpresa = GrupoEmpresa(nombre=nombre, nit=nit, direccion=direction, correo=email, telefono=phone)
            regEmpresa.save()
            mensaje_grupo = f"Grupo empresarial: {nombre} registrado exitosamente."
        #==============mensajes =============
        messages.error(request, mensaje_grupo)
        return HttpResponseRedirect(reverse('registroEmpresa'))
        #Fin guardar empresa principal
#=======================================================================
@login_required
def deleteGrupEmpresa(request, idgrup):
    try:
        buscar = GrupoEmpresa.objects.get(id=idgrup)
        buscar.delete()
        mensaje_delete_em = f"Grupo empresarial: {buscar.nombre}, eliminado con éxito."
    except GrupoEmpresa.DoesNotExist:
        mensaje_delete_em = f"Error: Información no encontrada."
    messages.error(request, mensaje_delete_em)
    return HttpResponseRedirect(reverse('registroEmpresa'))
    
#Vista para listar cursos
@login_required #proteger la ruta
def listarcursos(request):
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  if request.method == 'GET':
       #============= aqui verificar el rol que tiene =====================
       if perfil_usuario.idrol.id == 4:
          empselect = FormadorEmpresa.objects.get(idusu=perfil_usuario.id, estado=True) 
          cursos = Curso.objects.filter(idusu=perfil_usuario, idempresa=empselect.idempresa).order_by('-id') 
       elif perfil_usuario.idrol.id == 5: #=== filtrar unicamente los cursos pertenecientes a la empresa
          idemp = perfil_usuario.idempresa.id
          cursos = Curso.objects.filter(idempresa=idemp).order_by('-id') 
       elif perfil_usuario.idrol.id == 3:
          idempresa = perfil_usuario.idarea.idempresa.id #=== empresa del usuario jefe
          cursos = Curso.objects.filter(idempresa=idempresa).order_by('-id')
       else:  
          cursos = Curso.objects.all().order_by('-id')
       #=============== fin validacion ===================================
       sesiones = Sesioncurso.objects.all()
       objetivos = ObjetivosCurso.objects.all()
       tematicas = TemasSesion.objects.all()
       compe = CompetenciaCurso.objects.all()
       return render(request, 'admin/listcursos.html', {'usu':perfil_usuario, 'cursos':cursos, 'sesiones':sesiones, 'objetivos':objetivos, 'tematicas':tematicas, 'compes':compe})
  
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
    tematicas = TemasSesion.objects.all()
    formadores = UserPerfil.objects.filter(idrol=4)
    grupos = Grupos.objects.all()
    empresa = Empresa.objects.all()
    rol = RolUser.objects.all()
    sectores = SectorEmpresa.objects.all()
    tamanios = TamEmpresa.objects.all()
    #======= validar la empresa y los grupos ==========
    if perfil_usuario.idrol.id == 5:
       idem = perfil_usuario.idempresa.id
       empresa = Empresa.objects.filter(id=idem)
       grupos = Grupos.objects.filter(idempresa=idem)
       rol = RolUser.objects.filter(id=4)
    #=================================================
    if request.method == 'POST':
        #=== tomar las variables de empresa y formador ==========
        formador_select = request.POST.get('formador', '')
        empresa_select = request.POST.get('empresa', '')
        precio = 0
        id_formador = None
        id_empresa = None
        #===================================================
        curso.nombre = request.POST.get('nombre')
        curso.descrip = request.POST.get('descrip')
        curso.precio = precio
        #============ guardar los grupos actualizados ==========
        if request.POST.getlist('grupo'):
            delgcurso = GruposCursos.objects.filter(idcurso=curso.id)#==borra los datos para hacer la vinculacion
            delgcurso.delete()
            #=============
            gruposn = request.POST.getlist('grupo')
            for gr in gruposn:
                grupo_objeto = Grupos.objects.get(id=gr)
                grupo_cur = GruposCursos(idgrupo=grupo_objeto, idcurso=curso) #======= guardar el curso a un grupo seleccionado
                grupo_cur.save() 
        #=======================================================
        if perfil_usuario.idrol.id == 4: 
            #buscar a que empresa y el formador para guardarlo en la tabla
            idformador = FormadorEmpresa.objects.get(idusu=perfil_usuario, estado=True)
            id_formador = idformador.idusu
            id_empresa = idformador.idempresa
        else:
            if formador_select and empresa_select:
                perfil_formador = UserPerfil.objects.get(id=formador_select)
                empresa_sel = Empresa.objects.get(id=empresa_select)   
                #==== vincular el formador con la empresa ==========
                if not FormadorEmpresa.objects.filter(idempresa=empresa_sel, idusu=perfil_formador).exists():
                   saveFormador = FormadorEmpresa(idempresa=empresa_sel, idusu=perfil_formador)
                   saveFormador.save()
                #===================================
                id_formador = perfil_formador
                id_empresa = empresa_sel 
        #=========== actualizar el formador =============
        curso.idempresa = id_empresa
        curso.idusu = id_formador
        curso.save()
     
        for objetivo in objetivos:
            # Obtener los valores actualizados del formulario
            descripobj = request.POST.get(f'descripobj_{objetivo.id}')
            # Aplicar los cambios a la sesión actual
            objetivo.descrip = descripobj
            objetivo.save()
        #Recibe los objetivos en caso de que existan
        #======= guardar los nuevos objetivos =========
        if 'desobj[]' in request.POST in request.POST:
            descripcionesob = request.POST.getlist('desobj[]')
            for descripob in descripcionesob:
                regnewobj = ObjetivosCurso(descrip=descripob, idcurso=curso)
                regnewobj.save()
        #=========================================================
        for sesion in sesiones:
            # Obtener los valores actualizados del formulario
            nueva_fecha_inicio = request.POST.get(f'fechainicio_{sesion.id}')
            nueva_fecha_fin = request.POST.get(f'fechafin_{sesion.id}')
            nuevo_lugar = request.POST.get(f'lugar_{sesion.id}')

            #obtener variables por cada tema
            idtem = request.POST.get(f'idtema_{ sesion.id }')
            tema = request.POST.get(f'tema_{ sesion.id }')
            temades = request.POST.get(f'temades_{ sesion.id }')
            recursos = request.POST.get(f'recursos_{ sesion.id }')
            archivo = request.FILES.get(f'temarec_{ sesion.id }')
           
            # Aplicar los cambios a la sesión actual
            sesion.fechainicio = nueva_fecha_inicio
            sesion.fechafin = nueva_fecha_fin
            sesion.lugar = nuevo_lugar
            sesion.save()

            #actualizar los temas 
            temasesion = TemasSesion.objects.get(id=idtem)
            temasesion.descrip = tema
            temasesion.competencias = temades
            temasesion.recursos  = recursos
            if archivo:
                nombre_archivo_old = archivo.name
                ruta_destino_old = f"archivos/{nombre_archivo_old}"
                ruta_guardada_old = default_storage.save(ruta_destino_old, archivo)
                ruta_destino_old = settings.MEDIA_URL + ruta_guardada_old
                temasesion.ruta = ruta_destino_old
            temasesion.save()
        #================ guardar las nuevas sesiones ==================================
        contador=1
        if 'fecha_inicio[]' in request.POST and 'fecha_final[]' in request.POST and 'lugar[]' in request.POST:
            fechas_inicio_new = request.POST.getlist('fecha_inicio[]')
            fechas_final_new = request.POST.getlist('fecha_final[]')
            lugares_new = request.POST.getlist('lugar[]')
            for fecha_inicio_new, fecha_final_new, lugar_new in zip(fechas_inicio_new, fechas_final_new, lugares_new):
                #obtener las variables
                tema_new = request.POST.get(f'tematicaInput_{contador}')
                destema_new = request.POST.get(f'desInput_{contador}')
                recur_new = request.POST.get(f'recur_{contador}')
                archivo_new = request.FILES.get(f'archivo_{contador}')
                #guardar la sesion
                regsesionnew = Sesioncurso(fechainicio=fecha_inicio_new, fechafin=fecha_final_new, lugar=lugar_new, estado=1, idcurso=curso)
                regsesionnew.save()
                #=========guarda el archivo
                if archivo_new:
                    nombre_archivo = archivo_new.name
                    ruta_destino = f"archivos/{nombre_archivo}"
                    ruta_guardada = default_storage.save(ruta_destino, archivo_new)
                    ruta_destino_new = settings.MEDIA_URL + ruta_guardada
                else:
                    ruta_destino_new = None
                #========guarda los temas
                regtema_new = TemasSesion(descrip=tema_new, competencias=destema_new, recursos=recur_new, ruta=ruta_destino_new, idsesion=regsesionnew)
                regtema_new.save()
                contador = contador+1
        #========================= aqui finaliza las nuevas sesiones =========================
        messages.success(request, 'Curso actualizado exitosamente.')
        return redirect('listarcursos')
    else:
        datos = {'usu':perfil_usuario, 'curso': curso, 'sesiones': sesiones, 'objetivos': objetivos, 'temas':tematicas, 'formadores':formadores, 'grupos':grupos, 'empresa':empresa, 'roles':rol,'sectores':sectores, 'tamanios':tamanios}
        return render(request, 'admin/updatecurso.html', datos)
     
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
            idarea = request.POST.get('area')
            iddepartamento = request.POST.get('depar', '')
            #=========== validar si es nulo para aplicar a toda el area ===============
            id_area = get_object_or_404(Area, id=idarea)
           
            if not iddepartamento:
                # ========= guardar la info en la tabla de kpis area =========
                regkpi = Kpiarea(nombre=request.POST['nombre'], descrip=request.POST['descrip'], fechaini=request.POST['fechaini'], fechafin=request.POST['fechafin'], valor=request.POST['valor'], idarea=id_area, idepar=None)
                regkpi.save()
            else:
                id_depar = get_object_or_404(Departamento, id=iddepartamento)
                regkpi = Kpiarea(nombre=request.POST['nombre'], descrip=request.POST['descrip'], fechaini=request.POST['fechaini'], fechafin=request.POST['fechafin'], valor=request.POST['valor'], idarea=None, idepar=id_depar)
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
    
    if perfil_usuario.idrol.id == 5: 
       idemp=perfil_usuario.idempresa.id
       empresas = Empresa.objects.filter(id=idemp)
       area = Area.objects.filter(idempresa=idemp)
    #=========== usuario jefe =========
    elif perfil_usuario.idrol.id == 3: 
       idempresa = perfil_usuario.idarea.idempresa.id #=== empresa del usuario jefe
       empresas = Empresa.objects.filter(id=idempresa)
       area = Area.objects.filter(idempresa=idempresa)
       print('atreas', area)
    else:
       empresas = Empresa.objects.all()
       area = Area.objects.all()
    depart = Departamento.objects.all()
    #================= obtner las fechas actuales ================
    fecha_actual_utc = timezone.now()
    fecha_actual_local = timezone.localtime(fecha_actual_utc)
   
    return render(request, 'admin/kpiareasdep.html', {'usu': perfil_usuario, 'area': area, 'depart': depart, 'fecha':fecha_actual_local, 'empresas':empresas})

#listar KPIs de cada area
@login_required
def listarkpiarea(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    kpobj = Kpiobjetivos.objects.all()
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        kparea = Kpiarea.objects.filter(Q(idarea__idempresa=idempresa) | Q(idepar__idarea__idempresa=idempresa))
    elif perfil_usuario.idrol.id == 3:
        idempresa = perfil_usuario.idarea.idempresa #=== empresa del usuario jefe
        kparea = Kpiarea.objects.filter(Q(idarea__idempresa=idempresa) | Q(idepar__idarea__idempresa=idempresa)) 
    else:
        kparea = Kpiarea.objects.all()
    return render(request, 'admin/listkpi.html', {'usu': perfil_usuario, 'kpareas':kparea, 'kpobjs':kpobj})

#editar kpi de cada area
@login_required
def editarkpi(request, idkpi):
    mensajeUpdate = ''
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    datoskpi = Kpiarea.objects.get(id=idkpi)
    objetivos = Kpiobjetivos.objects.filter(idkpi=datoskpi)
    fecha_actual_utc = timezone.now()
    fecha_actual_local = timezone.localtime(fecha_actual_utc)
    if request.method == 'POST':
        #=======validar el id de la empresa ==================
        #idem = perfil_usuario.idepart  # aquí se obtiene la empresa a la cual pertenece
        id_area = request.POST.get('area', '')
        iddepartamento = request.POST.get('depar', '')
        if not id_area and not iddepartamento:
             mensajeAlerta = 'Debe existir al menos una Area o Departamento seleccionados.'
             messages.error(request, mensajeAlerta)
             return HttpResponseRedirect(reverse('editarkpi', kwargs={'idkpi': idkpi}))
        #=========== recupera los datos del front ================
        datoskpi.nombre = request.POST.get('nombre')
        datoskpi.descrip = request.POST.get('descrip')
        datoskpi.fechaini = request.POST.get('fecini')
        datoskpi.fechafin = request.POST.get('fecfin')
        datoskpi.valor = request.POST.get('valor')
       
        if not iddepartamento:
            # ========= guardar la info en la tabla de kpis area =========
            idarea = get_object_or_404(Area, id=id_area)
            datoskpi.idarea = idarea
            datoskpi.idepar=None
        else:
            id_depar = Departamento.objects.get(id=iddepartamento)
            datoskpi.idarea = None
            datoskpi.idepar=id_depar
        datoskpi.save()
        #====================================================
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
        mensajeUpdate = 'Kpi actualizado de manera exitosa.'
    #=======consultas para la vista =========================
    infokpi = Kpiarea.objects.get(id=idkpi)
    obkpi = Kpiobjetivos.objects.filter(idkpi=idkpi)
    if not infokpi.idarea:
        emprincipal = Empresa.objects.get(id=infokpi.idepar.idarea.idempresa.id)
    else:
        emprincipal = Empresa.objects.get(id=infokpi.idarea.idempresa.id) 
    #========== validar los valores ==========
    if perfil_usuario.idrol.id == 3:
        idempresa = perfil_usuario.idarea.idempresa.id #=== empresa del usuario jefe
        empresa = Empresa.objects.filter(id=idempresa)
    #========= usuario administrador gerente==========
    elif perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id #=== empresa del usuario jefe
        empresa = Empresa.objects.filter(id=idempresa)
    else:
        empresa = Empresa.objects.all()
    
    return render(request, 'admin/updatekpi.html', {'usu': perfil_usuario, 'infokpis':infokpi, 'obkpis':obkpi, 'empresa':empresa, 'principal':emprincipal, 'mensajeUp':mensajeUpdate, 'fecha':fecha_actual_local})

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

#========== desactivar o activar el KPI =============
@login_required
def desactivarkpi(request, idkpi):
    try:
        kpi = Kpiarea.objects.get(id=idkpi)
        if kpi.estado:
           kpi.estado = False
        else:
            kpi.estado = True
        kpi.save()
        messages.success(request, 'El estado del KPI ha sido actualizado.')
    except Kpiarea.DoesNotExist:
        messages.error(request, 'Existe un error con el KPI seleccionado.')
    return redirect('listarkpiarea')

#================= consultar empresa seleccionada ======
@login_required
def selectEmpresa(request):
    idempresa = request.GET.get('opcion')
    #========= buscar la empresa ==========
    empresa = Empresa.objects.get(id=idempresa)
    data = list(Area.objects.filter(idempresa=empresa).values('id', 'nombre', 'descrip'))
    return JsonResponse({'areas': data})
   
#=============== consultar el area seleccionada ====================
@login_required
def selectArea(request):
    idarea = request.GET.get('opcion')
    area = Area.objects.get(id=idarea)
    data = list(Departamento.objects.filter(idarea=area).values('id', 'nombre', 'descrip'))
    return JsonResponse({'data': data})


#Vista para listar Empresas
@login_required
def listarempresa(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    if perfil_usuario.idrol.id == 5:
       idempresa = perfil_usuario.idempresa.id 
       emp = Empresa.objects.filter(id=idempresa)
    else:
       emp = Empresa.objects.all()
    #=================================
    sec = SectorEmpresa.objects.all()
    grpemp = GrupoEmpresa.objects.all()
    tam = TamEmpresa.objects.all()
    return render(request, 'admin/listempresas.html', {'usu':perfil_usuario,'emp':emp, 'grpemp':grpemp, 'sec':sec, 'tam':tam})

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
    grpEmp = GrupoEmpresa.objects.all()
    sector = SectorEmpresa.objects.all()
    tamint = TamEmpresa.objects.all()
    empresabus = Empresa.objects.get(id=idempresa)
    if request.method == 'POST':
        empresa = Empresa.objects.get(id=idempresa)
        empresa.nombre = request.POST.get('nameEmp')
        empresa.nit = request.POST.get('nit')
        empresa.direccion = request.POST.get('direccion')
        empresa.correo = request.POST.get('correo')
        empresa.telefono = request.POST.get('telefono')
        gropemp = request.POST.get('groupEmp', '')
        sec = request.POST.get('sector')
        tam = request.POST.get('tamanioEmp')

        #=========== validar que el grupo empresa no este vacio =======
        if not gropemp:
            grupo = None
        else:
            grupo = GrupoEmpresa.objects.get(id=gropemp)

        empresa.idgrupoem = grupo # === se asigna en blanco si no hay datos
        empresa.idsector = SectorEmpresa.objects.get(id=sec)
        empresa.idtam = TamEmpresa.objects.get(id=tam)
        empresa.save()
        messages.success(request, 'Empresa actualizada exitosamente.')
        return redirect('listarempresa')
    else:
        return render(request, 'admin/updateempresa.html', {'usu':perfil_usuario, 'empresa':empresabus, 'sector':sector, 'grpEmp':grpEmp, 'tamint':tamint})

#Codigo Jhon
class empresagetsector(View):
    def get(self, request, *args, **kwargs):
        data=list(SectorEmpresa.objects.values())
        return JsonResponse(data, safe=False)
#Fin codigo Jhon

#descargar archivos
@login_required #proteger la ruta
def download(request, ruta):
    file_path = ruta
    file_path = './static/archivos' + file_path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'  # Default to binary if type can't be determined

            response = HttpResponse(file.read(), content_type=content_type)
            file_name = os.path.basename(file_path)
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
      return HttpResponse("File not found", status=404)
    
#======== listado grupos de formación ====================
@login_required #proteger la ruta
def listGrupos(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    if perfil_usuario.idrol.id == 5: #=== debe filtrar los grupos de la empresa que pertenece el gerente
       idempresa = perfil_usuario.idempresa.id
       grupos_cursos = GruposCursos.objects.filter(idgrupo__idempresa=idempresa).select_related('idgrupo', 'idcurso')
       grupousers = GruposUser.objects.filter(idgrupo__idempresa=idempresa).select_related('idgrupo', 'iduser') #====
       empresa = Empresa.objects.filter(id=idempresa)
    else:
       grupos_cursos = GruposCursos.objects.select_related('idgrupo', 'idcurso')
       grupousers = GruposUser.objects.select_related('idgrupo', 'iduser')
       empresa = Empresa.objects.all()
    #=========== contar los usuarios que pertenecen a este grupo =============
    grupos_con_cursos = {}
    grupos_des = []
    grupouserold = []
    for grupo_curso in grupos_cursos:
        id_grupos_cursos = grupo_curso.id
        id_grupo = grupo_curso.idgrupo.id
        nombre_grupo = grupo_curso.idgrupo.nombre
        descrip_grupo = grupo_curso.idgrupo.descrip
        nombre_curso = grupo_curso.idcurso.nombre
        descrip_curso = grupo_curso.idcurso.descrip
        # contar el numero de usuarios por cada grupo 
        num_usuarios = GruposUser.objects.filter(idgrupo=grupo_curso.idgrupo).count()
        # Verificar si el grupo ya ha sido agregado a la lista
        if not any(grupo['id'] == grupo_curso.idgrupo.id for grupo in grupos_des):
            grupos_des.append({'id': id_grupo, 'nombre':nombre_grupo, 'descrip': descrip_grupo, 'total':num_usuarios}) 

        if nombre_grupo not in grupos_con_cursos:
            grupos_con_cursos[nombre_grupo] = []
               
        grupos_con_cursos[nombre_grupo].append((id_grupos_cursos, nombre_curso, descrip_curso))
     #================================= Aqui buscar los grupos que estan en la tabla gruposuser =================
    for gusers in grupousers:
        id_grupo = gusers.idgrupo.id
        nombre_grupo = gusers.idgrupo.nombre
        descrip_grupo = gusers.idgrupo.descrip
        # contar el numero de usuarios por cada grupo 
        num_usuarios = GruposUser.objects.filter(idgrupo=gusers.idgrupo).count()
        # Verificar si el grupo ya ha sido agregado a la lista
        if not any(grupo['id'] == gusers.idgrupo.id for grupo in grupouserold):
            grupouserold.append({'id': id_grupo, 'nombre':nombre_grupo, 'descrip': descrip_grupo, 'total':num_usuarios}) 
    #=========== obtener los datos faltantes =============
    datos_faltantes = [dato for dato in grupouserold if dato not in grupos_des]
    #=================================================================================================
    return render(request, 'admin/listgrupo.html', {'usu':perfil_usuario, 'grupos_con_cursos':grupos_con_cursos, 'grupos_des':grupos_des, 'datos_faltantes':datos_faltantes, 'empresa':empresa})

#=============== formulario de crear nuevo grupo con cursos y trabajadores =================
@login_required #proteger la ruta
def creargrupo(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    ngrupos = Grupos.objects.all()
    addgrupouser = GruposUser.objects.all()
    addgrupocurso = GruposCursos.objects.all()
    cursos = Curso.objects.all()
    usuarios = UserPerfil.objects.all()
    empresa = Empresa.objects.all()
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        empresa = Empresa.objects.filter(id=idempresa)
        usuarios = UserPerfil.objects.filter(Q(idarea__idempresa=idempresa) | Q(idepart__idarea__idempresa=idempresa))
        cursos = Curso.objects.filter(idempresa=idempresa)

    if request.method == 'POST':
        ngrupo = request.POST.get('ngrupo')
        cursos_seleccionados = request.POST.getlist('cursosselec')
        usuarios_seleccionados = request.POST.getlist('ususelect')
        # Obtén los objetos de Curso y Grupo
        if ngrupo and cursos_seleccionados and usuarios_seleccionados:
            cursos_objetos = Curso.objects.filter(id__in=cursos_seleccionados)
            grupo_objeto = Grupos.objects.get(id=ngrupo)
            user_objetos = UserPerfil.objects.filter(id__in=usuarios_seleccionados)
            # Recorre los cursos seleccionados y guarda la relación en GruposCursos
            for curso_objeto in cursos_objetos:
                if GruposCursos.objects.filter(idgrupo=grupo_objeto, idcurso=curso_objeto).exists():
                    messages.success(request, 'El grupo ya esta agregado.')
                    return redirect('creargrupo')
                #guarda los cursos seleccionados
                grupo_curso = GruposCursos(idgrupo=grupo_objeto, idcurso=curso_objeto)
                grupo_curso.save()
            #aqui se debe guardar los estudiantes con el grupo
            for user_objeto in user_objetos:
                if GruposUser.objects.filter(idgrupo=grupo_objeto, iduser=user_objeto).exists():
                    messages.success(request, 'El usuario ya esta registrado en el mismo grupo.')
                    return redirect('creargrupo')
                #guardar los estudiantes
                grupo_usu = GruposUser(idgrupo=grupo_objeto, iduser=user_objeto)
                grupo_usu.save()  
            #print('datos', request.POST)
            messages.success(request, 'Datos guardados exitosamente.')
        else:
            messages.success(request, 'Por favor, completa todos los campos.')
        return redirect('creargrupo')
    else:
      #============ solamente obtener los grupos que no tienen ningun curso o usuario vinculado =============
        grupos_faltantes = ngrupos.exclude(
            Q(gruposuser__in=addgrupouser) | Q(gruposcursos__in=addgrupocurso)
        )
      #===========obtener los datos para agregar un nuevo usuario ================
        rol = RolUser.objects.all()
        depars = Departamento.objects.all()
        areas =Area.objects.all()
        return render(request, 'admin/addgrupo.html', {'usu':perfil_usuario, 'ngrupos':grupos_faltantes, 'cursos':cursos, 'usuarios':usuarios, 'roles':rol, 'empresa':empresa, 'depars':depars, 'areas':areas})
#================================================
#======== Duplicar grupo con todos sus usuarios y cursos agregados ================
def duplicarGrupo(request, idgr):
    grupo_original = get_object_or_404(Grupos, id=idgr)
    with transaction.atomic():
        # Duplicar el formulario
        grupo_nuevo = Grupos.objects.create(
            nombre=f"{grupo_original.nombre} (Copia)",
            descrip=f"{grupo_original.descrip} (Copia)",
        )
        #Duplicar los cursos
        for cursos_original in GruposCursos.objects.filter(idgrupo=grupo_original):
            curso_nuevo = GruposCursos.objects.create(
                idcurso=cursos_original.idcurso,
                idgrupo=grupo_nuevo,
            )
        #duplicar los usuarios en los grupos
        for usuarios_original in GruposUser.objects.filter(idgrupo=grupo_original):
            usuarios_nuevo = GruposUser.objects.create(
                iduser=usuarios_original.iduser,
                idgrupo=grupo_nuevo,
            )
    return HttpResponseRedirect(reverse('listGrupos'))
#======= Agregar nuevo grupo desde la parte del admin ============
def createUser(nombre, apellido, cedula, tel, id_rol, idepar, idarea, cargo_user, email, passw, idempresa):
       #================ consultas ================
        rol_user = get_object_or_404(RolUser, id=id_rol)
        id_empresa = get_object_or_404(Empresa, id=idempresa)
        #========= crear el usuario ========
        user = User.objects.create_user(username=email, password=passw)
        user.save()
        #========== crear el user perfil==========
        if rol_user.id != 4:
            if not idepar:
                id_area = Area.objects.get(id=idarea)
                id_depar = None
            else: 
                id_depar = Departamento.objects.get(id=idepar)
                id_area = None
            userper = UserPerfil(nombre=nombre, apellido=apellido, cedula=cedula, telefono=tel, idrol=rol_user, cargo=cargo_user, idepart=id_depar, idarea=id_area, user=user )
            userper.save()
        else: 
            userper = UserPerfil(nombre=nombre, apellido=apellido, cedula=cedula, telefono=tel, idrol=rol_user, cargo=cargo_user, idepart=None, idarea=None, user=user )
            userper.save()
            #============ guardar la relacion de empresa y formador
            formador = FormadorEmpresa(idempresa=id_empresa, idusu=userper)
            formador.save()
        return userper
#======================================
@login_required #proteger la ruta
def saveusernuevo(request):
    if request.method == 'POST':
       perfil_usuario = UserPerfil.objects.get(user=request.user)
       ngrupos = Grupos.objects.all()
       addgrupouser = GruposUser.objects.all()
       addgrupocurso = GruposCursos.objects.all()
       cursos = Curso.objects.all()
       rol = RolUser.objects.all()
       empresa = Empresa.objects.all()
       depars = Departamento.objects.all()
       areas =Area.objects.all()
       #============ solamente obtener los grupos que no tienen ningun curso o usuario vinculado =============
       grupos_faltantes = ngrupos.exclude(
            Q(gruposuser__in=addgrupouser) | Q(gruposcursos__in=addgrupocurso)
        )
       #========= guardar en userperfil =================
       id_rol = request.POST['rol']
       cargo_user = request.POST.get('cargo', '')
       idepar = request.POST.get('depar', '')
       idarea = request.POST.get('area', '')
       nombre = request.POST['nombre']
       apellido =request.POST['apellido']
       cedula = request.POST['ced']
       tel = request.POST['tel']
       email = request.POST['email']
       passw = request.POST['pass']
       idempresa = request.POST.get('emp', '')
       #================ consultas ================
       createUser(nombre, apellido, cedula, tel, id_rol, idepar, idarea, cargo_user, email, passw, idempresa)
       usuarios = UserPerfil.objects.all()
       #================ buscar el id de la empresa ===================
       mensaje = "Usuario guardado de manera exitosa."
       messages.info(request, mensaje)
       return render(request, 'admin/addgrupo.html', {'usu':perfil_usuario, 'ngrupos':grupos_faltantes, 'cursos':cursos, 'usuarios':usuarios, 'rol':rol, 'empresa':empresa, 'depars':depars, 'areas':areas})
#================================================
@login_required
def addusernuevo(request):
    id_rol = request.POST['rol']
    cargo_user = request.POST.get('cargo', '')
    idepar = request.POST.get('depar', '')
    idarea = request.POST.get('area', '')
    nombre = request.POST['nombre']
    apellido =request.POST['apellido']
    cedula = request.POST['ced']
    tel = request.POST['tel']
    email = request.POST['email']
    passw = request.POST['pass']
    idempresa = request.POST.get('emp', '')
    #return JsonResponse({'id_rol':id_rol, 'nombre': nombre, 'apellido': apellido, 'cargo_user': cargo_user, 'idepar': idepar, 'idarea':idarea, 'cedula':cedula, 'tel':tel, 'email':email, 'passw': passw, 'idempresa':idempresa })
    if id_rol == '4':
       user = createUser(nombre, apellido, cedula, tel, id_rol, idepar, idarea, cargo_user, email, passw, idempresa)
       return JsonResponse({'mensaje': 'Formador creado de maera exitosa', 'iduser':user.id, 'nombre':user.nombre, 'apellido': user.apellido}) 
       #return JsonResponse({'id': user.id, 'nombre': user.nombre, 'apellido': user.apellido})
    else:
       return JsonResponse({'mensaje': 'Error al crear el formador'})  
#============= crear grupo ============
@login_required #proteger la ruta
def addgrupo(request):
    if request.method == 'POST': 
        nom = request.POST.get('nombreg')
        des = request.POST.get('descripg')
        emp = request.POST.get('gemp', '')
        if nom != '' and des != '':
           if Grupos.objects.filter(nombre=nom).exists():
              return JsonResponse({'mensaje': 'Ya existe un grupo con ese nombre. Por favor, elige un nombre diferente.'}, status=400) 
           else:
              empresa = Empresa.objects.get(id=emp)
              info = Grupos(nombre=nom, descrip=des, idempresa=empresa)
              info.save()
              return JsonResponse({'id': info.id, 'nombre': info.nombre, 'descrip': info.descrip})
        else:
            return JsonResponse({'mensaje': 'Los campos no pueden estar vacios.'}, status=401) 
#============= Elimanr grupo =========
@login_required #proteger la ruta
def eliminargrupo(request, idgrupo):
    try:
        gr = Grupos.objects.get(id=idgrupo)
        gr.delete()
        messages.success(request, 'Grupo eliminada exitosamente.')
    except Grupos.DoesNotExist:
        messages.error(request, 'El grupo no Existe')
    return redirect('creargrupo')

#================Eliminar grupo de manera definitiva con la vinculacion de usuarios y cursos=============
@login_required #proteger la ruta
def deletegrupos(request, idgrupo):
    try:
        gr = Grupos.objects.get(id=idgrupo)
        gr.delete()
        messages.success(request, 'Grupo eliminada exitosamente.')
    except Grupos.DoesNotExist:
        messages.error(request, 'El grupo no Existe')
    return redirect('listGrupos')
#===============Editar grupo ===============

@login_required #proteger la ruta
def editargrupo(request):
    if request.method == 'POST':
        idgr = request.POST.get('id')
        nom = request.POST.get('nombre')
        des = request.POST.get('descrip')
        try:
            if nom != '' and des != '':
                if Grupos.objects.filter(nombre=nom).exists():
                    return JsonResponse({'mensaje': 'Ya existe un grupo con ese nombre. Por favor, elige un nombre diferente.'}, status=404) 
                else:
                    datosGrupo = Grupos.objects.get(id=idgr)
                    datosGrupo.nombre = nom
                    datosGrupo.descrip = des
                    datosGrupo.save()
                    #========== validar los grupos solamente aparecer los que estan sin vinculos=========
                    addgrupouser = GruposUser.objects.all()
                    addgrupocurso = GruposCursos.objects.all()
                    opciones = list(
                        Grupos.objects.exclude(
                            Q(gruposuser__in=addgrupouser) | Q(gruposcursos__in=addgrupocurso)
                        ).values()
                    )
                    return JsonResponse({'message': 'Datos actualizados correctamente.', 'opciones':opciones})             
            else:
                return JsonResponse({'mensaje': 'Los campos no pueden estar vacios'}, status=404) 
        except Grupos.DoesNotExist:
            return JsonResponse({'mensaje': 'No se encontró el objeto con el ID proporcionado.'}, status=404)

# editar grupo desde la vista de grupos agregados
@login_required #proteger la ruta
def editargrupoagregado(request):
    if request.method == 'POST':
        idgr = request.POST.get('idgrupo')
        nom = request.POST.get('nombre')
        des = request.POST.get('descrip')
        gemp = request.POST.get('gemp','')
        try:
            if nom != '' and des != '':
                if Grupos.objects.filter(nombre=nom).exclude(id=idgr).exists():
                    mensaje = "Ya existe un grupo con ese nombre. Por favor, elige un nombre diferente."
                    messages.error(request, mensaje)
                    url = reverse('listGrupos')
                    return HttpResponseRedirect(url)
                else:
                    empresa = Empresa.objects.get(id=gemp)
                    datosGrupo = Grupos.objects.get(id=idgr)
                    datosGrupo.nombre = nom
                    datosGrupo.descrip = des
                    datosGrupo.idempresa = empresa
                    datosGrupo.save()
                    mensaje = "La información se actualizó de manera exitosa."
                    messages.error(request, mensaje)
                    return HttpResponseRedirect(reverse('listGrupos'))
                    #========== validar los grupos solamente aparecer los que estan sin vinculos=========
            else:
                mensaje = "Los campos no pueden estar vacios."
                messages.error(request, mensaje)
                return HttpResponseRedirect(reverse('listGrupos'))
        except Grupos.DoesNotExist:
            mensaje = "No se encontró el grupo para realizar los cambios."
            messages.error(request, mensaje)
            return HttpResponseRedirect(reverse('listGrupos'))
        
# listar los usuarios pertenecientes a un grupo
@login_required #proteger la ruta
def usersgrupo(request, idgrupo):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    regusu = GruposUser.objects.filter(idgrupo=idgrupo)
    gruponame = Grupos.objects.get(id=idgrupo)
    #==== subconsulta ===
    squery = Subquery(GruposUser.objects.filter(idgrupo=idgrupo).values('iduser'))
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        usuarios = UserPerfil.objects.filter(Q(idarea__idempresa=idempresa) | Q(idepart__idarea__idempresa=idempresa)).exclude(id__in=squery)
    else:
        usuarios = UserPerfil.objects.exclude(id__in=squery).exclude(idrol__in=[1, 4, 5])
    #========== si es metodo post ===============
    if request.method == 'POST':
        usuariosn = request.POST.getlist('userselect')
        usunuevo = request.POST.getlist('nuevosselect')
        #regusun = GruposUser.objects.filter(idgrupo=idgrupo).values('iduser')
        user_objetos = UserPerfil.objects.filter(id__in=usunuevo)
        grupo_objeto = Grupos.objects.get(id=idgrupo)
        # Obtener los ids presentes en la queryset
        ids_faltantes = set(GruposUser.objects.filter(idgrupo=idgrupo).exclude(iduser__in=usuariosn).values_list('iduser', flat=True))
        # Encontrar el id que falta
        if ids_faltantes:
            GruposUser.objects.filter(iduser__in=ids_faltantes).delete()
        #agregar nuevos usuarios al grupo
        for user_objeto in user_objetos:
            grupo_usu = GruposUser(idgrupo=grupo_objeto, iduser=user_objeto)
            grupo_usu.save() 
        messages.error(request, 'Datos actualizados correctamente')
    return render(request, 'admin/listusergrupo.html', {'usu':perfil_usuario, 'regusu':regusu, 'usuarios':usuarios, 'idgrupo':idgrupo, 'gruponame':gruponame})

# aqui se puede actualizar los cursos en cada grupo
@login_required
def cursosgrupo(request, idgrupo):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    regcurso = GruposCursos.objects.filter(idgrupo=idgrupo)
    gruponame = Grupos.objects.get(id=idgrupo)
    squery = Subquery(GruposCursos.objects.filter(idgrupo=idgrupo).values('idcurso')) #=== consulta de subquery
    #============= si el usuario es gerente hacer la validacion=======
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        cursos = Curso.objects.filter(idempresa=idempresa).exclude(id__in=squery)
    else:
        cursos = Curso.objects.exclude(id__in=squery)
    #=========== guardar los siguientes resultados ====================
    if request.method == 'POST':
        cursoold = request.POST.getlist('cursoselect')
        cursonew = request.POST.getlist('cursonew')
        curreg = GruposCursos.objects.filter(idgrupo=idgrupo).values('id')
        cursos_objetos = Curso.objects.filter(id__in=cursonew)
        grupo_objeto = Grupos.objects.get(id=idgrupo)
        #convertir el query
        ids_query = {curso['id'] for curso in curreg}
        # Encontrar el id que falta
        ids_faltantes = [id for id in ids_query if str(id) not in cursoold]
        for id_faltante in ids_faltantes:
            getid = get_object_or_404(GruposCursos, id=id_faltante)
            getid.delete()
        #agregar los nuevos cursos seleccionados
        for curso_objeto in cursos_objetos:
            grupo_cur = GruposCursos(idgrupo=grupo_objeto, idcurso=curso_objeto)
            grupo_cur.save() 
        messages.error(request, 'Datos actualizados correctamente')
    return render(request, 'admin/listcursogrupo.html', {'usu':perfil_usuario, 'idgrupo':idgrupo, 'regcurso':regcurso, 'cursos':cursos,  'gruponame':gruponame })
    

@login_required
def visualizarAreaDepto(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    #========= si el usuario es administrador(gerente) ===========
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        empresa = Empresa.objects.filter(id=idempresa)
    else:
       empresa = Empresa.objects.all()
    #===============================
    areas = ''
    if request.method == 'POST':
        selecarea = request.POST.get('selectEmp')
        # ===========  buscar todas las areas ligadas a la empresa seleccionada ========
        #========= empresa seleccionada ======
        empr = Empresa.objects.get(id=selecarea)
        areas = Area.objects.filter(idempresa=empr)
        #========= departamentos ==============
        depar = Departamento.objects.all()
        return render(request, 'admin/listvinculacion.html',{'usu':perfil_usuario, 'empresa':empresa, 'areas':areas, 'selecarea':selecarea, 'emp':empr, 'depar':depar})
    else:
        return render(request, 'admin/listvinculacion.html',{'usu':perfil_usuario, 'empresa':empresa})
#================ crear una nueva area =========
@login_required
def addArea(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    #========= si el usuario es administrador(gerente) ===========
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        empresa = Empresa.objects.filter(id=idempresa)
    else:
       empresa = Empresa.objects.all()
    #===============================
    if request.method == 'POST':
        # Recibe los datos del formulario
        activarPanel = 1 #===== acti var el popup una vez guardado
        area_nueva = request.POST.get('nomarea')
        descripcion = request.POST.get('desareanueva', '')
        empresa_select = request.POST.get('empresa')
        #=========== craer el area ============
        empr = Empresa.objects.get(id=empresa_select)
        depar = Departamento.objects.all()
        areas = Area.objects.filter(idempresa=empr)
        #========= validar ====
        existing_area = Area.objects.filter(nombre=area_nueva, idempresa=empr).first()
        if not existing_area:
           newarea = Area(nombre=area_nueva, descrip=descripcion, idempresa=empr)
           newarea.save() 
        return render(request, 'admin/listvinculacion.html',{'usu':perfil_usuario, 'empresa':empresa, 'areas':areas, 'activarPanel':activarPanel, 'selecarea':empresa_select, 'emp':empr, 'depar':depar})

#===================== crear nuevo departamento =======
@login_required
def addDepartamento(request):
     perfil_usuario = UserPerfil.objects.get(user=request.user)
     #========= si el usuario es administrador(gerente) ===========
     if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        empresa = Empresa.objects.filter(id=idempresa)
     else:
        empresa = Empresa.objects.all()
    #===============================
     if request.method == 'POST':
         area = request.POST.get('area')
         depar = request.POST.get('departamento', '')
         descrip = request.POST.get('descripdep', '')
         areaob = Area.objects.filter(id=area).first()
         emp_select = areaob.idempresa.id #empresa elegida
         empr = Empresa.objects.get(id=emp_select)
         areas = Area.objects.filter(idempresa=empr)
         existing_dep = Departamento.objects.filter(nombre=depar, idarea=areaob).first()
         if not existing_dep:
             newdepar = Departamento(nombre=depar, descrip=descrip, idarea=areaob)
             newdepar.save()
         deparcom = Departamento.objects.all()
         return render(request, 'admin/listvinculacion.html',{'usu':perfil_usuario, 'empresa':empresa, 'areas':areas,  'selecarea':emp_select, 'emp':empr, 'depar':deparcom})

#================ eliminar departamento =========
@login_required
def deleteDepar(request, iddepar, area):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    areaob = Area.objects.filter(id=area).first()
    emp_select = areaob.idempresa.id #empresa elegida
    empr = Empresa.objects.get(id=emp_select)
    areas = Area.objects.filter(idempresa=empr)
    deparcom = Departamento.objects.all()
    #========= si el usuario es administrador(gerente) ===========
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        empresa = Empresa.objects.filter(id=idempresa)
    else:
       empresa = Empresa.objects.all()
    #=========================================
    try:
        emp = Departamento.objects.get(id=iddepar)
        emp.delete()
        messages.success(request, 'Departamento eliminado exitosamente.')
    except Departamento.DoesNotExist:
        messages.error(request, 'El departamento no existe Existe')
    return render(request, 'admin/listvinculacion.html',{'usu':perfil_usuario, 'empresa':empresa, 'areas':areas,  'selecarea':emp_select, 'emp':empr, 'depar':deparcom})

@login_required
def eliminavinculo(request, idarea):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    areaob = Area.objects.filter(id=idarea).first()
    empr, emp_select = '', ''
    if areaob:
       emp_select = areaob.idempresa.id #empresa elegida
       empr = Empresa.objects.get(id=emp_select)
       areas = Area.objects.filter(idempresa=empr)
    deparcom = Departamento.objects.all()
    #========= si el usuario es administrador(gerente) ===========
    if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        emp_select = idempresa
        empresa = Empresa.objects.filter(id=idempresa)
        empr = Empresa.objects.get(id=idempresa)
        areas = Area.objects.filter(idempresa=empr)
    else:
        empresa = Empresa.objects.all()
    #===============================
    try:
        emp = Area.objects.get(id=idarea)
        emp.delete()
        messages.success(request, 'Area eliminada exitosamente.')
    except Area.DoesNotExist:
        messages.error(request, 'El area no Existe')
    areas = Area.objects.filter(idempresa=empr)
    return render(request, 'admin/listvinculacion.html',{'usu':perfil_usuario, 'empresa':empresa, 'areas':areas,  'selecarea':emp_select, 'emp':empr, 'depar':deparcom})
    

def validarasistencia(request, idsesion):
    
    if request.method == 'POST':
            verificar = True
            mensaje = ''

            texto = request.POST.get("inputUser").lower() #==convertir el texto siempre a minusculas
            if User.objects.filter(username=texto).exists():
                usuario = User.objects.get(username=texto)
                user = UserPerfil.objects.get(user=usuario)
   
            else:
                mensaje = f"El usuario {texto} no se encuentra registrado en el sistema, lo invito a inscribirse"
                return render(request, 'admin/validarasistencia.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':True})
           
            if Sesioncurso.objects.filter(id=idsesion).exists():
                sesion = Sesioncurso.objects.get(id=idsesion)
                totals = Sesioncurso.objects.filter(idcurso=sesion.idcurso).order_by('fechainicio')
                numero_sesion = 1 #== inicializar var y obtener el numero de la sesion correspondiente
                for idx, s in enumerate(totals, start=1):
                    if s.id == idsesion:
                        numero_sesion = idx
                        break
                
                if SesionAsistencia.objects.filter(idsesioncurso=sesion, idusuario=user).exists():
                    mensaje= f'El usuario: {texto}, ya se encuentra registrado a esta sesión: {numero_sesion} del curso: {sesion.idcurso.nombre}'
                    return render(request, 'admin/validarasistencia.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':False})
                
                if verificar:
                    asistencia = SesionAsistencia(idsesioncurso=sesion, idusuario=user, asistencia_pendiente=True)
                    asistencia.save()
                    mensaje = f'{texto}. Tu asistencia para la sesión número {numero_sesion} del curso "{sesion.idcurso.nombre}" ha sido registrada exitosamente.'
                return render(request, 'admin/validarasistencia.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':False})
                
            else:
                mensaje = f'la sesion {idsesion} no existe'
                return render(request, 'admin/validarasistencia.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':False}) 
    else:    
        return render(request, 'admin/validarasistencia.html',{'idsesion':idsesion, 'estado':False})
        

def generarqr(request, idsesion):
    data = f'http://localhost:8000/administracion/validarasistencia/{idsesion}/'
    relative_path = generar_qr(data,idsesion)
    print('ruta es', relative_path)
    return render(request, 'admin/codigoqr.html',{"qr_code_url":relative_path, 'idsesion':idsesion, 'data':data})


@login_required
def listarasistentes(request, idsesion):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    sesion = Sesioncurso.objects.get(id=idsesion)
    if perfil_usuario.idrol.id == 3:
       areajefe = perfil_usuario.idarea.id
       usuarios = SesionAsistencia.objects.filter(Q(idusuario__idarea=areajefe) | Q(idusuario__idepart__idarea=areajefe), idsesioncurso=sesion).order_by('-fecha_asistencia')
    else:
       usuarios = SesionAsistencia.objects.filter(idsesioncurso=sesion)
    return render(request, 'admin/listasistentes.html', {'usuarios':usuarios, 'usu':perfil_usuario, 'sesion':idsesion})

@login_required #proteger la ruta
def eliminarasistente(request, idasis):
    try:
        asistente = SesionAsistencia.objects.get(id=idasis)
        sesion = asistente.idsesioncurso.id
        asistente.delete()
        messages.success(request, 'Asistente eliminado exitosamente.')
    except SesionAsistencia.DoesNotExist:
        messages.error(request, 'El Asistente no existe')
    return redirect('listarasistentes', idsesion=sesion)
#Fin codigo Jhon

@login_required
def listarcalificacion(request):
    #==== variables ===============
    totaplicabilidad, totalclaridad, totrelevancia, promaplicabilidad, promclaridad, promrlevancia  = 0, 0, 0, 0, 0, 0
    #==== variables ==
    totclaridad, totcapacidad, totdominio = 0, 0, 0
    formclaridad, formcapacidad,  formdominio = 0, 0, 0
    valoresformador = ''
    idcurso = request.POST.get('idcurso') #=== recibe la variable de post
    curso = Curso.objects.get(id=idcurso)
    #=========== informacion ===========
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    #==== validar si el usuario es jefe ==============
    if perfil_usuario.idrol.id == 3:
        areajefe = perfil_usuario.idarea.id
        datos = CalificacionUsuarios.objects.filter(Q(idusuario__idarea=areajefe) | Q(idusuario__idepart__idarea=areajefe), curso=curso)
        formador = CalificacionFormador.objects.filter(Q(usuario__idarea=areajefe) | Q(usuario__idepart__idarea=areajefe), curso=curso)
    else:
       datos = CalificacionUsuarios.objects.filter(curso=curso)
       formador = CalificacionFormador.objects.filter(curso=curso) #== calificacion de los formadores
    
    if datos:
        for dat in datos:
            totaplicabilidad += dat.aplicabilidad  # Sumar aplicabilidad
            totalclaridad += dat.claridad # sumar el total de claridad
            totrelevancia += dat.relevancia # sumar relevancia
           
        promaplicabilidad = (totaplicabilidad/(5*len(datos)))*100
        promclaridad = (totalclaridad/(5*len(datos)))*100
        promrlevancia = (totrelevancia/(5*len(datos)))*100
        #=========== calcular los valores para torta de curso =====
        totcurso = promaplicabilidad + promclaridad + promrlevancia
        valorc1 = (promrlevancia/totcurso)*100
        valorc2 = (promclaridad/totcurso)*100
        valorc3 = (promaplicabilidad/totcurso)*100
        valorescurso = {'valorc1': valorc1, 'valorc2': valorc2, 'valorc3': valorc3}
    
    #========= sacar los datos de la calificacion del fomador
    if formador: 
        for cap in formador:
            totclaridad += cap.claridad
            totcapacidad += cap.capacidad
            totdominio += cap.dominio
        #======== completar los promedios ================= 
        formclaridad = (totclaridad/(5*len(formador)))*100
        formcapacidad = (totcapacidad/(5*len(formador)))*100
        formdominio = (totdominio/(5*len(formador)))*100
        #========= calcular los valores para la torta formador ==================
        totsum = formclaridad + formcapacidad + formdominio 
        valor1 = (formclaridad/totsum)*100
        valor2 = (formcapacidad/totsum)*100
        valor3 = (formdominio/totsum)*100
        valoresformador = {'valor1': valor1, 'valor2': valor2, 'valor3': valor3}
    return render(request, 'admin/liscalificacionuser.html',{'usu':perfil_usuario, 'datos':datos, 'curso':curso, 'formador':formador, 'promaplicabilidad':promaplicabilidad, 'promclaridad':promclaridad, 'promrlevancia':promrlevancia, 'formclaridad':formclaridad, 'formcapacidad':formcapacidad, 'formdominio':formdominio, 'valores':valoresformador, 'valorescurso':valorescurso })

#==================== aqui imprimir la información de graficas del total de curso =============
@login_required
def metricasCurso(request, idcurso):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    #totalsesiones = Sesioncurso.objects.filter(idcurso=idcurso)
    curso = Curso.objects.get(id=idcurso)#==consultar la informacion del curso
    sumaplicabilidad, sumclaridad, sumrelevancia = 0, 0, 0
    sumclaridadfor, sumcapacidad, sumdominio = 0, 0, 0
    valorescurso, barras, valoresformador, barraform = '', '', '', ''
    #=== obtener el total de calificaciones por sesion =========
    datos_sesion = CalificacionUsuarios.objects.filter(curso=curso.id)
    #====== obtener  el total de calificacion de formador =======
    formador_sesion = CalificacionFormador.objects.filter(curso=curso.id) 
    #========= calcular los datos de porcentaje ===============
    if datos_sesion:
        for dat in datos_sesion:  
            sumaplicabilidad += dat.aplicabilidad  # Sumar aplicabilidad
            sumclaridad += dat.claridad # sumar el total de claridad
            sumrelevancia += dat.relevancia # sumar relevancia
        num_sesiones = (5*len(datos_sesion))
        promaplicabilidad = (sumaplicabilidad/num_sesiones)*100
        promclaridad = (sumclaridad/num_sesiones)*100
        promrlevancia = (sumrelevancia/num_sesiones)*100
        #====== calcular valores de porcentaje =======
        totcurso = promaplicabilidad + promclaridad + promrlevancia
        valorc1 = (promrlevancia/totcurso)*100
        valorc2 = (promclaridad/totcurso)*100
        valorc3 = (promaplicabilidad/totcurso)*100
        valorescurso = {'valorc1': valorc1, 'valorc2': valorc2, 'valorc3': valorc3}
        barras = {'relevancia':promrlevancia, 'claridad':promclaridad, 'aplicacion':promaplicabilidad}
    #============= calcular los datos para porcentaje de formador =======
    if formador_sesion:
        for cap in formador_sesion: 
            sumclaridadfor += cap.claridad
            sumcapacidad += cap.capacidad
            sumdominio += cap.dominio
        #======== completar los promedios ================= 
        num_formadores = (5*len(formador_sesion))
        formclaridad = (sumclaridadfor/num_formadores)*100
        formcapacidad = (sumcapacidad/num_formadores)*100
        formdominio = (sumcapacidad/num_formadores)*100
        #========= calcular los valores para la torta formador ==================
        totsum = formclaridad + formcapacidad + formdominio 
        valor1 = (formclaridad/totsum)*100
        valor2 = (formcapacidad/totsum)*100
        valor3 = (formdominio/totsum)*100
        valoresformador = {'valor1': valor1, 'valor2': valor2, 'valor3': valor3}
        barraform = {'valorb1': formclaridad, 'valorb2':formcapacidad, 'valorb3':formdominio}
    return render(request, 'admin/metricascurso.html',{'usu':perfil_usuario, 'curso':curso, 'valorescurso':valorescurso, 'barras':barras, 'valores':valoresformador, 'barraform':barraform })
   

@login_required
def borrarcalificacion(request, idcali):
    try:
        calificacion = CalificacionUsuarios.objects.get(id=idcali)
        calificacion.delete()
        sesion = calificacion.id_sesiones_curso.id
        bsesion = calificacion.id_sesiones_curso
        buser = calificacion.idusuario
        calformador = CalificacionFormador.objects.get(sesion_curso=bsesion, usuario=buser)
        calformador.delete()
        messages.success(request, 'Calificacion eliminada exitosamente.')
    except:
        messages.success(request, "Lo sentimos, ocurrio un error en la eliminación.")
    return redirect('listarcalificacion', idsesion=sesion)

def compromisos_listar(usuarios, idcurso):
    usuarios_con_compromisos = {}
    if idcurso != 0:
      idcursob = Curso.objects.get(id=idcurso)
      sesion_ids = Sesioncurso.objects.filter(idcurso=idcursob).values_list('id', flat=True)
      #=== obtine el total de compromisos por cada sesion del curso =======
      for usuario in usuarios:
            conta_total = Compromisos.objects.filter(id_usuario=usuario.id, id_sesion__in=sesion_ids).count()
            conta_total_terminados = Compromisos.objects.filter(id_usuario=usuario.id, id_estado=1, id_sesion__in=sesion_ids).count()
            conta_total_pendientes = Compromisos.objects.filter(id_usuario=usuario.id, id_estado=2, id_sesion__in=sesion_ids).count()
            conta_total_incum = Compromisos.objects.filter(id_usuario=usuario.id, id_estado=3, id_sesion__in=sesion_ids).count()
            usuarios_con_compromisos[usuario] = {
                                                    'total': conta_total,
                                                    'terminados': conta_total_terminados,
                                                    'pendientes': conta_total_pendientes,
                                                    'incumplidos': conta_total_incum
                                                    }
    #========= obtiene compromisos por todos los cursos                                           
    else:
        for usuario in usuarios:
            conta_total = Compromisos.objects.filter(id_usuario=usuario.id).count()
            conta_total_terminados = Compromisos.objects.filter(id_usuario=usuario.id, id_estado=1).count()
            conta_total_pendientes = Compromisos.objects.filter(id_usuario=usuario.id, id_estado=2).count()
            conta_total_incum = Compromisos.objects.filter(id_usuario=usuario.id, id_estado=3).count()
            usuarios_con_compromisos[usuario] = {
                                                    'total': conta_total,
                                                    'terminados': conta_total_terminados,
                                                    'pendientes': conta_total_pendientes,
                                                    'incumplidos': conta_total_incum
                                                }
    
    return usuarios_con_compromisos

@login_required # aqui permite retornar el listado de usuarios para elegir y ver los compromisos
def listar_compromisos(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    formador = ''
    cursos = ''
    #=====================================================
    if perfil_usuario.idrol.id == 4: #=== si el usuario es formador
        formador = FormadorEmpresa.objects.get(idusu=perfil_usuario, estado=True)
        cursos = Curso.objects.filter(idusu=perfil_usuario.id)
        grupos_cursos = GruposCursos.objects.filter(idcurso__in=cursos).values('idgrupo').distinct()
        usuarios_grupo = GruposUser.objects.filter(idgrupo__in=grupos_cursos).values('iduser').distinct()
        usuarios = UserPerfil.objects.filter(id__in=usuarios_grupo)

    elif perfil_usuario.idrol.id == 1: #=== si el usuario es administrador
        cursos = Curso.objects.all()
        usuarios = UserPerfil.objects.all().exclude(idrol__in=[1, 4, 5])
    
    elif perfil_usuario.idrol.id == 3: #==== si el usuario es jefe
         areajefe = perfil_usuario.idarea.id
         usuarios = UserPerfil.objects.filter(Q(idarea=areajefe) | Q(idepart__idarea=areajefe)).exclude(idrol__in=[1, 4, 5])
    
    elif perfil_usuario.idrol.id == 5: #==== si el usuario es administrador(gerente)
         idempresa = perfil_usuario.idempresa.id
         usuarios = UserPerfil.objects.filter(Q(idarea__idempresa=idempresa) | Q(idepart__idarea__idempresa=idempresa)).exclude(idrol__in=[1, 4, 5])
         cursos = Curso.objects.filter(idempresa=idempresa)
    #======== obtener los compromisos por cada usuario========================
    estados = EstadoCompromisos.objects.all()
    usuarios_con_compromisos = compromisos_listar(usuarios, 0) #=== llama a la funcion compromisos
    return render(request, 'admin/listadousercompromisos.html', {'usu':perfil_usuario, 'usuarios':usuarios_con_compromisos, 'formador':formador, 'estados':estados, 'cursos':cursos})

# aqui permite ver los compromisos por cada usuario 
@login_required
def  vercompromisos(request, iduser):
     perfil_usuario = UserPerfil.objects.get(user=request.user)
     usu = UserPerfil.objects.get(id=iduser)
     compromisos = Compromisos.objects.filter(id_usuario=usu)
     estados = EstadoCompromisos.objects.all()
     return render(request, 'admin/usuariocompromiso.html', {'usu':perfil_usuario, 'compromisos':compromisos, 'estados':estados, 'usuario':usu})

#========filtrar los compromisos por curso =======
@login_required
def filtroCompromisos(request):
  #=== buscar el cuso asociado ====
  if request.method == 'POST':
    idcur = request.POST.get('idcur') #=== capyurar el id del parametro
    curso = Curso.objects.get(id=idcur)
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    grupoasociado = GruposCursos.objects.filter(idcurso=idcur)
    formador = ''
    users_com = GruposUser.objects.none() 
    users_total = UserPerfil.objects.none()
    for grup in grupoasociado:
        users = GruposUser.objects.filter(idgrupo=grup.idgrupo.id).values('iduser').distinct()
        users_com = users_com.union(users)  # Unir los conjuntos de usuarios
    #================ usuario administrador (gerente)
    if perfil_usuario.idrol.id == 5:
        for user in users_com:
            idemp = perfil_usuario.idempresa.id
            usu = UserPerfil.objects.filter(Q(idarea__idempresa=idemp) | Q(idepart__idarea__idempresa=idemp), id=user['iduser'])
            users_total = users_total.union(usu)
    else:
        for user in users_com:
            usu = UserPerfil.objects.filter(id=user['iduser'])
            users_total = users_total.union(usu)

    usuarios_con_compromisos = compromisos_listar(users_total, idcur) #=== llama a la funcion compromisos
    estados = EstadoCompromisos.objects.all()
    #=====================================================
    if perfil_usuario.idrol.id == 4:
        formador = FormadorEmpresa.objects.get(idusu=perfil_usuario, estado=True)
        cursos = Curso.objects.filter(idusu=perfil_usuario.id)
    #============= usuario administrador (gerente)
    elif perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        cursos = Curso.objects.filter(idempresa=idempresa)
    else:
        cursos = Curso.objects.all()
    #======== obtener los compromisos por cada usuario========================
    userids = users_total.values_list('id', flat=True)
    usercom = Compromisos.objects.filter(id_usuario__in=userids, id_sesion__idcurso=curso)
    #usucompromisos = Compromisos.
    return render(request, 'admin/listadousercompromisos.html', {'usu':perfil_usuario, 'usuarios':usuarios_con_compromisos, 'formador':formador, 'estados':estados, 'cursos':cursos, 'curso_ac':curso, 'usercom':usercom, 'idcur':idcur})
  else:
    return redirect('listar_compromisos')
      
#aqui actualiza el compromiso de cada usuario
@login_required
def savecompromiso(request):
    if request.method == 'POST':
        formador = ''
        #obtener estado
        idestado = request.POST.get("estado")
        idcom = request.POST.get("idcom") #=== variable para recibir el id del curso
        compromiso = Compromisos.objects.get(id=idcom)
        compromiso.respuesta = request.POST.get("respuesta")
        compromiso.id_estado = EstadoCompromisos.objects.get(id=idestado)
        compromiso.puntaje = request.POST.get("puntaje")
        compromiso.save()
    #====================================================
        #obtener usuario
        perfil_usuario = UserPerfil.objects.get(user=request.user)
        estados = EstadoCompromisos.objects.all()
        mensaje = "Información guardada de manera exitosa"
        estados = EstadoCompromisos.objects.all()
        cursos = Curso.objects.all()
        #=====================================================
        if perfil_usuario.idrol.id == 4:
            formador = FormadorEmpresa.objects.get(idusu=perfil_usuario, estado=True)
            cursos = Curso.objects.filter(idusu=perfil_usuario.id)
            grupos_cursos = GruposCursos.objects.filter(idcurso__in=cursos).values('idgrupo').distinct()
            usuarios_grupo = GruposUser.objects.filter(idgrupo__in=grupos_cursos).values('iduser').distinct()
            usuarios = UserPerfil.objects.filter(id__in=usuarios_grupo)
        elif perfil_usuario.idrol.id == 3:
            areajefe = perfil_usuario.idarea.id
            usuarios = UserPerfil.objects.filter(Q(idarea=areajefe) | Q(idepart__idarea=areajefe)).exclude(idrol__in=[1, 4, 5])
        elif perfil_usuario.idrol.id == 5:
            idempresa = perfil_usuario.idempresa.id
            usuarios = UserPerfil.objects.filter(Q(idarea__idempresa=idempresa) | Q(idepart__idarea__idempresa=idempresa)).exclude(idrol__in=[1, 4, 5])
            cursos = Curso.objects.filter(idempresa=idempresa)
        else:
            usuarios = UserPerfil.objects.all().exclude(idrol__in=[1, 4, 5])
        usuarios_con_compromisos = compromisos_listar(usuarios, 0) #=== llama a la funcion compromisos
        return render(request, 'admin/listadousercompromisos.html', {'usu':perfil_usuario, 'usuarios':usuarios_con_compromisos, 'formador':formador, 'estados':estados, 'mensaje':mensaje,'cursos':cursos})

@login_required
def addrespuesta(request, idcomp):
    if request.method == 'POST':
        compromiso = Compromisos.objects.get(id=idcomp)
        compromiso.puntaje = request.POST.get("puntuacion")
        compromiso.respuesta = request.POST.get("txtRespuesta")
        compromiso.id_estado = EstadoCompromisos.objects.get(descripcion="cumplido")
        compromiso.save()
        mensaje="Compromiso respondido correctamente"
        return redirect('listarcompromisos')
    else:
        return redirect('listarcompromisos')

@login_required
def delete_compromiso(request, idcomp):
    compromiso = Compromisos.objects.filter(id=idcomp)
    compromiso.delete()
    mensaje="Compromiso eliminado correctamente"
    #aqui buscar el compromiso para devolver a todo el listado de usuarios
    comActu = Compromisos.objects.get(id=idcomp)
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    usu = UserPerfil.objects.get(id=comActu.id_usuario.id)
    compromisos = Compromisos.objects.filter(id_usuario=usu)
    estados = EstadoCompromisos.objects.all()
    return render(request, 'admin/usuariocompromiso.html', {'usu':perfil_usuario, 'compromisos':compromisos, 'mensaje':mensaje, 'estados':estados, 'usuario':usu})

def inscribir_asistente(request, idsesion):
    if request.method == 'POST':
        try: 
            user = User.objects.create_user(username=request.POST['correo'], 
            password=request.POST['cedula'])
            user.save()
            rol_user = RolUser.objects.get(id=2)
            
            userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['apellido'], telefono=request.POST['telefono'], cedula=request.POST['cedula'], idrol=rol_user, cargo=request.POST['cargoUser'], idepart=None, idarea=None, user=user, pendiente=True )
            userper.save()
            #=========== vincular al grupo =======
            sesion = Sesioncurso.objects.get(id=idsesion)
            #grupo_curso = GruposCursos.objects.filter(idcurso=sesion.idcurso.id).first()
            #grupo = Grupos.objects.get(id=grupo_curso.idgrupo.id)
            try: 
               # ingreso_grupo = GruposUser(idgrupo=grupo, iduser=userper)
               # ingreso_grupo.save()
                asistencia = SesionAsistencia(idsesioncurso=sesion, idusuario=userper, asistencia_pendiente=True)
                asistencia.save()
                messages.success(request,"Usuario guardado y validado satisfactoriamente")
            except Exception as e:
                messages.error(request,"Ocurrio un error con su registro")
            
            return redirect('validarasistencia', idsesion=idsesion) # redirecciona a otra vista
        except IntegrityError:
            messages.error(request, "Error al guardar el usuario")
            return redirect('validarasistencia', idsesion=idsesion)
    #end guardar usuario
    else:
        return redirect('validarasistencia', idsesion=idsesion)

@login_required    
def cambiar_pendiente(request, idsesion, iduser):
    if request.method == 'POST':
        usuario = UserPerfil.objects.get(id=iduser)
        pendiente = request.POST.get('selectpendiente')
        usuario.pendiente = pendiente
        usuario.save()
        asistencia = SesionAsistencia.objects.get(idusuario=usuario, idsesioncurso=idsesion)
        asistencia.asistencia_pendiente = pendiente
        asistencia.save()
        messages.success(request,"Cambio de estado realizado satisfactoriamente")
        return redirect('listarasistentes', idsesion=idsesion)

#=================Aqui se registra una nueva competencia ================
@login_required  
def crearCompetencia(request):
    if request.method == 'POST':
        competencia = request.POST.get('com', None)
        competencia_existente = Competencias.objects.filter(nombre=competencia).exists()
        comp = ''
        if competencia_existente:
            mensaje = f"La competencia: {competencia} ya se encuentra registrada."
            estado  = 0
        else:
            com = Competencias(nombre=competencia)
            com.save()
            mensaje = f"La competencia: {competencia} se ha registrado exitosamente."
            estado = 1
            comp = com.id
        response_data = {
                    'estado': estado,
                    'valor': competencia,
                    'mensaje': mensaje,
                    'comp': comp
                }
        
        return JsonResponse(response_data)

#==================== eliminar competencia ==================
@login_required  
def eliminarCompetencia(request, idcom):
    competencia = get_object_or_404(Competencias, id=idcom)
    competencia.delete()
    msj = "Competencia eliminada de manera exitosa."
    #competencias = Competencias.objects.all()
    #messages.error(request, msj)
    #return HttpResponseRedirect(reverse('registroCursos'))
    response_data = {
                'mensaje': msj,
                'valor': idcom,
                'competencias': 'hola'
            }
    return JsonResponse(response_data)
  
#================= registro de usuarios ======================
@login_required
def registroUser(request):
     mensaje = ''
     perfil_usuario = UserPerfil.objects.get(user=request.user)
     if request.method == 'POST' and request.FILES['archivo']:
        archivo_excel = request.FILES['archivo']
        # Utilizamos pandas para leer el archivo Excel directamente desde la memoria
        df = pd.read_excel(archivo_excel)
        #=============== obtener los cargos, roluser, empresa fuera del bucle ======
        id_roles = df['Idrol'].dropna().unique()
        id_area = df['Idarea'].dropna().unique()
        id_depar = df['Idepart'].dropna().unique()
        id_grupo = df['Idgrupo'].dropna().unique() #=== registrar grupo
        #===== obtener todas las relaciones ===============
        roles = {role.id: role for role in RolUser.objects.filter(id__in=id_roles)}
        areasn = {area.id: area for area in Area.objects.filter(id__in=id_area)}
        departamentos = {depar.id: depar for depar in Departamento.objects.filter(id__in=id_depar)}
        #============= obtener los grupos asociados ===============
        gruposb = {grupo.id: grupo for grupo in Grupos.objects.filter(id__in=id_grupo)}
        #========== registrar a los usuarios ===============
        for index, row in df.iterrows():
            try: 
                if User.objects.filter(username=row['Email']).exists():
                   mensaje = "Alguno de los usuarios ya estan registrados"
                   continue
                user = User.objects.create_user(username=row['Email'], password=row['Password'])
                user.save()
                #========== registrar los datos en perfil user
                if row['Idarea'] and row['Idarea'] in areasn:
                    idarea = areasn[row['Idarea']]
                else:
                    idarea = None
                #================
                if row['Idepart'] and row['Idepart'] in departamentos:
                    idep = departamentos[row['Idepart']]
                else:
                    idep = None
                #================
                userper = UserPerfil(nombre=row['Nombre'], apellido=row['Apellido'], cedula=row['Cedula'], telefono=row['Telefono'], vpass=row['Password'], idrol=roles[row['Idrol']], cargo=row['Cargo'], idarea=idarea, idepart=idep, user=user )
                userper.save()
                #============= guardar el grupo con los usuarios ===========
                if row['Idgrupo']:
                   idg = gruposb[row['Idgrupo']]
                   guser = GruposUser(idgrupo=idg, iduser=userper)
                   guser.save()
                #===========================================================
                mensaje = "Registros importados de manera exitosa!"
            except IntegrityError:
                mensaje = "Error al procesar el registro"
            #======== end registrar ============================
     #=========== si el usuario es administrador (gerente)================
     if perfil_usuario.idrol.id == 5:
        idempresa = perfil_usuario.idempresa.id
        usuarios = UserPerfil.objects.filter(Q(idarea__idempresa=idempresa) | Q(idepart__idarea__idempresa=idempresa)).exclude(idrol__in=[1]) #=== todos los usuarios para listar
        empresa = Empresa.objects.filter(id=idempresa) #== listado de la empresa
        grupos = Grupos.objects.filter(idempresa=idempresa)
        cursos = Curso.objects.filter(idempresa=idempresa)
     else:
        usuarios = UserPerfil.objects.all() #=== todos los usuarios para listar
        empresa = Empresa.objects.all() #== listado de empresas
        grupos = Grupos.objects.all()
        cursos = Curso.objects.all()
     #======== areas y departamentos ==============
     areas = Area.objects.all() 
     depar = Departamento.objects.all()
     rol = RolUser.objects.all()
     formadorempresa = FormadorEmpresa.objects.all()
     return render(request, 'admin/registrouser.html', {'usu':perfil_usuario, 'mensaje':mensaje, 'usuarios':usuarios, 'empresa':empresa, 'areas':areas, 'depar':depar, 'roles':rol, 'formador':formadorempresa, 'grupos':grupos,'cursos':cursos})

#================= aqui registrar nuevo usuario =================
@login_required
def addNewUser(request):
    if request.method == 'POST':
       #================== registrar user ==============
       try: 
              id_rol = request.POST['rol']
              cargo_user = request.POST.get('cargo', '')
              idepar = request.POST.get('depar', '')
              idarea = request.POST.get('area', '')
              idempresa = request.POST.get('emp', '')
              #================ consultas ================
              rol_user = get_object_or_404(RolUser, id=id_rol)
              id_empresa = get_object_or_404(Empresa, id=idempresa)
              #========= crear el usuario ========
              user = User.objects.create_user(username=request.POST['email'], password=request.POST['pass'])
              user.save()
              #========== crear el user perfil==========
              if rol_user.id != 4 and rol_user.id != 5:
                if not idepar:
                    id_area = Area.objects.get(id=idarea)
                    id_depar = None
                else: 
                    id_depar = Departamento.objects.get(id=idepar)
                    id_area = None
                userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['apellido'], cedula=request.POST['ced'], telefono=request.POST['tel'], vpass=request.POST['pass'], idrol=rol_user, cargo=cargo_user, idepart=id_depar, idarea=id_area, user=user )
                userper.save()
              else: 
                if rol_user.id == 5:
                   userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['apellido'], cedula=request.POST['ced'], telefono=request.POST['tel'], vpass=request.POST['pass'], idrol=rol_user, cargo=cargo_user, idepart=None, idarea=None, user=user, idempresa=id_empresa)
                   userper.save()
                else:
                   userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['apellido'], cedula=request.POST['ced'], telefono=request.POST['tel'], vpass=request.POST['pass'], idrol=rol_user, cargo=cargo_user, idepart=None, idarea=None, user=user )
                   userper.save()
                #============ guardar la relacion de empresa y formador
                formador = FormadorEmpresa(idempresa=id_empresa, idusu=userper)
                formador.save()
              
              mensajereg = f"El usuario: {userper.user.username}, ha sido registrado exitosamente"
       except IntegrityError:
              mensajereg = "Error: El usuario ya se encuentra registrado."
    messages.error(request, mensajereg)
    return HttpResponseRedirect(reverse('registroUser'))

#============= filtrar usuarios ============
@login_required
def filterUser(request):
    if request.method == 'POST':
        perfil_usuario = UserPerfil.objects.get(user=request.user)
        areas = Area.objects.all() 
        depar = Departamento.objects.all()
        rol = RolUser.objects.all()
        formadorempresa = FormadorEmpresa.objects.all()
        #=========== validar el filtro ===========
        if perfil_usuario.idrol.id == 5:
            idempresa = perfil_usuario.idempresa.id
            empresas = Empresa.objects.filter(id=idempresa) #== listado de la empresa
            grupos = Grupos.objects.filter(idempresa=idempresa)
            cursos = Curso.objects.filter(idempresa=idempresa)
        else:
            empresas = Empresa.objects.all() #== listado de empresas
            grupos = Grupos.objects.all()
            cursos = Curso.objects.all()
        #========= datos del formulario ========
        idemp = request.POST.get('idempresa', '')
        idgrupo = request.POST.get('idgrupo', '')
        idcurso = request.POST.get('idcurso', '')
        usuarios =''
        #==== validar para imprimir los datos ===========0
        if idemp:
           empresa = Empresa.objects.get(id=idemp)
           usuarios = UserPerfil.objects.filter(Q(idarea__idempresa=empresa) | Q(idepart__idarea__idempresa=empresa))
           mensaje = f'Lista de usuarios pertenecientes a la empresa: {empresa.nombre}'
        if idgrupo:
           grupo = Grupos.objects.get(id=idgrupo)
           gruposuser_ids = GruposUser.objects.filter(idgrupo=grupo).values_list('iduser', flat=True)
           usuarios = UserPerfil.objects.filter(id__in=gruposuser_ids)
           mensaje = f'Lista de usuarios pertenecientes al grupo: {grupo.nombre}'
        if idcurso: 
            #============ datos de usuarios ===========
            curso = Curso.objects.get(id=idcurso)
            grupoasociado = GruposCursos.objects.filter(idcurso=curso)
            for grup in grupoasociado:
                users_ids = GruposUser.objects.filter(idgrupo=grup.idgrupo.id).values_list('iduser', flat=True).distinct()
                usuarios = UserPerfil.objects.filter(id__in=users_ids)
            mensaje = f'Lista de usuarios pertenecientes al curso: {curso.nombre}'
        datos = {'usu':perfil_usuario, 'mensajefil':mensaje, 'usuarios':usuarios, 'empresa':empresas, 'areas':areas, 'depar':depar, 'roles':rol, 'formador':formadorempresa, 'grupos':grupos,'cursos':cursos}
        return render(request, 'admin/registrouser.html', datos)

#==========eliminar usuarios==================
@login_required
def deleteUser(request, idusu):
    find_user = get_object_or_404(UserPerfil, id=idusu)
    find_user.delete()
    usu = User.objects.get(id=find_user.user.id)
    usu.delete()
    mensajeDelete = f"Usuario: {find_user.user.username}, eliminado de manera exitosa "
    messages.error(request, mensajeDelete)
    return HttpResponseRedirect(reverse('registroUser'))

#============= desactivar un usuario ===========
@login_required
def lockaccess(request, idusu):
    user = get_object_or_404(UserPerfil, id=idusu)
    if user.estado != 0:
        user.estado = 0
    else:
        user.estado = 1
    user.save()
    mensajeDelete = f"El estado del usuario: {user.user.username}, ha cambiado de manera exitosa."
    messages.error(request, mensajeDelete)
    return HttpResponseRedirect(reverse('registroUser'))

#============= update user =====
@login_required
def updateUser(request, idusu):
    if request.method == 'POST':
      try: 
              id_rol = request.POST.get('rolUsu', '')
              cargo_user = request.POST.get('cargoUsu', '')
              idepar = request.POST.get('deparUsu', '')
              idarea = request.POST.get('areaUsu', '')
              passw = request.POST.get('passwUsu', '')

              #================ consultas ====
              userupdate = get_object_or_404(UserPerfil, id=idusu)
              if userupdate.idrol.id != 4:
                if not idepar:
                    id_area = Area.objects.get(id=idarea)
                    id_depar = None
                else: 
                    id_depar = Departamento.objects.get(id=idepar)
                    id_area = None
              else:
                  empresas_selec = request.POST.getlist('empvincu')
                  id_depar = None
                  id_area = None
              #============ validar que no esten vacios =======
              rol_user = get_object_or_404(RolUser, id=id_rol)
              #========== actualizar el user perfil==========
              userupdate.nombre = request.POST['nombreUsu']
              userupdate.apellido = request.POST['apellidoUsu']
              userupdate.cedula = request.POST['cedUsu']
              userupdate.telefono = request.POST['telUsu']
              userupdate.idrol = rol_user 
              userupdate.cargo = cargo_user
              userupdate.idepart = id_depar     
              userupdate.idarea = id_area          
              userupdate.save()
              #========= update el usuario ========
              user = get_object_or_404(User, id=userupdate.user.id)
              if passw:
                user.set_password(passw)
                user.save()
              if userupdate.idrol.id == 4:
                #==== borrar los datos antes de actualizar ==============
                FormadorEmpresa.objects.filter(idusu=userupdate).delete()
                for empresa_id in empresas_selec:
                    empresa = Empresa.objects.get(id=empresa_id)
                    formadorempresa = FormadorEmpresa(idempresa=empresa, idusu=userupdate)
                    formadorempresa.save()   
              #================================================
              mensajeUpdate = f"El usuario: {userupdate.user.username}, ha sido actualizado exitosamente"
      except IntegrityError:
              mensajeUpdate = "Error: El sistema no puede encontrar el usuario."
      messages.error(request, mensajeUpdate)
      return HttpResponseRedirect(reverse('registroUser'))
    
#============= generar excel de los asistentes a la sesion 
@login_required
def excelasistentes(request, idsesion):
    total_datos = []
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    sesion = Sesioncurso.objects.get(id=idsesion)
    if perfil_usuario.idrol.id == 3:
       areajefe = perfil_usuario.idarea.id
       usuarios = SesionAsistencia.objects.filter(Q(idusuario__idarea=areajefe) | Q(idusuario__idepart__idarea=areajefe), idsesioncurso=sesion).order_by('-fecha_asistencia')
    else:
       usuarios = SesionAsistencia.objects.filter(idsesioncurso=sesion)
    #=== iterar sobre todos los usuarios =============
    for usuinfo in usuarios:
        total_datos.append({
            'Nombre': usuinfo.idusuario.nombre,
            'Apellido': usuinfo.idusuario.apellido,
            'No Identificación': usuinfo.idusuario.cedula,
            'Correo': usuinfo.idusuario.user.username,
            'Cargo': usuinfo.idusuario.cargo,
        })
    df = pd.DataFrame(total_datos) #convertir los datos a data frame
    archivo_excel = BytesIO()
    df.to_excel(archivo_excel, index=False)
    archivo_excel.seek(0)
    # Crear una respuesta HTTP con el archivo de Excel
    response = HttpResponse(archivo_excel, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="asistencia_usuarios.xlsx"'
    return response

#=========== funcion para duplicar curso ===
@login_required
def copyCursos(request, idcurso):
    curso_original = get_object_or_404(Curso, id=idcurso)
    with transaction.atomic():
        # Duplicar el formulario
        curso_nuevo = Curso.objects.create(
            nombre=f"{curso_original.nombre} (Copia)",  # Agregar 'Copia' solo al nombre
            descrip=f"{curso_original.descrip} (Copia)",  # Agregar 'Copia' solo a la descripción
            precio=curso_original.precio,  # Copiar el precio tal cual (asumiendo que es numérico)
            idempresa=curso_original.idempresa,  # Copiar la relación a empresa
            idusu=curso_original.idusu,  # Copiar la relación al usuario
          )
        
        #==== duplicar las competencias del curso
        for competencias_original in CompetenciaCurso.objects.filter(idcurso=curso_original):
            CompetenciaCurso.objects.create(
                    idcompetencia=competencias_original.idcompetencia,
                    idcurso=curso_nuevo,  # Relacionar la nueva sesión con el curso duplicado
                )

        # Duplicar las sesiones del curso
        for sesiones_original in Sesioncurso.objects.filter(idcurso=curso_original):
            sesion_nueva=Sesioncurso.objects.create(
                fechainicio=sesiones_original.fechainicio,
                fechafin=sesiones_original.fechafin,
                lugar=sesiones_original.lugar,
                estado=sesiones_original.estado,
                idcurso=curso_nuevo,  # Relacionar la nueva sesión con el curso duplicado
             )
             
            #duplicar temas
            for temas_original in TemasSesion.objects.filter(idsesion=sesiones_original):
                TemasSesion.objects.create(
                    descrip=temas_original.descrip,
                    competencias=temas_original.competencias,
                    recursos=temas_original.recursos,  
                    idsesion=sesion_nueva,
                    ruta=temas_original.ruta,
            )
            
        # Diplicar los objetivos del curso
        for objetivos_original in ObjetivosCurso.objects.filter(idcurso=curso_original):
            ObjetivosCurso.objects.create(
                descrip=objetivos_original.descrip,
                competencias=objetivos_original.competencias,
                idcurso=curso_nuevo,  # Relacionar la nueva sesión con el curso duplicado
            )
            
        #==== instanciar la parte de 
    return HttpResponseRedirect(reverse('listarcursos'))
   