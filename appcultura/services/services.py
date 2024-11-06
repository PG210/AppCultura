# mi_aplicacion/services.py
from requests_oauthlib import OAuth2Session
from mywebapp import settings
from requests.auth import HTTPBasicAuth
from django.utils import timezone
from datetime import timedelta
from appcultura.modelos.accesstoken import AccessToken

# URLs de Microsoft OAuth2
AUTHORIZE_URL = 'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize'
TOKEN_URL = 'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'


class MicrosoftOAuthService:
    
    def __init__(self):
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self.redirect_uri = settings.MICROSOFT_REDIRECT_URI
        self.tenant_id = settings.MICROSOFT_TENANT_ID

    def get_authorization_url(self):
        """Generar la URL de autorización de Microsoft con scopes consistentes"""
        dat = [
                'email',
                'profile',
                'openid',
                'https://graph.microsoft.com/Mail.Send',
                'https://graph.microsoft.com/Mail.ReadWrite',
                'https://graph.microsoft.com/User.Read',
                'offline_access'
            ]
        oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=dat)
        authorization_url, _ = oauth.authorization_url(
            AUTHORIZE_URL.format(tenant_id=self.tenant_id),
            prompt='consent'  # Forzar la renovación del consentimiento
        )
        return authorization_url

    def get_token(self, authorization_code):
        """Obtener el token de acceso usando el código de autorización"""
        dat = [
                'email',
                'profile',
                'openid',       
                'https://graph.microsoft.com/Mail.Send',
                'https://graph.microsoft.com/Mail.ReadWrite',
                'https://graph.microsoft.com/User.Read'
            ]
        oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=dat)

        # Intercambiar el código de autorización por el token
        token = oauth.fetch_token(
            TOKEN_URL.format(tenant_id=self.tenant_id),
            code=authorization_code,
            client_secret=self.client_secret,
            include_client_id=self.client_id,
            auth=HTTPBasicAuth(self.client_id, self.client_secret)
        )
        # Guardar el token en la base de datos
        self.save_token(token)
        return token

    def refresh_access_token(self):
        dat = [
                'email',
                'profile',
                'openid',
                'https://graph.microsoft.com/Mail.Send',
                'https://graph.microsoft.com/Mail.ReadWrite',
                'https://graph.microsoft.com/User.Read'
            ]
        """Renovar el token de acceso usando el refresh token"""
        access_token_record = AccessToken.objects.first()  # Obtener el registro del token
        if not access_token_record or not access_token_record.refresh_token:
            raise ValueError("No se ha encontrado el refresh token")

        oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=dat)

        # Intercambiar el refresh token por un nuevo access token
        token = oauth.refresh_token(
            TOKEN_URL.format(tenant_id=self.tenant_id),
            refresh_token=access_token_record.refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Guardar el nuevo token
        self.save_token(token)

    def save_token(self, token):
        """Guardar o actualizar el token en la base de datos"""
        expires_at = timezone.now() + timedelta(seconds=token['expires_in'])
        access_token_record = AccessToken.objects.first()  # Asumimos que tienes un solo token
       
        if not access_token_record:
            access_token_record = AccessToken()

        access_token_record.access_token = token['access_token']
        access_token_record.refresh_token = token.get('refresh_token', access_token_record.refresh_token)  # Si no se recibe un nuevo refresh_token, mantener el anterior
        access_token_record.token_type = token['token_type']
        access_token_record.expires_in = token['expires_in']
        access_token_record.expires_at = expires_at
        access_token_record.scope = ', '.join(token['scope'])
        access_token_record.save()
    
    #============metodo para verificar la expiracion del token ==============
    def is_token_expired(self):
        """Verifica si el token de acceso ha expirado."""
        access_token_record = AccessToken.objects.first()
        
        if not access_token_record:
            return True  # No hay token almacenado
        
        return access_token_record.expires_at <= timezone.now()
