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
    path('administracion/kpis/', viewadmin.kpiarea, name='kpiarea'),  # Crear KPI para area y departamento
    path('administracion/kpis/list/', viewadmin.listarkpiarea, name='listarkpiarea'),  # Crear KPI para area y departamento
    path('administracion/kpis/editar/<int:idkpi>/', viewadmin.editarkpi, name='editarkpi'),  # editar curso
    path('administracion/kpis/delete/<int:idkpi>/', viewadmin.eliminarkpi, name='eliminarkpi'),  # eliminar cursos
    path('administracion/empresa/', viewadmin.registroEmpresa, name='registroEmpresa'), #Rergistro de empresa
    path('administracion/empresa/list', viewadmin.listarempresa, name='listarempresa'), #Listar Empresas
    path('administracion/empresa/delete/<int:idempresa>/', viewadmin.eliminarempresa, name='eliminarempresa'),  # eliminar cursos
    path('administracion/empresa/update/<int:idempresa>/', viewadmin.modificarempresa, name='modificarempresa'), #Modificar empresa

]   
   
