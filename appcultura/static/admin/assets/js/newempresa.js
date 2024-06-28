$(document).ready(function () {
// Manejar clic en el botón
$("#addbuild").click(function () {
    // Obtener el valor del campo de entrada
    let entidad = $("#entidad").val();
    let nit = $("#nit").val();
    let email = $("#emailbuild").val();
    let tel = $("#phonebuild").val();
    let dir = $("#addressbuild").val();
    let sector = $("#fieldsector").val();
    let tam = $("#fieldtam").val();
    let csrf_token = $('[name="csrfmiddlewaretoken"]').val();
    if (entidad == null || nit == null || email == null || tel == null || dir == null || sector == "" || tam == "" ){
      toastr.info('Completa todos los campos.', null, { timeOut: 3000, extendedTimeOut: 3000});
      return true;
    }
    // Enviar datos al backend usando AJAX
    $.ajax({
        url: "/administracion/new/empresa/",  // Reemplaza con la URL de tu vista en Django
        method: "POST",
        headers: {
            'X-CSRFToken': csrf_token
        },
        data: {
          entidad: entidad,
          nit: nit,
          email: email,
          tel: tel,
          dir: dir,
          sector: sector,
          tam: tam
        },
        success: function (response) {
            // Manejar la respuesta del backend
            $("#formnuewbuild")[0].reset();
            if(response.id){
                $("#empresa").append('<option value="' + response.id + '">' + response.nombre + '</option>');
                $("#emp").append('<option value="' + response.id + '">' + response.nombre + '</option>');
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