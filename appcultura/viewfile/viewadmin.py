from ast import Delete
from email import message
import json
import os
import mimetypes
from pdb import post_mortem
import select
from urllib import request, response
from django.conf import settings
from django.core.files.storage import FileSystemStorage
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
import pandas as pd

from appcultura.modelos.calificacionusuarios import CalificacionUsuarios
from appcultura.modelos.compromisos import Compromisos
from appcultura.modelos.estado_compromisos import EstadoCompromisos
from appcultura.modelos.formador_empresa import FormadorEmpresa #errores de la base de datos
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

from appcultura.viewfile.fadmin.functionadmin import generar_qr
#Fin Codigo Jhon

@login_required #proteger la ruta
def registroCursos(request):
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  comp = Competencias.objects.all()
  formadores = UserPerfil.objects.filter(idrol=4)
  if request.method == 'POST':
      #=== Get data lists =======
      fechas_inicio = request.POST.getlist('fecha_inicio[]')
      fechas_final = request.POST.getlist('fecha_final[]')
      lugares = request.POST.getlist('lugar[]')
      descripciones = request.POST.getlist('desobj[]')
      competencias = request.POST.getlist('competencias[]')
      compe = request.POST.getlist('compe')
      nombre_curso = request.POST['nombre']
      formador_select = request.POST.get('formador', '')
      empresa_select = request.POST.get('empresa', '')
      
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
              id_formador = perfil_formador
              id_empresa = empresa_sel 
          else:
              id_formador = None
              id_empresa = None

      regcurso = Curso(nombre=request.POST['nombre'], descrip=request.POST['descrip'], precio=request.POST['precio'], idempresa=id_empresa, idusu=id_formador)
      regcurso.save()
      idcurso = Curso.objects.get(id=regcurso.id)

      #=========== registers of competences =================
      for com in compe:
          idcom = Competencias.objects.get(id=com)
          regcom = CompetenciaCurso(idcompetencia=idcom, idcurso=idcurso)
          regcom.save()
      #======= here register of objectives of course ==========
      for description, competencia in zip(descripciones, competencias):
            regobject = ObjetivosCurso(descrip=description, competencias=competencia, idcurso=idcurso)
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
                fs = FileSystemStorage(location=os.path.join(settings.STATIC_ROOT, 'archivos')) 
                nombre_archivo = fs.save(archivo.name, archivo)
                ruta_destino = fs.url(nombre_archivo)
            else:
                ruta_destino = None
            #========guarda los temas
            regtema = TemasSesion(descrip=tema, competencias=destema, recursos=recur, ruta=ruta_destino, idsesion=regsesion)
            regtema.save()
      #========= send messaje and return the view of courses =================
      mensaje = "Curso registrado exitosamente"
      idcom = 1
      return render(request, 'admin/addcurso.html', {'usu':perfil_usuario, 'msj':mensaje, 'competencias':comp, 'idcom':idcom, 'formadores':formadores})
  else:
      return render(request, 'admin/addcurso.html', {'usu':perfil_usuario, 'competencias':comp, 'formadores':formadores})

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
          cursos = Curso.objects.filter(idusu=perfil_usuario, idempresa=empselect.idempresa) 
       else:  
          cursos = Curso.objects.all()
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
    if request.method == 'POST':
        print(request.POST)
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
        #Recibe los objetivos en caso de que existan
        
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
                fs = FileSystemStorage(location=os.path.join(settings.STATIC_ROOT, 'archivos')) 
                nombre_archivo = fs.save(archivo.name, archivo)
                ruta_destino = fs.url(nombre_archivo)
            else:
               ruta_destino = temasesion.ruta
            temasesion.ruta = ruta_destino
            temasesion.save()

        messages.success(request, 'Curso actualizado exitosamente.')
        return redirect('listarcursos')
    else:
        return render(request, 'admin/updatecurso.html', {'usu':perfil_usuario, 'curso': curso, 'sesiones': sesiones, 'objetivos': objetivos, 'temas':tematicas})
     
#crear funcion para crear kpi de area o departamento  
@login_required #proteger la ruta
def kpiarea(request):
    try:
        perfil_usuario = UserPerfil.objects.get(user=request.user)
        if request.method == 'POST':
            print(request.POST)
            # ================= here the KPI of areas =============
            objetivos = request.POST.getlist('objetivos[]')
            metas = request.POST.getlist('metas[]')
            indicadores = request.POST.getlist('indicadores[]')
            #idem = perfil_usuario.idempresa  # aquí se obtiene la empresa a la cual pertenece
            #idemp = idem.idempresa  # se obtiene el idempresa
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
    
    area = Area.objects.all()
    depart = Departamento.objects.all()
    empresas = Empresa.objects.all()
    #================= obtner las fechas actuales ================
    fecha_actual_utc = timezone.now()
    fecha_actual_local = timezone.localtime(fecha_actual_utc)
   
    return render(request, 'admin/kpiareasdep.html', {'usu': perfil_usuario, 'area': area, 'depart': depart, 'fecha':fecha_actual_local, 'empresas':empresas})

