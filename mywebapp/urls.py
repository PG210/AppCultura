"""mywebapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path
from appcultura import views
from appcultura.viewfile import viewadmin #utilizar una nueva vista 
from appcultura.viewfile import viewformu #crear formularios
from appcultura.viewfile import viewuser, viewformador #Utilizar la vista de usuario

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  #pagina inicial
    path('login/user/', views.loginuser, name='loginuser'),  #login
    path('logout/', views.singout, name='logout'), # cerrar sesion
    path('reg/user/', views.reguser, name='reguser'),  #registrar user
    
    #========= agregar nuevo usuario desde el admin ==============
    path('administracion/save/nuevo/user/', viewadmin.saveusernuevo, name='saveusernuevo'),
    #=========================================================
    path('administracion/', views.administracion, name='administracion'),  #panel de administrador
    path('administracion/curso/', viewadmin.registroCursos, name='registroCursos'),  #registro curso
    path('administracion/curso/list/', viewadmin.listarcursos, name='listarcursos'),  #registro cursos
    path('administracion/curso/delete/<int:idcurso>/', viewadmin.eliminarcurso, name='eliminarcurso'),  # eliminar cursos
    path('administracion/curso/editar/<int:idcurso>/', viewadmin.editarcurso, name='editarcurso'),  # editar curso
    path('administracion/curso/competencia/', viewadmin.crearCompetencia, name='crearCompetencia'),
    path('administracion/curso/competencia/delete/<int:idcom>/', viewadmin.eliminarCompetencia, name='eliminarCompetencia'),
    
    #==============descargar archvios ===========
    path('administracion/curso/descarga/<path:ruta>/', viewadmin.download, name='download'), 
    #==============================
    path('administracion/kpis/', viewadmin.kpiarea, name='kpiarea'),  # Crear KPI para area y departamento
    path('administracion/kpis/list/', viewadmin.listarkpiarea, name='listarkpiarea'),  # Crear KPI para area y departamento
    path('administracion/kpis/editar/<int:idkpi>/', viewadmin.editarkpi, name='editarkpi'),  # editar curso
    path('administracion/kpis/delete/<int:idkpi>/', viewadmin.eliminarkpi, name='eliminarkpi'),  # eliminar cursos
    path('administracion/kpis/estado/<int:idkpi>/', viewadmin.desactivarkpi, name='desactivarkpi'), # activar o desactivar el kpi
    path('administracion/kpis/select/', viewadmin.selectEmpresa, name='selectEmpresa'), #consultar al bakend las areas de las empresas
    path('administracion/kpis/select/area/', viewadmin.selectArea, name='selectArea'), # consutar los departamentos del area seleccionada
   

    path('administracion/empresa/', viewadmin.registroEmpresa, name='registroEmpresa'), #Rergistro de empresa
    path('administracion/empresa/list', viewadmin.listarempresa, name='listarempresa'), #Listar Empresas
    path('administracion/empresa/delete/<int:idempresa>/', viewadmin.eliminarempresa, name='eliminarempresa'),  # eliminar cursos
    path('administracion/empresa/update/<int:idempresa>/', viewadmin.modificarempresa, name='modificarempresa'), #Modificar empresa
    

    #=================== registro de grupo empresarial ============================
    path('administracion/add/grupo/empresa/', viewadmin.grupoempresa, name='registroGrupoEmp'), #Modificar empresa
    path('administracion/delete/grupo/empresa/<int:idgrup>/', viewadmin.deleteGrupEmpresa, name='deleteGrupEmpresa'),
    path('administracion/add/new/area/', viewadmin.addArea, name='addArea'),
    path('administracion/add/new/departamento/', viewadmin.addDepartamento, name='addDepartamento'),
    path('administracion/delete/departamento/<int:iddepar>/<int:area>/', viewadmin.deleteDepar, name='deleteDepar'),
    #====================== registro de grupos de fromación =================
    
    path('administracion/grupos/list/', viewadmin.listGrupos, name='listGrupos'), #ruta para registrar o dirigir a cursos
    path('administracion/grupos/crear/', viewadmin.creargrupo, name='creargrupo'),
    path('administracion/grupos/nuevo/', viewadmin.addgrupo, name='addgrupo'),
    path('administracion/grupos/delete/<int:idgrupo>/', viewadmin.eliminargrupo, name='eliminargrupo'),
    path('administracion/grupos/editar/', viewadmin.editargrupo, name='editargrupo'),
    path('administracion/grupos/update/', viewadmin.editargrupoagregado, name='editargrupoagregado'), #editar grupos desde form externo
    path('administracion/grupos/list/user/<int:idgrupo>/', viewadmin.usersgrupo, name='usersgrupo'), #lista los usuarios pertenecientes a un grupo
    path('administracion/grupos/list/cursos/<int:idgrupo>/', viewadmin.cursosgrupo, name='cursosgrupo'),
    path('administracion/grupos/delete/total/<int:idgrupo>/', viewadmin.deletegrupos, name='deletegrupos'),
    path('administracion/grupos/duplicar/<int:idgr>/', viewadmin.duplicarGrupo, name='duplicarGrupo'),
    
    #====================== end registro de grupos =================
    #====================== Crear formularios ========================
    path('administracion/formu/', viewformu.crearformu, name='crearformu'),
    path('administracion/formu/listar/', viewformu.listarformu, name='listarformu'),
    path('administracion/formu/compartir/<int:idsesion>/', viewformu.qr_formulario, name="qrformu"),
    path('administracion/formu/editar/<int:idform>/', viewformu.editarform, name='editarform'),
    path('administracion/formu/delete/ask/<int:idpreg>/<int:idformu>/', viewformu.eliminarPregunta, name='eliminarPregunta'),
    path('administracion/formu/add/ask/<int:idform>/', viewformu.addNewPreguntas, name='addNewPreguntas'),
    path('administracion/formu/delete/answer/<int:idres>/<int:idform>/', viewformu.eliminarRespuesta, name='eliminarRespuesta'),
    path('administracion/formu/update/<int:idform>/', viewformu.savePreguntas, name='savePreguntas'),
    path('administracion/formu/copiar/<int:idform>/', viewformu.copiarform, name='copiarform'),
    path('administracion/formu/delete/<int:idform>/', viewformu.eliminarForm, name='eliminarForm'),
    path('administracion/formu/sesion/add/<int:idform>/', viewformu.addsesionform, name='addsesionform'), #agregar formularios a la sesion
    #=================== rutas para revisar formularios ==================
    path('administracion/formu/list/cursos/', viewformu.usersFomularios, name='usersFomularios'), #agregar formularios a la sesion
    path('administracion/formu/list/forms/sesion/<int:idsesion>/', viewformu.verFomrsesion, name='verFomrsesion'), #agregar formularios a la sesion
    
    #============= end formularios ==================
    path('administracion/empresa/vincular/list/', viewadmin.visualizarAreaDepto, name='visualizarAreaDepto'),
    path('administracion/empresa/vincular/delete/<int:idarea>/', viewadmin.eliminavinculo, name='eliminarvinculo'),
    path('administracion/validarasistencia/<int:idsesion>/', viewadmin.validarasistencia, name='validarasistencia'),
    path('administracion/generarqr/<int:idsesion>/', viewadmin.generarqr, name='generarqr'),

    #================ valoracion del curso =========================================
    path('administracion/curso/asistentelist/<int:idsesion>/', viewadmin.listarasistentes, name='listarasistentes'),
    path('administracion/curso/deleteasistente/<int:idasis>/', viewadmin.eliminarasistente, name='eliminarasistente'),
    path('administracion/curso/list/valoracion/<int:idsesion>/', viewadmin.listarcalificacion, name="listarcalificacion"),
    path('administracion/curso/list/deletevaloracion/<int:idcali>/', viewadmin.borrarcalificacion, name="borrarcalificacion"),
    path('administracion/curso/metricas/<int:idcurso>/', viewadmin.metricasCurso, name="metricasCurso"),

    #==================== rutas para evaluar formulario ============
    path('usuarios/curso/sesion/formulario/<int:idsesion>/', viewuser.verformusesion, name="verformusesion"),
    path('usuarios/curso/respuesta/formulario/<int:idsesion>/<int:idformu>/', viewuser.saveRespuestas, name="saveRespuestas"),
    path('evaluar/test/<int:idsesion>/', viewuser.verFormuQR, name="verFormuQR"),
    path('administracion/validarasistenciaform/<int:idsesion>/', viewuser.validarasistenciaform, name='validarasistenciaform'),
    path('usuarios/inscribiruserform/<int:idsesion>/', viewuser.inscribirasistenteform, name="inscribirasistenteform"),
    path('usuarios/inscribiruserform/form/<int:idsesion>/<int:idusuario>/', viewuser.listformuqr, name="listformuqr"),
    path('usuarios/inscribiruserform/form/save/<int:idsesion>/<int:idformu>/<int:idusu>/', viewuser.saveRespuestasFormu, name="saveRespuestasFormu"),
    
    #=========================================================
    path('administracion/validarasistencia/<int:idsesion>/', viewadmin.validarasistencia, name='validarasistencia'),
    path('administracion/generarqr/<int:idsesion>/', viewadmin.generarqr, name='generarqr'),
    path('administracion/curso/asistentelist/<int:idsesion>/', viewadmin.listarasistentes, name='listarasistentes'),

    path('Administracion/curso/cambiarpendiente/<int:idsesion>/<int:iduser>/', viewadmin.cambiar_pendiente, name="cambiarpendiente"),
    #=================== cambiar pendiente desde formularios ========================
    path('administracion/usuario/cambiarpendiente/<int:idsesion>/<int:iduser>/', viewformu.cambiar_pendiente_formulario, name="cambiar_pendiente_formulario"),
    
    path('administracion/curso/deleteasistente/<int:idasis>/', viewadmin.eliminarasistente, name='eliminarasistente'),
    path('administracion/curso/list/valoracion/<int:idsesion>/', viewadmin.listarcalificacion, name="listarcalificacion"),
    path('administracion/curso/list/deletevaloracion/<int:idcali>/', viewadmin.borrarcalificacion, name="borrarcalificacion"),
    path('administracion/compromisos/', viewadmin.listar_compromisos, name="listarcompromisos"),
    path('administracion/compromisos/editcompromiso/<int:idcomp>/', viewadmin.addrespuesta, name="editcompromiso"),
    path('administracion/compromisos/deletecompromiso/<int:idcomp>/', viewadmin.delete_compromiso, name="deletecompromiso"),
    #=============================== ver compromisos de cada usuario ================================0
    path('administracion/compromisos/ver/usuario/<int:iduser>/', viewadmin.vercompromisos, name="vercompromisos"),
    path('administracion/compromisos/savecompromiso/<int:idcom>/', viewadmin.savecompromiso, name="savecompromiso"),
    path('administracion/compromisos/buscar/<int:idcur>/', viewadmin.filtroCompromisos, name="filtroCompromisos"),
    
    #================================= Rutas de Usuario =============================================================
    path('usuarios/curso/listar/', viewuser.listar_cursos_usuario, name="listarcursosusuario"),
    path('usuarios/calificar-sesion/<int:idsesion>/', viewuser.add_calificacion, name="addcalificacion"),
    path('usuarios/compromisos/', viewuser.agregar_compromiso, name="compromisos"),
    path('usuarios/compromisos/editar/<int:idcomp>/', viewuser.editarcompromiso, name="editarcompromiso"),
    path('usuarios/inscribiruser/<int:idsesion>/', viewadmin.inscribir_asistente, name="inscribirasistente"),
    path('usuarios/calificaciones/view/<int:idcurso>/', viewuser.calificacionCurso, name="calificacionCurso"),
    path('usuarios/formu/all/view/<int:idcurso>/', viewuser.formulariosCurso, name="formulariosCurso"),
    
    #============================ Fin de Rutas de usuario ===========================================================
    
    #============================= carga masiva de los usuarios desde el amdin==================
    path('usuarios/view/registro/', viewadmin.registroUser, name="registroUser"),
    path('usuarios/view/nuevo/user/', viewadmin.addNewUser, name="addNewUser"),
    path('usuarios/view/delete/user/<int:idusu>/', viewadmin.deleteUser, name="deleteUser"),
    path('usuarios/view/lock/user/<int:idusu>/', viewadmin.lockaccess, name="lockaccess"),
    path('usuarios/view/update/user/<int:idusu>/', viewadmin.updateUser, name="updateUser"),

    #=================================== crear links de formadores =========================
    path('view/new/trainer/', viewformador.viewhome, name="viewhome"),
    path('add/new/trainer/', viewformador.registerTrainer, name="registerTrainer"),
    path('show/formadoremp/', viewformador.empresasmodal, name="empresasmodal"),
    path('formador/cambiar/empresa/', viewformador.cambiarEmpresa, name="cambiarEmpresa"),
    path('formador/empresa/', viewformador.consultarEmpresa, name="consultarEmpresa"),
    
    #==================================== agregar actividades a compromisos ===================
    path('usuario/add/avance/', viewuser.craeteAvance, name="craeteAvance"),
    path('usuario/update/avance/<int:idavance>/', viewuser.updateAvance, name="updateAvance"),
    path('usuario/delete/avance/<int:idavance>/', viewuser.deleteAvance, name="deleteAvance"),
    
    #====================================Dashboard de admin=======================================================================
    path('administracion/filtrar/curso/<int:idcurso>/', views.filtrarcurso, name="filtrarCurso"),
    #=== ruta para filtrar los cursos de resultados de aprendizaje ====
    path('administracion/filter/cursos/<int:idcurso>/', viewformu.filtroCurso, name="filtroCurso"),
  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   
