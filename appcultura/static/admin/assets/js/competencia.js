$(document).ready(function(){
  $("#enviarcom").on('click', function(){
    validarFormulario();
  });
});

// validar formulario
function validarFormulario(){
  let com = $("#comp").val();
  let csrftoken = $("input[name='csrfmiddlewaretoken']").val();
  if (com === ''){
      toastr.info('El campo de competencia es obligatorio.');
      return;
  }
  // si pasa las validaciones
  enviarFormulario(com, csrftoken);
}

// Enviar datos al backend
function enviarFormulario(com, csrftoken){
    $.ajax({
       url:'/administracion/curso/competencia/',
       type: 'POST',
       data: { com: com, 
               csrfmiddlewaretoken: csrftoken
        },
      success: function(response) {
          $("#comp").val('');
          if (response.estado == 1){
             toastr.success(response.mensaje);
             $(".inputchek").append('<li class="list-group-item" lcat="'+ response.comp +'">'+
                                    '<span><input type="checkbox" name="compe" value="'+ response.comp +'">&nbsp;'+ response.valor +'&nbsp;'+
                                    '<a href="" onclick="deleteCompetencia('+ response.comp +')" style="color: red;">x</a>'+
                                    '</span></li>');
          }
          else
             toastr.info(response.mensaje);
       },
       error:function(error){
           toastr.error('Ocurrio un error en la solicitud.', error);
       }

   });
}
//============================================================
function deleteCompetencia(comp){
   eliminarComp(comp);
}
//=========================================================
//eliminar dato
$(document).ready(function() {
  // Manejar el clic en el botón de eliminar
  $(".delete-button").on('click', function(event) {
      event.preventDefault();
      let comId = $(this).data('id');
      eliminarComp(comId);
  });
});

//============== eliminar dato =========0
function eliminarComp(comId){
    $.ajax({
        url: '/administracion/curso/competencia/delete/'+ comId +'/', // URL de eliminación
        type: 'GET',
        data: { 
            id: comId
        },
        success: function(response) {
          $('li[lcat="' + response.valor + '"]').remove();
          toastr.warning(response.mensaje);
        },
        error: function(error) {
          toastr.error('Ha ocurrido un error en la solicitud.');
        }
    });
}
