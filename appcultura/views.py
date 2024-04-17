from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from appcultura.modelos.calificacionformador import CalificacionFormador
from appcultura.modelos.calificacionusuarios import CalificacionUsuarios
from appcultura.modelos.compromisos import Compromisos
from appcultura.modelos.cursos import Curso
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
from django.db.models import Q, Sum
from collections import defaultdict


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
def ultimaAsistencia(idcurso):
    valorc1, valorc2, valorc3 = 0, 0, 0
    vfclaridad, vfcapacidad, vfdominio = 0, 0, 0
    asistencia = ''
    totalsesiones = Sesioncurso.objects.filter(idcurso=idcurso)
    sumaplicabilidad, sumclaridad, sumrelevancia, fclaridad, fcapacidad, fdominio = 0, 0, 0, 0, 0, 0
    valorescurso = ''
    datos = []
    calif_formador = []
        #=== obtener el total de calificaciones por sesion =========
    for sesion in totalsesiones:
        datos_sesion = CalificacionUsuarios.objects.filter(id_sesiones_curso=sesion)
        datos.extend(datos_sesion)
        #========== datos para formador ==================
        datos_formador = CalificacionFormador.objects.filter(sesion_curso=sesion)
        calif_formador.extend(datos_formador)
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
        #=================== valores para usuario ===================
        if calif_formador:
            for info in calif_formador:
                fclaridad += info.claridad  # Sumar claridad
                fcapacidad += info.capacidad # sumar capacidad
                fdominio += info.dominio # sumar relevancia
            num_sesiones_formador = (5*len(calif_formador))
            promfclarida = (fclaridad/num_sesiones_formador)*100
            promfcapacidad = (fcapacidad/num_sesiones_formador)*100
            promfdominio = (fdominio/num_sesiones_formador)*100
            #====== calcular valores de porcentaje =======
            totformador = promfclarida + promfcapacidad + promfdominio
            vfclaridad = round((promfclarida/totformador) * 100, 2)
            vfcapacidad = round((promfcapacidad/totformador) * 100, 2)
            vfdominio = round((promfdominio/totformador) * 100, 2)
        #=============================================================
    valorescurso = {
        'curso':asistencia,
        'valorc1': valorc1, 
        'valorc2': valorc2, 
        'valorc3': valorc3,
        'vfclaridad': vfclaridad, 
        'vfcapacidad': vfcapacidad,
        'vfdominio': vfdominio

        }
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
#=========== buscar los cursos totales apara el admin =============
def totalasistencias_admin(curso):
    total_asistencias, total_users, faltas, porasis, porfaltas, portotal = 0, 0, 0, 0, 0, 0
    sesiones = Sesioncurso.objects.filter(idcurso=curso)
    #======= obtener el numero de asistencias del curso ============
    for nsesion in sesiones:
         asistencia = SesionAsistencia.objects.filter(idsesioncurso=nsesion).count()
         total_asistencias += asistencia
    #====== obtener el total colaboradores en el curso ===================
    grupos = GruposCursos.objects.filter(idcurso=curso)
    for ngrupos in grupos:
        n_user = GruposUser.objects.filter(idgrupo=ngrupos.idgrupo).count()
        total_users += n_user
    #====== faltas =========
    faltas = total_users - total_asistencias
    if total_users != 0:
        porasis = round(total_asistencias*100/total_users, 1)
        porfaltas = round(faltas*100/total_users, 1)
        portotal = round(total_users*100/total_users, 1)
    #======= datos =====
    datos_funcion = {
        'total_asistencias': total_asistencias,
        'total_users': total_users,
        'faltas': faltas,
        'porasis': porasis,
        'porfaltas': porfaltas,
        'portotal': portotal,
        'curso': curso
    }
    return datos_funcion

#============== funcion para retornar las sesiones que faltan ============
def sesionesproximas():
    fecha_hoy = timezone.now()
    sesiones = Sesioncurso.objects.filter(fechainicio__gt=fecha_hoy)
    return sesiones
#=============== funcion para retornar los formularios contestados ============
def formulariosCompletos(curso):
    formularios, totform, falta, porcom, porfalta, portotal  = 0, 0, 0, 0, 0, 0
    sesiones = Sesioncurso.objects.filter(idcurso=curso)
    for sesion in sesiones:
        formu = RespuestaForm.objects.filter(idsesion=sesion.id).values('iduser').distinct().count()
        formularios += formu
    #==== total de formularios =====
    grupos = GruposCursos.objects.filter(idcurso=curso)
    for ngrupos in grupos:
        n_user = GruposUser.objects.filter(idgrupo=ngrupos.idgrupo).count()
        totform += n_user
    falta = totform - formularios #=== formularios faltantes por responder
    if totform != 0:
        porcom = round(formularios*100/totform, 1)
        porfalta = round(falta*100/totform, 1)
        portotal = round(totform*100/totform, 1)
    datos = {
        'completados': formularios,
        'total': totform,
        'falta': falta,
        'porcom': porcom,
        'porfalta': porfalta,
        'portotal': portotal,
        'curso': curso
    }
    return datos
