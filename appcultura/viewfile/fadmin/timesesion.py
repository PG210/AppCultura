from django.contrib.sessions.models import Session
from django.utils import timezone
import math

"""def tiempo(session_key):
    try:
        session = Session.objects.get(session_key=session_key)
        time_remaining = (session.expire_date - timezone.now()).total_seconds()
        #thoras = math.floor(time_remaining / 60)
        return int(time_remaining)
    except Session.DoesNotExist:
        # Si no se encuentra una sesión para el usuario, se asume que la sesión ha expirado
        return 0"""
    
def tiempo(request):
    if request.user.is_authenticated:
        session_key = request.COOKIES.get("sessionid")
        if session_key:
            try:
                session = Session.objects.get(session_key=session_key, expire_date__gte=timezone.now())
                time_remaining = (session.expire_date - timezone.now()).total_seconds()
                return {'thoras': time_remaining}
            except Session.DoesNotExist:
                pass
    return {'thoras': None}