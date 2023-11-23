import os
import mimetypes
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #sirve para hacer las peticiones
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.contrib import messages #mensajes para la vista
from django.db import IntegrityError #errores de la base de datos
from ..models import UserPerfil, Curso, Sesioncurso, ObjetivosCurso, Area, Departamento, Kpiarea, Kpiobjetivos, EmpresaAreas
from django.contrib import messages #mensajes para la vista
from ..models import TemasSesion, Grupos, GruposCursos, GruposUser
from ..models import TamEmpresa, SectorEmpresa, Empresa, GrupoEmpresa
from django.db.models import Subquery, OuterRef
#Codigo Jhon
from django.http import JsonResponse
from django.views import View
#Fin Codigo Jhon

@login_required #proteger la ruta
def registroCursos(request):
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  if request.method == 'POST':
      #=== Get data lists =======
      print(request.POST)
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
       return render(request, 'admin/listcursos.html', {'usu':perfil_usuario, 'cursos':cursos, 'sesiones':sesiones, 'objetivos':objetivos, 'tematicas':tematicas})
  
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
    #=========== contar los usuarios que pertenecen a este grupo =============
    grupos_con_cursos = {}
    grupos_des = []
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
    
    return render(request, 'admin/listgrupo.html', {'usu':perfil_usuario, 'grupos_con_cursos':grupos_con_cursos, 'grupos_des':grupos_des})

#=============== formulario de crear nuevo grupo con cursos y trabajadores =================
@login_required #proteger la ruta
def creargrupo(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    ngrupos = Grupos.objects.all()
    cursos = Curso.objects.all()
    usuarios = UserPerfil.objects.all()
    if request.method == 'POST':
        ngrupo = request.POST.get('ngrupo')
        cursos_seleccionados = request.POST.getlist('cursosselec')
        usuarios_seleccionados = request.POST.getlist('ususelect')
        # Obtén los objetos de Curso y Grupo
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
        return redirect('creargrupo')
    else:
      return render(request, 'admin/addgrupo.html', {'usu':perfil_usuario, 'ngrupos':ngrupos, 'cursos':cursos, 'usuarios':usuarios})
#======= listado de grupos ============
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
        opciones = list(Grupos.objects.values())
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
                    opciones = list(Grupos.objects.values())
                    return JsonResponse({'message': 'Datos actualizados correctamente.', 'opciones':opciones})             
            else:
                return JsonResponse({'mensaje': 'Los campos no pueden estar vacios'}, status=404) 
        except Grupos.DoesNotExist:
            return JsonResponse({'mensaje': 'No se encontró el objeto con el ID proporcionado.'}, status=404)

# listar los usuarios pertenecientes a un grupo
@login_required #proteger la ruta
def usersgrupo(request, idgrupo):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    regusu = GruposUser.objects.filter(idgrupo=idgrupo)
   # usuarios = UserPerfil.objects.all()
    usuarios = UserPerfil.objects.exclude(
        id__in=Subquery(
            GruposUser.objects.filter(idgrupo=idgrupo).values('iduser')
        )
    )
    print(usuarios)
    return render(request, 'admin/listusergrupo.html', {'usu':perfil_usuario, 'regusu':regusu, 'usuarios':usuarios})
