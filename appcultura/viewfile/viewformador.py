from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse #sirve para hacer las peticiones
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate #crea la sesion de un usuario al registrarse
from django.contrib.auth.decorators import login_required # proteger las rutas de accesos
from django.db import IntegrityError
from appcultura.modelos.empresa import Empresa

from appcultura.modelos.formador_empresa import FormadorEmpresa #errores de la base de datos

from ..models import UserPerfil, Formulario, Preguntas, Opciones, Curso, Sesioncurso, SesionFormulario, GruposCursos, RespuestaForm
from django.http import Http404
from django.http import JsonResponse

def viewhome(request):
    if request.method == 'POST':
        print(request.POST)  
    return render(request, 'formador/home.html')

def registerTrainer(request):
    print('nueva vista')

#==== vista para elegir la empresa actual ===========
@login_required
def empresasmodal(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    data = list(FormadorEmpresa.objects.filter(idusu=perfil_usuario.id).select_related('idempresa').values('id', 'idempresa', 'idempresa__nombre', 'idusu', 'estado'))
    return JsonResponse({'data': data})

@login_required
def consultarEmpresa(request):
    idformador = request.GET.get('opcion')
    if idformador:
     perfil_usuario = UserPerfil.objects.get(id=idformador)
     data = list(FormadorEmpresa.objects.filter(idusu=perfil_usuario.id).select_related('idempresa').values('id', 'idempresa', 'idempresa__nombre', 'idusu', 'estado'))
    else:
        data = ''
    return JsonResponse({'data': data})
#==============
@login_required
def cambiarEmpresa(request):
    perfil_usuario = UserPerfil.objects.get(user=request.user)
    if request.method == 'POST':
        print(request.POST)
        id_empresa =request.POST.get('selectEmpresa')
        empresa = Empresa.objects.get(id=id_empresa)
        formadores = FormadorEmpresa.objects.filter(idusu=perfil_usuario)
        for formador in formadores:
            formador.estado = False
            formador.save()
        #========== buscar la que desea activar ==============
        updateselec = FormadorEmpresa.objects.get(idempresa=empresa, idusu=perfil_usuario)
        updateselec.estado = True
        updateselec.save()
        return redirect('administracion') # redirecciona a la vista principal
   