#=====================================================================
def agrupar_datos_grafico(total_por_usuario):
    rangos = {'0% - 25%': 0, '26% - 50%': 0, '51% - 75%': 0, '76% - 100%': 0}
    for valor in total_por_usuario.values():
        if valor >= 0 and valor <= 25:
            rangos['0% - 25%'] += 1
        elif valor >= 26 and valor <= 50:
            rangos['26% - 50%'] += 1
        elif valor >= 51 and valor <= 75:
            rangos['51% - 75%'] += 1
        elif valor >= 76 and valor <= 100:
            rangos['76% - 100%'] += 1
    return rangos
#========== funcion para encontrar la calificacion en rangos =========
def calificaciones_admin(curso):
    total_por_usuario = defaultdict(int)  # Diccionario con valor inicial 0 para cada usuario
    formu = []
    valor_total = 0
    sesiones = Sesioncurso.objects.filter(idcurso=curso)
    grupos = GruposCursos.objects.filter(idcurso=curso)

    #======== obtener el valor total de los formularios ==================
    for ses in sesiones:
        formu_unit = SesionFormulario.objects.filter(idsesion=ses.id)
        if formu_unit:
           formu.extend(formu_unit)
   
    for formulario in formu:
        valor_form = Preguntas.objects.filter(idform=formulario.idform).aggregate(total=Sum('valor'))['total']
        valor_total += valor_form #=== aqui valor de todos los formularios asignados al curso
    #========================================================================================
    for grupo in grupos:
        usuarios_grupo = GruposUser.objects.filter(idgrupo=grupo.idgrupo.id).values_list('iduser', flat=True)
        
        for usuario_id in usuarios_grupo:
            for sesion in sesiones:
                respuestas_usuario = RespuestaForm.objects.filter(idsesion=sesion.id, iduser=usuario_id)
                total_usuario = respuestas_usuario.aggregate(total=Sum('valores'))['total'] or 0
                if valor_total != 0:
                   total_por_usuario[usuario_id] += round((total_usuario*100)/valor_total,0)

    #================= agrupar los datos =========================
    datos_mayor_a_20 = {clave: valor for clave, valor in total_por_usuario.items() if valor > 20}
    datos_ordenados = sorted(datos_mayor_a_20.items(), key=lambda x: x[1], reverse=True)
    primeros_valores = datos_ordenados[:10]
    
    #========= funcion para grafico =============================
    datos = agrupar_datos_grafico(total_por_usuario)
    valor1 = datos['0% - 25%']
    valor2 = datos['26% - 50%']
    valor3 = datos['51% - 75%']
    valor4 = datos['76% - 100%']
    valores = {
        'valor1': valor1,
        'valor2': valor2,
        'valor3': valor3,
        'valor4': valor4,
        'primeros_valores': primeros_valores
    }
    return valores
#================== valores de compromisos admin===============
def funcioncompromisos(curso):
    comusu = []
    sesiones = Sesioncurso.objects.filter(idcurso=curso)
    total_cumplido, total_pendiente, total_incum = 0, 0, 0
    for sesion in sesiones:
        #================= compromisos cumplidos ===========
        cumplido_conta = Compromisos.objects.filter(id_estado=1, id_sesion=sesion.id).count()
        total_cumplido += cumplido_conta
        #================= compromisos pendientes ===========
        pendiente_conta = Compromisos.objects.filter(id_estado=2, id_sesion=sesion.id).count()
        total_pendiente += pendiente_conta
        #================== compromisos no cumplidos ===========
        incumplido_conta = Compromisos.objects.filter(id_estado=3, id_sesion=sesion.id).count()
        total_incum += incumplido_conta
        #==== compromisos =================
        usuarios = Compromisos.objects.filter(id_sesion=sesion.id)
        comusu.extend(usuarios)
    compromiso = {
        'cumplidos': total_cumplido,
        'pendiente': total_pendiente,
        'incumplido': total_incum,
        'comusu': comusu
    }

    return compromiso
#============================= compromisos user =================
def compromisosUser(perfil_usuario):
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
      datos = {
        'totcompromisos': totcompromisos,
        'total_cumplido': total_cumplido,
        'total_pendientes': total_pendientes,
        'total_nocumplido': total_nocumplido,
        'porcomp': porcomp,
        'compromisos': compromisos,
      }
      return datos   
