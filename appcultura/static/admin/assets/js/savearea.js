$(document).ready(function() {
    $('#emp').change(function() {
      var selectedOption = $(this).val();
      // Realizar la solicitud AJAX al backend
      $.ajax({
        url: '/administracion/kpis/select/',
        method: 'GET',
        data: { opcion: selectedOption },
        success: function(response) {
          //================================
          var datos = response.areas;
          var select = $("#area");
          select.empty(); //==limpiar datos
          var selectDepar = $("#depar");
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
    $('#area').change(function() {
      var selectedArea = $(this).val();
      // Realizar la solicitud AJAX al backend
      $.ajax({
        url: '/administracion/kpis/select/area/',
        method: 'GET',
        data: { opcion: selectedArea },
        success: function(response) {
          //================================
          var depar = response.data;
          var selectDepar = $("#depar");
          selectDepar.empty(); //==limpiar datos
          selectDepar.append(`<option value="">Elegir...</option>`);
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
    //==========================
    $('#rol').change(function() {
      let valor = $(this).val();
      console.log('Valor es', valor)
      if ($(this).val() === '4') {
        $('#formadorOcultar').hide();
      } else {
        $('#formadorOcultar').show();
      }
    });
    //=======================
  });
//======================== aqui funcionalidades del check ==============
document.getElementById('botonCheck').addEventListener('change', function() {
    var elementoOculto = document.getElementById('elementoOculto');
    var elementoOcultoDos = document.getElementById('elementoOcultoDos');
    if (this.checked) {
        // Si el botón de verificación está marcado, oculta el elemento
        elementoOculto.style.display = 'none';
        elementoOcultoDos.style.display = 'none';
        var selectDepar = $("#depar");
          selectDepar.empty(); //==limpiar datos
          selectDepar.append(`<option value="">Sin departamento ...</option>`);
    } else {
        // Si el botón de verificación está desmarcado, muestra el elemento
        elementoOculto.style.display = 'block';
        elementoOcultoDos.style.display = 'block';
    }
});
//=====================================0 para ocultar el campo de area y cargos===========


