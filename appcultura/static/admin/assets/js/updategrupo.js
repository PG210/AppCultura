$(document).ready(function () {
      $('.btn-edit').on('click', function () {
          var rowId = $(this).data('id');
          // Oculta el botón de editar y muestra el botón de guardar
          $('.btn-edit[data-id=' + rowId + ']').hide();
          $('.btn-save[data-id=' + rowId + ']').show();

          // Hace las celdas editables
          $('.editable[data-id=' + rowId + ']').each(function () {
              var field = $(this).data('field');
              var value = $(this).text();
              $(this).html('<input type="text" name="' + field + '" value="' + value + '">');
          });
      });

      $('.btn-save').on('click', function () {
          var rowId = $(this).data('id');
          var data = {};

          // Recopila los datos editados
          $('.editable[data-id=' + rowId + ']').each(function () {
              var field = $(this).data('field');
              var value = $(this).find('input').val();
              data[field] = value;
          });
          
          // Agrega el id al objeto de datos
          data['id'] = rowId;
          // Obtiene el token CSRF del formulario
          var csrfToken = $('#formularioTabla [name="csrfmiddlewaretoken"]').val();
          data['csrfmiddlewaretoken'] = csrfToken;
          // Envía los datos al servidor mediante AJAX
          $.ajax({
              url: '/administracion/grupos/editar/',  // Reemplaza con la URL de tu endpoint
              type: 'POST',
              data: data,
              success: function(response) {
                  // Manejar la respuesta exitosa si es necesario
                  var msj = response.message;
                  var opres = response.opciones; //retorna la data desde el backend
                  Swal.fire({
                        icon: 'success',
                        title: 'Guardado exitoso',
                        text: msj,
                    });
                  
                    $("#ngrupo").empty();

                    for (var i = 0; i < opres.length; i++) {
                        // Acceder a los campos específicos del objeto
                        var id = opres[i].id;
                        var nombre = opres[i].nombre;
                        $("#ngrupo").append('<option value="' + id + '">' + nombre + '</option>');
                    }
                  
              },
              error: function(xhr, status, error) {
                  // Manejar el error si es necesario
                  var jsonResponse = xhr.responseJSON;
                  Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: jsonResponse.mensaje,
                        });
              },
              complete: function() {
                  // Oculta el botón de guardar y muestra el botón de editar
                  $('.btn-edit[data-id=' + rowId + ']').show();
                  $('.btn-save[data-id=' + rowId + ']').hide();

                  // Actualiza las celdas con los nuevos valores
                  $('.editable[data-id=' + rowId + ']').each(function () {
                      var value = $(this).find('input').val();
                      $(this).html(value);
                  });
              }
          });
      });
  });