#======================= obtener asistencias y formularios ==========
def infoUser(perfil_usuario):
      fecha_hoy = timezone.now()
      valorasis, porasis, formpendientes, porform = 0, 0, 0, 0
      sesiones_anteriores, sesiones, noasis = '', '', ''
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
      #============ datos ============
      datos = {
        'sesiones':sesiones,
        'tasis':totalasis,
        'asistencia': asistencia,
        'totalasis':valorasis,
        'porasis':porasis,
        'totforms': totalforms,
        'formtotal': total_formularios,
        'formpendientes': formpendientes,
        'porform': porform,
        'sesion': sesion, 
        'noasis': noasis,
        'grupocurso': grupocurso
      }
      return datos 
#========================================================
@login_required #proteger la ruta
def administracion(request):
  #usuario_logeado = request.user #obtener el usuario logeado
  perfil_usuario = UserPerfil.objects.get(user=request.user)
  nombre_cargo = perfil_usuario.cargo
  
  cursos = Curso.objects.all() #===== cursos para filtro
  if perfil_usuario.idrol.id == 2:
      #=== consultar las sesiones ===
      info_user = infoUser(perfil_usuario)
      #=========== compromisos ==============================
      compromisos_user = compromisosUser(perfil_usuario)
      #======= obtener las metricas de un solo curso ======
      asistencia_user = SesionAsistencia.objects.filter(idusuario=perfil_usuario.id).order_by('-fecha_asistencia').first()
      idcurso = asistencia_user.idsesioncurso.idcurso
      valorescurso = ultimaAsistencia(idcurso)
      #=============== aqui se envian los datos =========
      context = {
        'usu':perfil_usuario,
        'cargo':nombre_cargo,
        'valorescurso': valorescurso,
        'curso': asistencia_user,
        'cursos': cursos, #=== filtrar
        'compromisos': compromisos_user,
        'info': info_user
      }
      return render(request, 'user/dashboard.html', context)
  else:
      #======= buscar el ultimo registro =========
      ultimo_dato = SesionAsistencia.objects.order_by('-fecha_asistencia').first()
      users = UserPerfil.objects.all()
      curso = ultimo_dato.idsesioncurso.idcurso
      asisadmin = totalasistencias_admin(curso)
      proximas_sesiones = sesionesproximas()
      formularios = formulariosCompletos(curso) #== obtiene los formularios de un curso
      calificacion = calificaciones_admin(curso) #===== mostrar las calificaciones para grafica
      calificacioncurso = ultimaAsistencia(curso) #==== mostrar grafica de aceptacion
      compromisosadmin = funcioncompromisos(curso) #========= obtener datos para compromisos
      
      datos = {
          'usu': perfil_usuario,
          'cargo': nombre_cargo,
          'asisadmin': asisadmin,
          'cursos': cursos,
          'sesiones': proximas_sesiones,
          'formularios': formularios,
          'calificacion': calificacion,
          'users': users,
          'calificacioncurso': calificacioncurso,
          'compromisos': compromisosadmin
      }
      return render(request, 'admin/dashboard.html', datos)


 #================== funcion para filtrar cursos ==========
@login_required #proteger la ruta
def filtrarcurso(request, idcurso):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    nombre_cargo = perfil_usuario.cargo
    cursos = Curso.objects.all()
    if perfil_usuario.idrol.id == 1:
        users = UserPerfil.objects.all()
        curso = Curso.objects.get(id=idcurso)
        proximas_sesiones = sesionesproximas()
        asisadmin = totalasistencias_admin(curso)
        formularios = formulariosCompletos(curso) #== obtiene los formularios de un curso
        calificacion = calificaciones_admin(curso) #===== mostrar las calificaciones para grafica
        calificacioncurso = ultimaAsistencia(curso) #==== mostrar grafica de aceptacion
        compromisosadmin = funcioncompromisos(curso) #========= obtener datos para compromisos
        datos = {
            'usu': perfil_usuario,
            'cargo': nombre_cargo,
            'asisadmin': asisadmin,
            'cursos': cursos,
            'sesiones': proximas_sesiones,
            'formularios': formularios,
            'calificacion': calificacion,
            'users':users,
            'calificacioncurso': calificacioncurso,
            'compromisos': compromisosadmin
        }
        return render(request, 'admin/dashboard.html', datos)
    else:
        #=========== compromisos ==============================
        compromisos_user = compromisosUser(perfil_usuario)
        #=== consultar las sesiones ===
        info_user = infoUser(perfil_usuario)
        valorescurso = ultimaAsistencia(idcurso)
        curso_user = Curso.objects.get(id=idcurso)
        context = {
        'usu':perfil_usuario,
        'cargo':nombre_cargo,
        'info': info_user,
        'cursos': cursos, #=== filtrar
        'compromisos': compromisos_user,
        'valorescurso': valorescurso,
        'curso':curso_user
       }
        return render(request, 'user/dashboard.html', context)

  