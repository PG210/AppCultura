function togglePassword() {
      var passwordInput = document.getElementById('pass');
      var showPasswordCheckbox = document.getElementById('showPassword');
      // Cambiar el tipo de input basado en la casilla de verificación
      passwordInput.type = showPasswordCheckbox.checked ? 'text' : 'password';
  }
  //================ funcion para registrar============
  function copiarRuta() {
      var inputElement = document.getElementById("ruta_input");

      // Seleccionar el texto dentro del campo de entrada
      inputElement.select();
      inputElement.setSelectionRange(0, 99999); // Para dispositivos móviles

      // Copiar el texto al portapapeles
      document.execCommand("copy");
      // Alerta
       // Muestra el toast
       toastr.success("Ruta copiada al portapapeles", "", { progressBar: true });
    }
  //============================ ocultar =======================
  $(document).ready(function() {
    $('#checkboxOcultar').change(function() {
        // Si el checkbox está marcado, ocultar el div; de lo contrario, mostrarlo
        if ($(this).is(':checked')) {
            $('#ocudepar').hide();
            $('#ocudepardos').hide();
            let deparSel = $("#depar");
            deparSel.empty(); //==limpiar datos
            deparSel.append(`<option value="">Sin departamento ...</option>`);
        } else {
            $('#ocudepar').show();
            $('#ocudepardos').show();
        }
    });
});
//===========================
