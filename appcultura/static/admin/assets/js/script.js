   var contadorCampos = 1;
   var contaobjetivos =1;
   var contakpiobj = 1;

   function mostrarOcultarCampos() {
            var checkbox = document.getElementById("mostrarCampos");
            
            var camposDiv = document.getElementById("camposDiv");
            // Si la casilla de verificación está marcada, muestra los campos; de lo contrario, ocúltalos
            if (checkbox.checked) {
                camposDiv.style.display = "block";
            } else {
                camposDiv.style.display = "none";
            }
   }
        //================================================0
    function agregarCampo() {
      var formularioContainer = document.getElementById('formulario-container');
  
      // Crear un nuevo grupo de inputs
      var nuevoGrupo = document.createElement('div');
      nuevoGrupo.classList.add('mt-3', 'form-control'); // Agregar la clase al grupo
      // Crear tres inputs y agregarlos al grupo

        // Etiqueta y campo para la fecha de inicio
        var etiquetaInicio = document.createElement('label');
        etiquetaInicio.innerHTML = 'Fecha de Inicio:';
        etiquetaInicio.classList.add('col-sm-2', 'col-form-label');
        nuevoGrupo.appendChild(etiquetaInicio);

        var fechaInicio = document.createElement('input');
        fechaInicio.type = 'datetime-local';
        fechaInicio.name = 'fecha_inicio[]';
        fechaInicio.classList.add('col-sm-10');
        nuevoGrupo.appendChild(fechaInicio);

        // Etiqueta y campo para la fecha de finalizacion
        var etiquetaFinal = document.createElement('label');
        etiquetaFinal.innerHTML = 'Fecha final:';
        etiquetaFinal.classList.add('col-sm-2', 'col-form-label');
        nuevoGrupo.appendChild(etiquetaFinal);

        var fechaFinal = document.createElement('input');
        fechaFinal.type = 'datetime-local';
        fechaFinal.name = 'fecha_final[]';
        fechaFinal.classList.add('col-sm-10');
        nuevoGrupo.appendChild(fechaFinal);

         // Etiqueta y campo para lugar
        var etiqueLugar = document.createElement('label');
        etiqueLugar.innerHTML = 'Lugar:';
        etiqueLugar.classList.add('col-sm-2', 'col-form-label');
        nuevoGrupo.appendChild(etiqueLugar);

        var inputLugar = document.createElement('input');
        inputLugar.type = 'text';
        inputLugar.name = 'lugar[]';
        inputLugar.classList.add('col-sm-10');
        nuevoGrupo.appendChild(inputLugar);

         // Botón para eliminar el campo
         var btnEliminarCampo = document.createElement('button');
        btnEliminarCampo.innerHTML = 'X';
        btnEliminarCampo.classList.add('col-sm-1', 'btn', 'btn-danger', 'mt-2', 'float-end');
        btnEliminarCampo.onclick = function() {
          formularioContainer.removeChild(nuevoGrupo);
        };
       
        nuevoGrupo.appendChild(btnEliminarCampo);
        // Agregar el nuevo grupo al contenedor
      formularioContainer.appendChild(nuevoGrupo);
 
      contadorCampos++;
    }
    //======================= here function objective =================
    function agregarObjetivo() {
        var objetivosContainer = document.getElementById('contenedor-objetivos');
    
        // Crear un nuevo grupo de inputs
        var objetivosGrupo = document.createElement('div');
        objetivosGrupo.classList.add('mt-3', 'form-control'); // Agregar la clase al grupo
        // Crear tres inputs y agregarlos al grupo

        // Etiqueta y campo para la fecha de inicio
        var etiquetaDes = document.createElement('label');
        etiquetaDes.innerHTML = 'Descripción:';
        etiquetaDes.classList.add('col-sm-2', 'col-form-label');
        objetivosGrupo.appendChild(etiquetaDes);

        var desObjectivo = document.createElement('textarea');
        desObjectivo.type = 'text';
        desObjectivo.name = 'desobj[]';
        desObjectivo.classList.add('col-sm-10');
        desObjectivo.setAttribute('rows', '3');
        desObjectivo.setAttribute('required', 'required');
        objetivosGrupo.appendChild(desObjectivo);

        // Etiqueta y campo para lugar
        var etiqueCom = document.createElement('label');
        etiqueCom.innerHTML = 'Competencias:';
        etiqueCom.classList.add('col-sm-2', 'col-form-label');
        objetivosGrupo.appendChild(etiqueCom);

        var inputCom = document.createElement('textarea');
        inputCom.type = 'text';
        inputCom.name = 'competencias[]';
        inputCom.classList.add('col-sm-10');
        inputCom.setAttribute('rows', '3');
        inputCom.setAttribute('required', 'required');
        objetivosGrupo.appendChild(inputCom);

         // Botón para eliminar el campo
         var btnDelete = document.createElement('button');
         btnDelete.innerHTML = 'X';
         btnDelete.classList.add('col-sm-1', 'btn', 'btn-danger', 'mt-2', 'float-end');
         btnDelete.onclick = function() {
          objetivosContainer.removeChild(objetivosGrupo);
        };
       
        objetivosGrupo.appendChild(btnDelete);
        // Agregar el nuevo grupo al contenedor
        objetivosContainer.appendChild(objetivosGrupo);
 
      contaobjetivos++;
    }
    //===============================================
    //================funcion para agregar obj kpi ===========0
    function funcionkpi() {
        var kpiContainer = document.getElementById('contenedor-obj-kpi');
    
        // Crear un nuevo grupo de inputs
        var kpiGrupo = document.createElement('div');
        kpiGrupo.classList.add('mt-3', 'form-control'); // Agregar la clase al grupo
        // Crear tres inputs y agregarlos al grupo

        // Etiqueta y campo para la fecha de inicio
        var etiquetakpi = document.createElement('label');
        etiquetakpi.innerHTML = 'objetivo:';
        etiquetakpi.classList.add('col-sm-2', 'col-form-label');
        kpiGrupo.appendChild(etiquetakpi);

        var objkpi = document.createElement('textarea');
        objkpi.type = 'text';
        objkpi.name = 'objetivos[]';
        objkpi.classList.add('col-sm-10');
        objkpi.setAttribute('rows', '1');
        objkpi.setAttribute('required', 'required');
        kpiGrupo.appendChild(objkpi);

        // Etiqueta y campo para meta
        var etiqueCom = document.createElement('label');
        etiqueCom.innerHTML = 'Meta:';
        etiqueCom.classList.add('col-sm-2', 'col-form-label');
        kpiGrupo.appendChild(etiqueCom);
  
        var inputCom = document.createElement('textarea');
        inputCom.type = 'text';
        inputCom.name = 'metas[]';
        inputCom.classList.add('col-sm-10');
        inputCom.setAttribute('rows', '2');
        inputCom.setAttribute('required', 'required');
        kpiGrupo.appendChild(inputCom);
  
        // Etiqueta y campo para meta
        var etiqueCom = document.createElement('label');
        etiqueCom.innerHTML = 'Indicadores de éxito:';
        etiqueCom.classList.add('col-sm-2', 'col-form-label');
        kpiGrupo.appendChild(etiqueCom);
  
        var inputCom = document.createElement('textarea');
        inputCom.type = 'text';
        inputCom.name = 'indicadores[]';
        inputCom.classList.add('col-sm-10');
        inputCom.setAttribute('rows', '2');
        inputCom.setAttribute('required', 'required');
        kpiGrupo.appendChild(inputCom);   

      // Botón para eliminar el campo
      var btnDelete = document.createElement('button');
      btnDelete.innerHTML = 'X';
      btnDelete.classList.add('col-sm-1', 'btn', 'btn-danger', 'mt-2', 'float-end');
      btnDelete.onclick = function() {
      kpiContainer.removeChild(kpiGrupo);
    };
    
    kpiGrupo.appendChild(btnDelete);
    // Agregar el nuevo grupo al contenedor
    kpiContainer.appendChild(kpiGrupo);

  contakpiobj++;
}
    //=======================================