#listar KPIs de cada area
@login_required
def listarkpiarea(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    kparea = Kpiarea.objects.all()
    kpobj = Kpiobjetivos.objects.all()
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
    empresa = Empresa.objects.all()
    if not infokpi.idarea:
        emprincipal = Empresa.objects.get(id=infokpi.idepar.idarea.idempresa.id)
    else:
        emprincipal = Empresa.objects.get(id=infokpi.idarea.idempresa.id) 
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
    emp = Empresa.objects.all()
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
    grupos_cursos = GruposCursos.objects.select_related('idgrupo', 'idcurso')
    cursos_grup = Curso.objects.all()
    grupousers = GruposUser.objects.select_related('idgrupo', 'iduser')
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
    return render(request, 'admin/listgrupo.html', {'usu':perfil_usuario, 'grupos_con_cursos':grupos_con_cursos, 'grupos_des':grupos_des, 'cursos_grup':cursos_grup, 'datos_faltantes':datos_faltantes})

#=============== formulario de crear nuevo grupo con cursos y trabajadores =================
@login_required #proteger la ruta
def creargrupo(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    ngrupos = Grupos.objects.all()
    addgrupouser = GruposUser.objects.all()
    addgrupocurso = GruposCursos.objects.all()
    cursos = Curso.objects.all()
    usuarios = UserPerfil.objects.all()
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
        empresa = Empresa.objects.all()
        depars = Departamento.objects.all()
        areas =Area.objects.all()
        return render(request, 'admin/addgrupo.html', {'usu':perfil_usuario, 'ngrupos':grupos_faltantes, 'cursos':cursos, 'usuarios':usuarios, 'rol':rol, 'empresa':empresa, 'depars':depars, 'areas':areas})
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
@login_required #proteger la ruta
def saveusernuevo(request):
    if request.method == 'POST':
       perfil_usuario = UserPerfil.objects.get(user=request.user)
       ngrupos = Grupos.objects.all()
       addgrupouser = GruposUser.objects.all()
       addgrupocurso = GruposCursos.objects.all()
       cursos = Curso.objects.all()
       usuarios = UserPerfil.objects.all()
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
        #================ consultas ================
       rol_user = get_object_or_404(RolUser, id=id_rol)
        #========= crear el usuario ========
       user = User.objects.create_user(username=request.POST['email'], password=request.POST['pass'])
       user.save()
        #========== crear el user perfil==========
       if not idepar:
           id_area = Area.objects.get(id=idarea)
           id_depar = None
       else: 
        id_depar = Departamento.objects.get(id=idepar)
        id_area = None
       userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['apellido'], cedula=request.POST['ced'], telefono=request.POST['tel'], idrol=rol_user, cargo=cargo_user, idepart=id_depar, idarea=id_area, user=user )
       userper.save()
        
       #================ buscar el id de la empresa ===================
       mensaje = "Usuario guardado de manera exitosa."
       messages.info(request, mensaje)
       return render(request, 'admin/addgrupo.html', {'usu':perfil_usuario, 'ngrupos':grupos_faltantes, 'cursos':cursos, 'usuarios':usuarios, 'rol':rol, 'empresa':empresa, 'depars':depars, 'areas':areas})
#============= crear grupo ============
@login_required #proteger la ruta
def addgrupo(request):
    if request.method == 'POST': 
        nom = request.POST.get('nombreg')
        des = request.POST.get('descripg')
        if nom != '' and des != '':
           if Grupos.objects.filter(nombre=nom).exists():
              return JsonResponse({'mensaje': 'Ya existe un grupo con ese nombre. Por favor, elige un nombre diferente.'}, status=400) 
           else:
              info = Grupos(nombre=nom, descrip=des)
              info.save()
        else:
            return JsonResponse({'mensaje': 'Los campos no pueden estar vacios.'}, status=401) 
        #========== validar los grupos que deben salir =======
        addgrupouser = GruposUser.objects.all()
        addgrupocurso = GruposCursos.objects.all()
        opciones = list(
                        Grupos.objects.exclude(
                            Q(gruposuser__in=addgrupouser) | Q(gruposcursos__in=addgrupocurso)
                        ).values()
                    )
        return JsonResponse({'opciones': opciones})
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
        try:
            if nom != '' and des != '':
                if Grupos.objects.filter(nombre=nom).exists():
                    mensaje = "Ya existe un grupo con ese nombre. Por favor, elige un nombre diferente."
                    messages.error(request, mensaje)
                    url = reverse('listGrupos')
                    return HttpResponseRedirect(url)
                else:
                    datosGrupo = Grupos.objects.get(id=idgr)
                    datosGrupo.nombre = nom
                    datosGrupo.descrip = des
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
    usuarios = UserPerfil.objects.exclude(
        id__in=Subquery(
            GruposUser.objects.filter(idgrupo=idgrupo).values('iduser')
        )
    )
    #========== si es metodo post ===============
    if request.method == 'POST':
        usuariosn = request.POST.getlist('userselect')
        usunuevo = request.POST.getlist('nuevosselect')
        regusun = GruposUser.objects.filter(idgrupo=idgrupo).values('id')
        user_objetos = UserPerfil.objects.filter(id__in=usunuevo)
        grupo_objeto = Grupos.objects.get(id=idgrupo)
        # Obtener los ids presentes en la queryset
        ids_en_queryset = {usuario['id'] for usuario in regusun}
        # Encontrar el id que falta
        ids_faltantes = [id for id in ids_en_queryset if str(id) not in usuariosn]
        for id_faltante in ids_faltantes:
            getid = get_object_or_404(GruposUser, id=id_faltante)
            getid.delete()
        #agregar nuevos usuarios al grupo
        for user_objeto in user_objetos:
            grupo_usu = GruposUser(idgrupo=grupo_objeto, iduser=user_objeto)
            grupo_usu.save() 
        messages.error(request, 'Datos actualizados correctamente')
    return render(request, 'admin/listusergrupo.html', {'usu':perfil_usuario, 'regusu':regusu, 'usuarios':usuarios, 'idgrupo':idgrupo, 'gruponame':gruponame})

# aqui se puede actualizar los cursos en cada grupo
def cursosgrupo(request, idgrupo):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    regcurso = GruposCursos.objects.filter(idgrupo=idgrupo)
    gruponame = Grupos.objects.get(id=idgrupo)
    cursos = Curso.objects.exclude(
        id__in=Subquery(
            GruposCursos.objects.filter(idgrupo=idgrupo).values('idcurso')
        )
    )
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
    return render(request, 'admin/listcursogrupo.html', {'usu':perfil_usuario, 'idgrupo':idgrupo, 'regcurso':regcurso, 'cursos':cursos, 'gruponame':gruponame })
    

@login_required
def visualizarAreaDepto(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    empresa = Empresa.objects.all()
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
    empresa = Empresa.objects.all()
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
     empresa = Empresa.objects.all()
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
    empresa = Empresa.objects.all()
    areaob = Area.objects.filter(id=area).first()
    emp_select = areaob.idempresa.id #empresa elegida
    empr = Empresa.objects.get(id=emp_select)
    areas = Area.objects.filter(idempresa=empr)
    deparcom = Departamento.objects.all()
    try:
        emp = Departamento.objects.get(id=iddepar)
        emp.delete()
        messages.success(request, 'Departamento eliminado exitosamente.')
    except Empresa.DoesNotExist:
        messages.error(request, 'El departamento no existe Existe')
    return render(request, 'admin/listvinculacion.html',{'usu':perfil_usuario, 'empresa':empresa, 'areas':areas,  'selecarea':emp_select, 'emp':empr, 'depar':deparcom})

@login_required
def eliminavinculo(request, idarea):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    empresa = Empresa.objects.all()
    areaob = Area.objects.filter(id=idarea).first()
    emp_select = areaob.idempresa.id #empresa elegida
    empr = Empresa.objects.get(id=emp_select)
    areas = Area.objects.filter(idempresa=empr)
    deparcom = Departamento.objects.all()
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

            texto = request.POST.get("inputUser")
            if '@' in texto:
                if User.objects.filter(username=texto).exists():
                    usuario = User.objects.get(username=texto)
                    user = UserPerfil.objects.get(user=usuario)
   
                else:
                    mensaje = f"El usuario {texto} no se encuentra registrado en el sistema, lo invito a inscribirse"
                    return render(request, 'admin/validarasistencia.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':True})
            else:
                if UserPerfil.objects.filter(cedula=texto).exists():
                    user = UserPerfil.objects.get(cedula=texto)
                    
                else:
                    mensaje = f"El usuario {texto} no se encuentra registrado en el sistema, lo invito a inscribirse"
                    return render(request, 'admin/validarasistencia.html',{'idsesion':idsesion, 'mensaje':mensaje, 'estado':True})
            
            if Sesioncurso.objects.filter(id=idsesion).exists():
                sesion = Sesioncurso.objects.get(id=idsesion)
                cursos = GruposCursos.objects.filter(idcurso=sesion.idcurso)
                grupos = GruposUser.objects.filter(iduser=user)
                

                if SesionAsistencia.objects.filter(idsesioncurso=sesion, idusuario=user).exists():
                    mensaje="El usuario ya se encuentra registrado a esta sesión"
                    return render(request, 'admin/validarasistencia.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':False})
                
  
                if verificar:
                    asistencia = SesionAsistencia(idsesioncurso=sesion, idusuario=user, asistencia_pendiente=True)
                    asistencia.save()
                    mensaje="Asistencia verificada"
                
                        #mensaje=f'El usuario {texto} no esta asignado al curso {sesion.idcurso.nombre}'
                return render(request, 'admin/validarasistencia.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':False})
                
            else:
                mensaje = f'la sesion {idsesion} no existe'
                return render(request, 'admin/validarasistencia.html',{'idsesion':idsesion, 'mensaje':mensaje,'estado':False}) 
    else:    
        return render(request, 'admin/validarasistencia.html',{'idsesion':idsesion, 'estado':False})
        

