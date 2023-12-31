from ast import Delete
from email import message
import os
import mimetypes
from pdb import post_mortem
import select
from urllib import request
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

from appcultura.modelos.calificacionusuarios import CalificacionUsuarios
from appcultura.modelos.compromisos import Compromisos
from appcultura.modelos.estado_compromisos import EstadoCompromisos #errores de la base de datos
from ..models import UserPerfil, Curso, Sesioncurso, ObjetivosCurso, Area, Departamento, Kpiarea, Kpiobjetivos, EmpresaAreas
from django.contrib import messages #mensajes para la vista
from ..models import TemasSesion, Grupos, GruposCursos, GruposUser, Competencias, CompetenciaCurso
from ..models import TamEmpresa, SectorEmpresa, Empresa, GrupoEmpresa, Cargo
from django.db.models import Subquery, OuterRef, Q
from ..models import TamEmpresa, SectorEmpresa, Empresa, GrupoEmpresa, SesionAsistencia, RolUser
from django.db.models import Subquery, OuterRef

#Codigo Jhon
from django.http import JsonResponse
from django.views import View
from django.http import JsonResponse
from django.core.serializers import serialize

from appcultura.viewfile.fadmin.functionadmin import generar_qr
#Fin Codigo Jhon

@login_required #proteger la ruta
def registroCursos(request):
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  competencias = Competencias.objects.all()
  if request.method == 'POST':
      #=== Get data lists =======
      print(request.POST)
      fechas_inicio = request.POST.getlist('fecha_inicio[]')
      fechas_final = request.POST.getlist('fecha_final[]')
      lugares = request.POST.getlist('lugar[]')
      descripciones = request.POST.getlist('desobj[]')
      competencias = request.POST.getlist('competencias[]')
      compe = request.POST.getlist('compe')
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
            regsesion = Sesioncurso(fechainicio=fecha_inicio, fechafin=fecha_final, lugar=lugar, estado=1, idcurso=idcurso)
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
      return render(request, 'admin/addcurso.html', {'usu':perfil_usuario, 'msj':mensaje, 'competencias':competencias})
  else:
      return render(request, 'admin/addcurso.html', {'usu':perfil_usuario, 'competencias':competencias})

#Rergistro de Empresas
@login_required
def registroEmpresa(request):
    grupem = Empresa.objects.all()
    sec = SectorEmpresa.objects.all()
    varible = TamEmpresa.objects.all()
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    if request.method == 'POST':
        #=== Get data lists =======
        #Guardar empresa principal
        nombre = request.POST['nameEmp']
        nit = request.POST['nit']
        direction = request.POST['direccion']
        email = request.POST['correo']
        phone = request.POST['telefono']

        if not any(nombre) or not any(nit) or not any(direction) or not any(email) or not any(phone):
            mensaje = "Los campos no pueden quedar vacios"
            return render(request, 'admin/addempresa.html', {'usu':perfil_usuario, 'tamempresa':varible, 'secEmp':sec, 'grp':grupem, 'mensaje':mensaje})
        
        if Empresa.objects.filter(nit=nit).exists():
            mensaje = "La empresa ya se encuentra registrada"
            return render(request, 'admin/addempresa.html', {'usu':perfil_usuario, 'tamempresa':varible, 'secEmp':sec, 'grp':grupem, 'mensaje':mensaje})
        
        regEmpresa = GrupoEmpresa(nombre=nombre, nit=nit, direccion=direction, correo=email, telefono=phone)
        regEmpresa.save()
        mensaje = "Empresa Registrada exitosamente"
        #Fin guardar empresa principal

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

        

        if any(nameSuc) or any(nitSuc) or any(dirSuc) or any(correoSuc) or any(telSuc) or any(secSuc) or any(tamSuc):
            empresas_sucursales = []
            idempresa = GrupoEmpresa.objects.get(id=regEmpresa.id)
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
    
        return render(request, 'admin/addempresa.html', {'usu':perfil_usuario, 'tamempresa':varible, 'secEmp':sec, 'grp':grupem, 'mensaje':mensaje})
    else:
        return render(request, 'admin/addempresa.html', {'usu':perfil_usuario, 'tamempresa':varible, 'secEmp':sec, 'grp':grupem})

        #Fin Guardar Empresa Sucursal

