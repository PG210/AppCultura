from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from appcultura.modelos.calificacionusuarios import CalificacionUsuarios
from appcultura.modelos.compromisos import Compromisos
from appcultura.modelos.personas_compromiso import PersonasCompromisos
from appcultura.modelos.preguntasform import Preguntas
from appcultura.modelos.respuestasformulario import RespuestaForm
from appcultura.modelos.sesionasistencia import SesionAsistencia
from appcultura.modelos.sesionformulario import SesionFormulario
from appcultura.viewfile.viewuser import calificacionCurso #sirve para hacer las peticiones
from .models import RolUser
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate #crea la sesion de un usuario al registrarse
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.db import IntegrityError #errores de la base de datos
from .models import UserPerfil, GruposUser, Sesioncurso, GruposCursos
from django.utils import timezone
from django.db.models import Q


# Create your views here.
#vista para home
def home(request):
 #return render(request, 'home.html') # retorma la vista competa
    return render(request, 'layoutsinicio/login.html') 

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
    #return redirect('home')
    return render(request, 'layoutsinicio/login.html') 

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
#================ funcion para retornar los valores de grafica de torta en la ultima asistencia registrada ===
def ultimaAsistencia(idusuario):
    valorc1, valorc2, valorc3 = 0, 0, 0
    asistencia = SesionAsistencia.objects.filter(idusuario=idusuario).order_by('-fecha_asistencia').first()
    if asistencia:
        idcurso = asistencia.idsesioncurso.idcurso.id
        totalsesiones = Sesioncurso.objects.filter(idcurso=idcurso)
        sumaplicabilidad, sumclaridad, sumrelevancia = 0, 0, 0
        valorescurso = ''
        datos = []
        #=== obtener el total de calificaciones por sesion =========
        for sesion in totalsesiones:
            datos_sesion = CalificacionUsuarios.objects.filter(id_sesiones_curso=sesion)
            datos.extend(datos_sesion)

        #====== obtener porcentajes ===================
        if datos:
            for dat in datos:  
                sumaplicabilidad += dat.aplicabilidad  # Sumar aplicabilidad
                sumclaridad += dat.claridad # sumar el total de claridad
                sumrelevancia += dat.relevancia # sumar relevancia
            num_sesiones = (5*len(datos))
            promaplicabilidad = (sumaplicabilidad/num_sesiones)*100
            promclaridad = (sumclaridad/num_sesiones)*100
            promrlevancia = (sumrelevancia/num_sesiones)*100
            #====== calcular valores de porcentaje =======
            totcurso = promaplicabilidad + promclaridad + promrlevancia
            valorc1 = round((promrlevancia/totcurso) * 100, 2)
            valorc2 = round((promclaridad/totcurso) * 100, 2)
            valorc3 = round((promaplicabilidad/totcurso) * 100, 2)
    valorescurso = {'curso':asistencia, 'valorc1': valorc1, 'valorc2': valorc2, 'valorc3': valorc3}
    return valorescurso
#======== funcion para no asistencias ==================
def verificarasis(asistencias):
    sesiones_faltantes = []
    for asis in asistencias:
        asistencias_sesion = SesionAsistencia.objects.filter(idsesioncurso=asis)
        if not asistencias_sesion.exists():
            sesiones_faltantes.append(asis)
    totfaltantes =  len(sesiones_faltantes)
    valorasis = {'faltantes':sesiones_faltantes, 'totfaltantes':totfaltantes}
    return valorasis
#========================================================
@login_required #proteger la ruta
def administracion(request):
  #usuario_logeado = request.user #obtener el usuario logeado
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  nombre_cargo = perfil_usuario.cargo
  fecha_hoy = timezone.now()
  sesiones_anteriores, sesiones, noasis = '', '', ''
  
  valorasis, porasis, formpendientes, porform = 0, 0, 0, 0
  if perfil_usuario.idrol.id == 2:
      #=== consultar las sesiones ===
      grupouser = GruposUser.objects.filter(iduser=perfil_usuario.id)
      if grupouser:
         for grupo_usuario in grupouser:
             grupocurso = GruposCursos.objects.filter(idgrupo=grupo_usuario.idgrupo)
             for grupo_curso in grupocurso:
                #sesionestot = Sesioncurso.objects.filter(idcurso=grupo_curso.idcurso)
                sesiones = Sesioncurso.objects.filter(idcurso=grupo_curso.idcurso, fechainicio__gt=fecha_hoy)
                sesiones_anteriores = Sesioncurso.objects.filter(idcurso=grupo_curso.idcurso, fechainicio__lt=fecha_hoy)     
      #====== asistencias anteriores======================
      if sesiones_anteriores:
         noasis = verificarasis(sesiones_anteriores)
      #=============== sesion asistencia ==================
      asistencia = SesionAsistencia.objects.filter(idusuario=perfil_usuario)
      totalasis = asistencia.count()
      #======= calcular el porcentaje de asistencia solamente para fechas pasadas =========
      if noasis:
         valorasis = (totalasis + noasis.get('totfaltantes'))
         porasis = (totalasis*100)/(valorasis)
      #======== buscar formularios contestados ==============
      formularios = Preguntas.objects.filter(respuestaform__iduser=perfil_usuario).values('idform').distinct()
      totalforms = formularios.count() 
      #======= formularios totales ================
      total_formularios = 0
      formtotal = []
      sesion = []
      for st in sesiones_anteriores: #solamente recorre las sesiones que ya pasaron
          formtotal_sesion = SesionFormulario.objects.filter(idsesion=st.id)
          sesionval = SesionFormulario.objects.filter(idsesion=st.id).values('idsesion').distinct()
          total_formularios += formtotal_sesion.count()
          formtotal.extend(formtotal_sesion)
          sesion.extend(sesionval)

      #========= obtener los formularios pendientes ==========
      if total_formularios != 0:
          formpendientes = total_formularios-totalforms
          porform = (totalforms*100)/(total_formularios)
      #=========== compromisos ==============================
      compromisos = Compromisos.objects.filter(id_usuario=perfil_usuario)
      totcompromisos = compromisos.count()
      total_pendientes = 0
      total_cumplido =0
      total_nocumplido, porcomp = 0, 0
      for comp in compromisos:
          if comp.id_estado.id == 1:
              total_cumplido += 1
          elif comp.id_estado.id == 2:
              total_pendientes += 1
          elif comp.id_estado.id == 3:
              total_nocumplido += 1
      if totcompromisos != 0:
         porcomp = (total_cumplido*100)/(totcompromisos)
      #======= obtener las metricas de un solo curso ======
      valorescurso = ultimaAsistencia(perfil_usuario)
      #=============== aqui se envian los datos =========
      context = {
        'usu':perfil_usuario,
        'cargo':nombre_cargo,
        'sesiones':sesiones,
        'tasis':totalasis,
        'asistencia': asistencia,
        'totalasis':valorasis,
        'porasis':porasis,
        'porasis': porasis,
        'totforms': totalforms,
        'formtotal': total_formularios,
        'formpendientes': formpendientes,
        'porform': porform,
        'sesion': sesion, 
        'totcompromisos': totcompromisos,
        'total_cumplido': total_cumplido,
        'total_pendientes': total_pendientes,
        'total_nocumplido': total_nocumplido,
        'porcomp': porcomp,
        'compromisos': compromisos,
        'valorescurso': valorescurso,
        'noasis': noasis
      }
      return render(request, 'user/dashboard.html', context)
  else:
      return render(request, 'admin/inicio.html', {'usu':perfil_usuario, 'cargo':nombre_cargo})


 
  