def generarqr(request, idsesion):
    data = f'http://localhost:8000/administracion/validarasistencia/{idsesion}/'
    relative_path = generar_qr(data,idsesion)
    return render(request, 'admin/codigoqr.html',{"qr_code_url":relative_path, 'idsesion':idsesion, 'data':data})


@login_required
def listarasistentes(request, idsesion):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    sesion = Sesioncurso.objects.get(id=idsesion)
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
def listarcalificacion(request,idsesion):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    datos = CalificacionUsuarios.objects.filter(id_sesiones_curso=idsesion)
    suma=0
    promedio=0
    if datos:
        
        for dat in datos:
            suma=suma+dat.valoracion
            grupouser = GruposUser.objects.filter(iduser=dat.id_usuario)
        promedio = (suma/(5*len(datos)))*100
    else:
        grupouser = "Sin grupo"

    return render(request, 'admin/liscalificacionuser.html',{'usu':perfil_usuario, 'datos':datos, 'grupos':grupouser, 'promedio':promedio})

@login_required
def borrarcalificacion(request, idcali):
    try:
        calificacion = CalificacionUsuarios.objects.get(id=idcali)
        sesion = calificacion.id_sesiones_curso.id
        calificacion.delete()
        messages.success(request, 'Calificacion eliminada exitosamente.')
    except:
        messages.success(request, "No se pudo ingresar a la base de datos")
    return redirect('listarcalificacion', idsesion=sesion)