#Vista para listar cursos
@login_required #proteger la ruta
def listarcursos(request):
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  if request.method == 'GET':
       cursos = Curso.objects.all()
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
        '''
        if request.POST.getlist('desobj[]'):
            desobj_list = request.POST.getlist('desobj[]')
            compobj_list = request.POST.getlist('competencias[]')
            for desobj, compobj in zip(desobj_list, compobj_list):
                ObjetivosCurso.objects.create(descrip=desobj, competencias=compobj, idcurso=curso)
        '''
        
        #En caso de que exista una fecha de inicio nueva
        '''
        if request.POST.getlist('fecha_inicio[]'):
            fec_inicio_list = request.POST.getlist('fecha_inicio[]')
            fec_fin_list = request.POST.getlist('fecha_final[]')
            lugar_list = request.POST.getlist('lugar[]')
            tema_list = request.POST.getlist('tema[]')
            desc_tema_list = request.POST.getlist('descripcion[]')
            recursos_list = request.POST.getlist('recursos[]')
            if request.POST.getlist('archivo[]')[0] != '':
                archivo = request.POST.getlist('archivo[]')
                fs = FileSystemStorage(location=os.path.join(settings.STATIC_ROOT, 'archivos')) 
                nombre_archivo = fs.save(archivo.name, archivo)
                ruta_destino = fs.url(nombre_archivo)
            else:
                ruta_destino = None

            for fec_inicio, fec_fin, lugar in zip(fec_inicio_list, fec_fin_list, lugar_list):
                sesionescurso = Sesioncurso.objects.create(fechainicio=fec_inicio, fechafin=fec_fin, lugar=lugar, idcurso=curso)

            for temas, desc_tema, recursos_tema in zip(tema_list, desc_tema_list, recursos_list):
                TemasSesion.objects.create(descrip=temas, competencias=desc_tema, recursos=recursos_tema, ruta=ruta_destino, idsesion=sesionescurso)
        '''
        
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
        gropemp = request.POST.get('groupEmp')
        sec = request.POST.get('sector')
        tam = request.POST.get('tamanioEmp')

        empresa.idgrupoem = GrupoEmpresa.objects.get(id=gropemp)
        empresa.idsector = SectorEmpresa.objects.get(id=sec)
        empresa.idtam = TamEmpresa.objects.get(id=tam)
        empresa.save()
        messages.success(request, 'Empresa actualizada exitosamente.')
        return redirect('listarempresa')
    else:
        return render(request, 'admin/updateempresa.html', {'usu':perfil_usuario, 'empresa':empresa, 'sector':sector, 'grpEmp':grpEmp, 'tamint':tamint})

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
        cargo = Cargo.objects.all()
        depars = Departamento.objects.all()
        areas =Area.objects.all()
        return render(request, 'admin/addgrupo.html', {'usu':perfil_usuario, 'ngrupos':grupos_faltantes, 'cursos':cursos, 'usuarios':usuarios, 'rol':rol, 'empresa':empresa, 'cargo':cargo, 'depars':depars, 'areas':areas})
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
       cargo = Cargo.objects.all()
       depars = Departamento.objects.all()
       areas =Area.objects.all()
       #============ solamente obtener los grupos que no tienen ningun curso o usuario vinculado =============
       grupos_faltantes = ngrupos.exclude(
            Q(gruposuser__in=addgrupouser) | Q(gruposcursos__in=addgrupocurso)
        )
       #===========guardar usuario nuevo ======================
       user = User.objects.create_user(username=request.POST['email'], 
       password=request.POST['ced'])
       user.save()
       #========= guardar en userperfil =================
       user_id = User.objects.latest('id').id
       user_n = User.objects.get(id=user_id)
       id_rol = request.POST['rol']
       rol_user = RolUser.objects.get(id=id_rol)
       id_cargo = request.POST['cargo']
       cargo_user = Cargo.objects.get(id=id_cargo)
       id_empresa = Empresa.objects.get(id=request.POST['empresa'])
       id_area = request.POST['area']
       area_iden = Area.objects.get(id=id_area)
       idpear = request.POST['depar'] # aqui cambia a none si es vacia
       id_depar = Departamento.objects.get(id=idpear)
       if idpear is not None and idpear != '':
           try:
               empresa_user = EmpresaAreas.objects.get(idempresa=id_empresa, idarea=area_iden, idepar=id_depar)
               userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['ape'], cedula=request.POST['ced'], idrol=rol_user, idcargo=cargo_user, idempresa=empresa_user, user=user_n)
               userper.save()
           except EmpresaAreas.DoesNotExist:
               crearrelacion = EmpresaAreas(idempresa=id_empresa, idarea=area_iden, idepar=id_depar)
               crearrelacion.save()
               #========== guardar datos de usuario
               userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['ape'], cedula=request.POST['ced'], idrol=rol_user, idcargo=cargo_user, idempresa=crearrelacion, user=user_n)
               userper.save()
       else:
           try:
               empresa_user = EmpresaAreas.objects.get(idempresa=id_empresa, idarea=area_iden,  idepar__isnull=True)
               userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['ape'], cedula=request.POST['ced'], idrol=rol_user, idcargo=cargo_user, idempresa=empresa_user, user=user_n)
               userper.save()
           except EmpresaAreas.DoesNotExist:
               crearrelacion = EmpresaAreas(idempresa=id_empresa, idarea=area_iden)
               crearrelacion.save()
               #======= guardar datos==========
               userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['ape'], cedula=request.POST['ced'], idrol=rol_user, idcargo=cargo_user, idempresa=crearrelacion, user=user_n)
               userper.save()
       #================ buscar el id de la empresa ===================
       mensaje = "Usuario guardado de manera exitosa."
       messages.info(request, mensaje)
       return render(request, 'admin/addgrupo.html', {'usu':perfil_usuario, 'ngrupos':grupos_faltantes, 'cursos':cursos, 'usuarios':usuarios, 'rol':rol, 'empresa':empresa, 'cargo':cargo, 'depars':depars, 'areas':areas})
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
def vincularareadepto(request):
    empresa = Empresa.objects.all()
    areas = Area.objects.all()
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    if request.method == 'POST':
        selectemp = request.POST.get('selectEmp')
        namearea = request.POST.get('namearea')
        descarea = request.POST.get('descripcionarea')
        namedepto = request.POST.getlist('nomdepto[]')
        desdepto = request.POST.getlist('desdepto[]')
        Departamentos = []
        vinculos = []

        #Guardar data de areas
        area = Area(nombre=namearea, descrip=descarea)
        area.save()

        #Guardar data de Departamentos
        if any(namedepto) or any(desdepto):
            for i in range(len(namedepto)):
                deptolist = Departamento(
                    nombre = namedepto[i],
                    descrip = desdepto[i]
                )
                Departamentos.append(deptolist)
            Departamento.objects.bulk_create(Departamentos)

        #Vincular data de Areas y Departamentos a Empresa
        depto = Departamento.objects.filter(nombre__in=namedepto)
        emp = Empresa.objects.get(id=selectemp)
        id_area = Area.objects.get(nombre=namearea)
        print("variable", emp)
        if any(namedepto) or any(desdepto):
            for i in range (len(namedepto)):
                vinculolist = EmpresaAreas(
                    idempresa = emp,
                    idarea = id_area,
                    idepar = depto[i]
                )
                vinculos.append(vinculolist)
            EmpresaAreas.objects.bulk_create(vinculos)
            mensaje = "Areas y departamentos vinculados satisfactoriamente"
            return render(request, 'admin/vincularareadepartamento.html', {'usu':perfil_usuario, 'empresa':empresa, 'mensaje':mensaje, 'areas':areas})
        else:
            vincular = EmpresaAreas(idempresa=emp, idarea=id_area)
            vincular.save()
            mensaje = "Areas vinculadas satisfactoriamente"
        return render(request, 'admin/vincularareadepartamento.html', {'usu':perfil_usuario, 'empresa':empresa, 'mensaje':mensaje, 'areas':areas})
    else:
        return render(request, 'admin/vincularareadepartamento.html', {'usu':perfil_usuario, 'empresa':empresa, 'areas':areas})

