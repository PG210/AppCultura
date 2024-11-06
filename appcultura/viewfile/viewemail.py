from appcultura.utils.email_utils import send_email
from appcultura.modelos.accesstoken import AccessToken
from django.shortcuts import render

# Ejemplo de uso
def emailprueba(request):
     token_info = AccessToken.objects.filter().first()
     access_token = token_info.access_token # Asegúrate de obtener el token primero
     destino = "pedro@evolucion.co"
     asunto = "Reunión"
     content = "Esta es una reunión para el dia lunes"
     send_email(access_token, destino, asunto, content)
     return render(request, 'layoutsinicio/login.html')

def pagnotfind(request):
    return render(request, '404.html')