@login_required # aqui permite retornar el listado de usuarios para elegir y ver los compromisos
def listar_compromisos(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    usuarios = UserPerfil.objects.filter(idrol=2).exclude(idrol__in=[1, 4])
    formador = ''
    #=====================================================
    if perfil_usuario.idrol.id == 4:
        formador = FormadorEmpresa.objects.get(idusu=perfil_usuario, estado=True)
    return render(request, 'admin/listadousercompromisos.html', {'usu':perfil_usuario, 'usuarios':usuarios, 'formador':formador})

# aqui permite ver los compromisos por cada usuario 
@login_required
def  vercompromisos(request, iduser):
     perfil_usuario = UserPerfil.objects.get(user=request.user)
     usu = UserPerfil.objects.get(id=iduser)
     compromisos = Compromisos.objects.filter(id_usuario=usu)
     estados = EstadoCompromisos.objects.all()
     return render(request, 'admin/usuariocompromiso.html', {'usu':perfil_usuario, 'compromisos':compromisos, 'estados':estados})

#aqui actualiza el compromiso de cada usuario
@login_required
def savecompromiso(request, idcom):
    if request.method == 'POST':
        #obtener estado
        idestado = request.POST.get("estado")
        compromiso = Compromisos.objects.get(id=idcom)
        compromiso.respuesta = request.POST.get("respuesta")
        compromiso.id_estado = EstadoCompromisos.objects.get(id=idestado)
        compromiso.puntaje = request.POST.get("puntaje")
        compromiso.save()
    #====================================================
        #obtener usuario
        comActu = Compromisos.objects.get(id=idcom)
        perfil_usuario = UserPerfil.objects.get(user=request.user)
        usu = UserPerfil.objects.get(id=comActu.id_usuario.id)
        compromisos = Compromisos.objects.filter(id_usuario=usu)
        estados = EstadoCompromisos.objects.all()
        mensaje = "Información ingresada de manera exitosa"
        return render(request, 'admin/usuariocompromiso.html', {'usu':perfil_usuario, 'compromisos':compromisos, 'mensaje':mensaje, 'estados':estados})


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
    return render(request, 'admin/usuariocompromiso.html', {'usu':perfil_usuario, 'compromisos':compromisos, 'mensaje':mensaje, 'estados':estados})

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
def cambiar_pendiente(request, iduser, idsesion):
    if request.method == 'POST':
        usuario = UserPerfil.objects.get(id=iduser)
        pendiente = request.POST.get('selectpendiente')
        usuario.pendiente = pendiente
        usuario.save()
        asistencia = SesionAsistencia.objects.get(idusuario=usuario)
        asistencia.asistencia_pendiente = pendiente
        asistencia.save()
        messages.success(request,"Cambio de estado realizado satisfactoriamente")
        return redirect('listarasistentes', idsesion=idsesion)

#=================Aqui se registra una nueva competencia ================
@login_required  
def crearCompetencia(request):
    competencia = request.POST.get('comp')
    competencia_existente = Competencias.objects.filter(nombre=competencia).exists()
    if competencia_existente:
         mensaje = "Esta competencia ya se encuentra registrada."
         messages.error(request, mensaje)
         return HttpResponseRedirect(reverse('registroCursos'))
    else:
        com = Competencias(nombre=competencia)
        com.save()
        mensaje = "La competencia se ha registrado de manera exitosa"
        messages.error(request, mensaje)
        return HttpResponseRedirect(reverse('registroCursos'))

#==================== eliminar competencia ==================
@login_required  
def eliminarCompetencia(request, idcom):
    competencia = get_object_or_404(Competencias, id=idcom)
    competencia.delete()
    msj = "Competencia eliminada de manera exitosa."
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    competencias = Competencias.objects.all()
    messages.error(request, msj)
    return HttpResponseRedirect(reverse('registroCursos'))
    #return render(request, '', {'usu':perfil_usuario, 'competencias':competencias, 'msj':mensaje})

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
        #===== obtener todas las relaciones ===============
        roles = {role.id: role for role in RolUser.objects.filter(id__in=id_roles)}
        areasn = {area.id: area for area in Area.objects.filter(id__in=id_area)}
        departamentos = {depar.id: depar for depar in Departamento.objects.filter(id__in=id_depar)}
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
                userper = UserPerfil(nombre=row['Nombre'], apellido=row['Apellido'], cedula=row['Cedula'], telefono=row['Telefono'], idrol=roles[row['Idrol']], cargo=row['Cargo'], idarea=idarea, idepart=idep, user=user )
                userper.save()
                mensaje = "Registros importados de manera exitosa!"
            except IntegrityError:
                mensaje = "Error al procesar el registro"
            #======== end registrar ============================
     usuarios = UserPerfil.objects.all() #=== todos los usuarios para listar
     empresa = Empresa.objects.all() #== listado de empresas
     areas = Area.objects.all() 
     depar = Departamento.objects.all()
     rol = RolUser.objects.all()
     formadorempresa = FormadorEmpresa.objects.all()
     return render(request, 'admin/registrouser.html', {'usu':perfil_usuario, 'mensaje':mensaje, 'usuarios':usuarios, 'empresa':empresa, 'areas':areas, 'depar':depar, 'roles':rol, 'formador':formadorempresa})

#================= aqui registrar nuevo usuario =================
@login_required
def addNewUser(request):
    if request.method == 'POST':
       print(request.POST)
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
              if rol_user.id != 4:
                if not idepar:
                    id_area = Area.objects.get(id=idarea)
                    id_depar = None
                else: 
                    id_depar = Departamento.objects.get(id=idepar)
                    id_area = None
                userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['apellido'], cedula=request.POST['ced'], telefono=request.POST['tel'], idrol=rol_user, cargo=cargo_user, idepart=id_depar, idarea=id_area, user=user )
                userper.save()
              else: 
                userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['apellido'], cedula=request.POST['ced'], telefono=request.POST['tel'], idrol=rol_user, cargo=cargo_user, idepart=None, idarea=None, user=user )
                userper.save()
                #============ guardar la relacion de empresa y formador
                formador = FormadorEmpresa(idempresa=id_empresa, idusu=userper)
                formador.save()

              mensajereg = f"El usuario: {userper.user.username}, ha sido registrado exitosamente"
       except IntegrityError:
              mensajereg = "Error: El usuario ya se encuentra registrado."
    messages.error(request, mensajereg)
    return HttpResponseRedirect(reverse('registroUser'))

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