@login_required
def visualizarAreaDepto(request):
    print(request.POST)
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    empresa = Empresa.objects.all()
    if request.method == 'POST':
        selecarea = request.POST.get('selectEmp')
        areas = EmpresaAreas.objects.filter(idempresa=selecarea)
        print(areas)
        return render(request, 'admin/listvinculacion.html',{'usu':perfil_usuario, 'empresa':empresa, 'areas':areas})
    else:
        return render(request, 'admin/listvinculacion.html',{'usu':perfil_usuario, 'empresa':empresa})

@login_required
def eliminavinculo(request, idarea):
    try:
        emp = EmpresaAreas.objects.get(id=idarea)
        emp.delete()
        messages.success(request, 'Vinculacion eliminada exitosamente.')
    except Empresa.DoesNotExist:
        messages.error(request, 'La Vinculacion no Existe')
    return redirect('visualizarAreaDepto')

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
                
                '''
                for curso in cursos:
                    for grupo in grupos:
                        if grupo.idgrupo == curso.idgrupo:
                            verificar=True
                '''
  
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
    #=====================================================
    return render(request, 'admin/listadousercompromisos.html', {'usu':perfil_usuario, 'usuarios':usuarios})

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
            #id_cargo = request.POST['cargo']
            cargo_user = Cargo.objects.get(id=1)
            #id_empresa =  request.POST['empresa']
            empresa_user = EmpresaAreas.objects.get(id=1)
            userper = UserPerfil(nombre=request.POST['nombre'], apellido=request.POST['apellido'], telefono=request.POST['telefono'], cedula=request.POST['cedula'], idrol=rol_user, idcargo=cargo_user, idempresa=empresa_user, user=user, pendiente=True )
            userper.save()
            sesion = Sesioncurso.objects.get(id=idsesion)
            grupo = GruposCursos.objects.filter(idcurso=sesion.idcurso).first()
            ingreso_grupo = GruposUser(idgrupo=grupo.idgrupo, iduser=userper, )
            ingreso_grupo.save()

            asistencia = SesionAsistencia(idsesioncurso=sesion, idusuario=userper, asistencia_pendiente=True)
            asistencia.save()
            messages.success(request,"Usuario guardado y validado satisfactoriamente")
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
    if request.method == 'POST':
        competencia = get_object_or_404(Competencias, id=idcom)
        competencia.delete()
        mensaje = "Competencia eliminada de manera exitosa."
        perfil_usuario = UserPerfil.objects.get(user=request.user)
        competencias = Competencias.objects.all()
        return render(request, 'admin/addcurso.html', {'usu':perfil_usuario, 'competencias':competencias, 'msj':mensaje})
        