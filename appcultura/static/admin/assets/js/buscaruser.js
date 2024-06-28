  $(document).ready(function() {
    // Función para filtrar la tabla específica
    function filterTable(searchTerm) {
      $('#tablaDatos tbody tr').each(function() {
        var rowText = $(this).text().toLowerCase();
        if (rowText.indexOf(searchTerm) === -1) {
          $(this).hide();
        } else {
          $(this).show();
        }
      });
    }

    // Evento de entrada para el campo de búsqueda
    $('#searchInput').on('input', function() {
      var searchTerm = $(this).val().toLowerCase();
      filterTable(searchTerm);
    });
  });
