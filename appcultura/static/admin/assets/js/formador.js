$(document).ready(function () {
// Manejar clic en el botón
$("#addusu").click(function () {
    // Obtener el valor del campo de entrada
    let nombre = $("#nombre").val();
    let apellido = $("#apellido").val();
    let email = $("#email").val();
    let ced = $("#ced").val();
    let tel = $("#tel").val();
    let emp = $("#emp").val();
    let area = $("#area").val();
    let depar = $("#depar").val();
    let cargo = $("#cargo").val();
    let rol = $("#rol").val();
    let pass = $("#pass").val();
    let csrf_token = $('[name="csrfmiddlewaretoken"]').val();
    if (nombre == null || apellido == null || email == null || ced == null || tel == null || emp == "" || rol == "" || pass == null ){
      toastr.info('Completa todos los campos.', null, { timeOut: 3000, extendedTimeOut: 3000});
      return true;
    }
    // Enviar datos al backend usando AJAX
    $.ajax({
        url: "/administracion/add/nuevo/user/",  // Reemplaza con la URL de tu vista en Django
        method: "POST",
        headers: {
            'X-CSRFToken': csrf_token
        },
        data: {
          nombre: nombre,
          apellido: apellido,
          email: email,
          ced: ced,
          tel: tel,
          emp: emp,
          area: area,
          depar: depar,
          cargo: cargo,
          rol: rol,
          pass: pass
        },
        success: function (response) {
            // Manejar la respuesta del backend
            $("#formularioUsu")[0].reset();
            if(response.iduser){
              $("#formador").append('<option value="' + response.iduser + '">' + response.nombre + ' '+ response.apellido +'</option>');
               toastr.success(response.mensaje, null, { timeOut: 3000, extendedTimeOut: 3000});
            }
        },
        error: function (xhr, textStatus, errorThrown) {
            // Manejar errores
            var jsonResponse = xhr.responseJSON;
            if (xhr.status === 400) {
                toastr.error('Error en la solicitud.', null, { timeOut: 3000, extendedTimeOut: 3000});
                return;
            } else {
                // Mostrar mensaje de error genérico con SweetAlert
                toastr.error('Error en la solicitud.', null, { timeOut: 3000, extendedTimeOut: 3000});
                return;
            }
            //=============================
        }
    });
});
});
