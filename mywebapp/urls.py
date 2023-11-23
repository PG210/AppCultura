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
from django.contrib import admin
from django.urls import path
from appcultura import views
from appcultura.viewfile import viewadmin #utilizar una nueva vista 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  #pagina inicial
    path('login/user/', views.loginuser, name='loginuser'),  #login
    path('logout/', views.singout, name='logout'), # cerrar sesion
    path('reg/user/', views.reguser, name='reguser'),  #registrar user
    path('administracion/', views.administracion, name='administracion'),  #panel de administrador
    path('administracion/curso/', viewadmin.registroCursos, name='registroCursos'),  #registro cursos

    path('administracion/curso/list/', viewadmin.listarcursos, name='listarcursos'),  #registro cursos
    path('administracion/curso/delete/<int:idcurso>/', viewadmin.eliminarcurso, name='eliminarcurso'),  # eliminar cursos
    path('administracion/curso/editar/<int:idcurso>/', viewadmin.editarcurso, name='editarcurso'),  # editar curso
    #==============descargar archvios ===========
    path('administracion/curso/descarga/<path:ruta>/', viewadmin.download, name='download'), 
    #==============================
    path('administracion/kpis/', viewadmin.kpiarea, name='kpiarea'),  # Crear KPI para area y departamento
    path('administracion/kpis/list/', viewadmin.listarkpiarea, name='listarkpiarea'),  # Crear KPI para area y departamento
    path('administracion/kpis/editar/<int:idkpi>/', viewadmin.editarkpi, name='editarkpi'),  # editar curso
    path('administracion/kpis/delete/<int:idkpi>/', viewadmin.eliminarkpi, name='eliminarkpi'),  # eliminar cursos
    path('administracion/empresa/', viewadmin.registroEmpresa, name='registroEmpresa'), #Rergistro de empresa
    path('administracion/empresa/list', viewadmin.listarempresa, name='listarempresa'), #Listar Empresas
    path('administracion/empresa/delete/<int:idempresa>/', viewadmin.eliminarempresa, name='eliminarempresa'),  # eliminar cursos
    path('administracion/empresa/update/<int:idempresa>/', viewadmin.modificarempresa, name='modificarempresa'), #Modificar empresa
    #====================== registro de grupos de fromación =================
    path('administracion/grupos/list/', viewadmin.listGrupos, name='listGrupos'), #ruta para registrar o dirigir a cursos
    path('administracion/grupos/crear/', viewadmin.creargrupo, name='creargrupo'),
    path('administracion/grupos/nuevo/', viewadmin.addgrupo, name='addgrupo'),
    path('administracion/grupos/delete/<int:idgrupo>', viewadmin.eliminargrupo, name='eliminargrupo'),
    path('administracion/grupos/editar/', viewadmin.editargrupo, name='editargrupo'),
    path('administracion/grupos/list/user/<int:idgrupo>/', viewadmin.usersgrupo, name='usersgrupo'), #lista los usuarios pertenecientes a un grupo
    
    #====================== end registro de grupos =================
    #codigo Jhon
    path('administracion/empresa/api', viewadmin.empresagetsector.as_view(), name='empresagetsector')
    #fin codigo Jhon

]   
   
