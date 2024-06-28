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
                    Swal.fire({
                        icon: 'success',
                        title: 'Guardado exitoso',
                        text: 'Los datos se han guardado correctamente.',
                    });
                    $("#ngrupo").append('<option value="' + opres.id + '">' + opres.nombre + '</option>');
                    $("#grtable").append('<th scope="row">'+ opres.id +'</th>' +
                                  '<td><span class="editable" data-field="nombre" data-id="'+ opres.id +'">'+ opres.nombre +'</span></td>'+
                                  '<td><span class="editable" data-field="descrip" data-id="'+ opres.id +'">'+ opres.descrip +'</span></td>'+
                                  '<td>'+
                                      '<a type="button" class="btn btn-outline-primary btn-edit" data-id="'+ opres.id +'"><i class="bi bi-pencil-square"></i></a>'+
                                      '<a type="button" class="btn btn-outline-success btn-save" data-id="'+ opres.id +'" style="display: none;">Guardar</a>'+
                                      '<a type="button" class="btn btn-outline-danger" href="/administracion/grupos/delete/'+ opres.id +'/"><i class="bi bi-trash3-fill"></i></a>'+
                                  '</td>');
                  
                   
                },
                error: function (xhr, textStatus, errorThrown) {
                    // Manejar errores
                    var jsonResponse = xhr.responseJSON;
                    if (xhr.status === 400) {
                        // Mostrar mensaje de error personalizado con SweetAlert
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: jsonResponse.mensaje,
                        });
                    } else {
                        // Mostrar mensaje de error genérico con SweetAlert
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: jsonResponse.mensaje,
                        });
                    }
                    //=============================
                }
            });
        });
    });