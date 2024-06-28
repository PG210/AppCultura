$(document).ready(function () {
    // Manejar clic en el botón
    $("#enviarDatos").click(function () {
        // Obtener el valor del campo de entrada
        var nombreg = $("#nombreg").val();
        var descripg = $("#descripg").val();
        var gemp = $("#gemp").val(); 
        var csrf_token = $('[name="csrfmiddlewaretoken"]').val();
        // Enviar datos al backend usando AJAX
        $.ajax({
            url: "/administracion/grupos/nuevo/",  // Reemplaza con la URL de tu vista en Django
            method: "POST",
            headers: {
                'X-CSRFToken': csrf_token
            },
            data: {
                nombreg: nombreg,
                descripg: descripg,
                gemp: gemp
            },
            success: function (response) {
                // Manejar la respuesta del backend
                $("#formulariogrupo")[0].reset();
                $("#registrarGrupo").modal('hide');
                var opres = response; //retorna la data desde el backend
                toastr.success('Grupo creado exitosamente.', null, { timeOut: 3000, extendedTimeOut: 3000});
                $(".checkgrupo").append('<li class="list-group-item">'+
                                  '<span><input type="checkbox" name="grupo" value="'+ opres.id +'">&nbsp;'+ opres.nombre +'&nbsp;'+
                                  '</span></li>');
            },
            error: function (xhr, textStatus, errorThrown) {
                // Manejar errores
                var jsonResponse = xhr.responseJSON;
                if (xhr.status === 400) {
                    toastr.warning('Error al crear el grupo.', null, { timeOut: 3000, extendedTimeOut: 3000});
                    return;
                } else {
                    // Mostrar mensaje de error genérico con SweetAlert
                    toastr.warning('Error al crear el grupo.', null, { timeOut: 3000, extendedTimeOut: 3000});
                    return;
                }
                //=============================
            }
        });
    });
});