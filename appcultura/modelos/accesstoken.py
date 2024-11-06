from django.db import models

class AccessToken(models.Model):
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_type = models.CharField(max_length=50)
    expires_in = models.IntegerField()
    expires_at = models.DateTimeField()
    scope = models.TextField()

    def __str__(self):
        return f'Token {self.token_type} - Expires at {self.expires_at}'