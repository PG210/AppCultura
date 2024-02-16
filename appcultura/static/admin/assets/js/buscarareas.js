$(document).ready(function() {

    //=================================
    $('.empUsuSelect').change(function() {
      let userId = $(this).attr('id').replace('empUsu', '');
      let selectedOption = $(this).val();
      // Realizar la solicitud AJAX al backend
      $.ajax({
        url: '/administracion/kpis/select/',
        method: 'GET',
        data: { opcion: selectedOption },
        success: function(response) {
          //================================
          var datos = response.areas;
          var select = $("#areaUsu" + userId);
          select.empty(); //==limpiar datos
          var selectDepar = $("#deparUsu" + userId);
          selectDepar.empty(); //==limpiar datos

          select.append(`<option value="">Elegir ...</option>`);
          selectDepar.append(`<option value="">Elegir ...</option>`);
          datos.forEach(function(area) {
              select.append(`<option value="${area.id}">${area.nombre}</option>`);
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
//=====================solicitud para encontrar los departamentos ============
$(document).ready(function() {
    $('.areaUsuSelect').change(function() {
      let userId = $(this).attr('id').replace('areaUsu', '');
      let selectedArea = $(this).val();
      // Realizar la solicitud AJAX al backend
      $.ajax({
        url: '/administracion/kpis/select/area/',
        method: 'GET',
        data: { opcion: selectedArea },
        success: function(response) {
          //================================
          var depar = response.data;
          var selectDepar = $("#deparUsu" + userId);
          selectDepar.empty(); //==limpiar datos
          selectDepar.append(`<option value="">Elegir ...</option>`);
          depar.forEach(function(dep) {
              selectDepar.append(`<option value="${dep.id}">${dep.nombre}</option>`);
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
