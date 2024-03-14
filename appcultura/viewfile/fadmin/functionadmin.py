from io import BytesIO
import qrcode
from django.core.files.storage import default_storage


def generar_qr(data, name):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Agregar datos al código QR (puedes cambiar el texto según tus necesidades)
    #data = f'http://localhost:8000/administracion/validarasistencia/{idsesion}'
    qr.add_data(data)
    qr.make(fit=True)

    # Crear una imagen PIL (Pillow) desde el código QR
    img = qr.make_image(fill_color="black", back_color="white")

    # Guardar la imagen en un buffer de BytesIO
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    # Guardar la imagen en el sistema de archivos de Django
    filename = f"qrcodes/{name}_qrcode.png"
    filepath = default_storage.save(filename, buffer)

    # Obtener la URL de la imagen
    qr_code_url = default_storage.url(filepath)
    return qr_code_url