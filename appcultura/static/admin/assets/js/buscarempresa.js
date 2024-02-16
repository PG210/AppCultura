$(document).ready(function() {
    $('#formador').change(function() {
      var selectedOption = $(this).val();
      // Realizar la solicitud AJAX al backend
      $.ajax({
        url: '/formador/empresa/',
        method: 'GET',
        data: { opcion: selectedOption },
        success: function(data) {
          //================================
          let datos = data.data;
          var selectEmpresa = $("#empresa");
          selectEmpresa.empty(); //==limpiar datos

          selectEmpresa.append(`<option value="">Elegir ...</option>`);
          datos.forEach(function(dep) {
            selectEmpresa.append(`<option value="${dep.idempresa}">${dep.idempresa__nombre}</option>`); 
        });
          //===============================
        },
        error: function(xhr, status, error) {
          //console.error('La solicitud falló:', error);
        }
      });
      //=============================
    });
  });