import requests
import json

def send_email(access_token, recipient, subject, body):
    url = "https://graph.microsoft.com/v1.0/me/sendMail"
    
    # Crear el cuerpo del mensaje
    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient
                    }
                }
            ]
        },
        "saveToSentItems": "true"
    }

    # Establecer los encabezados
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Enviar la solicitud
    response = requests.post(url, headers=headers, data=json.dumps(message))

    # Manejar la respuesta
    if response.status_code == 202:
        print("Correo enviado exitosamente!")
    else:
        print("Error al enviar el correo:", response.json())
