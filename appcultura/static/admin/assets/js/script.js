   var contadorCampos = 1;
   var contaobjetivos =1;
   var contakpiobj = 1;
   var contadorTemas = 1;
   let editorcontarsesion = 1;

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
        nuevoGrupo.classList.add('mt-3', 'form-control', 'mb-8'); // Agregar la clase al grupo
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
        fechaInicio.setAttribute('required', 'required');
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
        fechaFinal.setAttribute('required', 'required');
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
        fechaFinal.setAttribute('required', 'required');
        nuevoGrupo.appendChild(inputLugar);

         // Botón para eliminar el campo
         var btnEliminarCampo = document.createElement('button');
        btnEliminarCampo.innerHTML = 'X';
        btnEliminarCampo.classList.add('col-sm-1', 'btn', 'btn-danger', 'mt-2', 'float-end');
        btnEliminarCampo.onclick = function() {
          formularioContainer.removeChild(nuevoGrupo);
        };

        nuevoGrupo.appendChild(btnEliminarCampo);
        // agregar nuevos campos para tematicas
        // Botón para agregar temáticas
        /*var btnTematicas = document.createElement('a');
        inputLugar.type = 'button';
        btnTematicas.innerHTML = 'Temas';
        btnTematicas.classList.add('col-sm-1', 'btn', 'btn-info', 'mt-2', 'float-end', 'me-2');
        btnTematicas.onclick = function() {
            agregarTematica(nuevoGrupo);
        };
        nuevoGrupo.appendChild(btnTematicas);
        */

        //================abrir modal ===============
        // Botón para abrir modal de temáticas
        var btnTematicas = document.createElement('button');
        btnTematicas.type = 'button';
        btnTematicas.innerHTML = 'Tematicas';
        btnTematicas.classList.add('col-sm-2', 'btn', 'btn-info', 'mt-2', 'float-end', 'me-2');
        btnTematicas.setAttribute('data-bs-toggle', 'modal');
        btnTematicas.setAttribute('data-bs-target', '#tematicasModal-' + contadorCampos); // ID único
        nuevoGrupo.appendChild(btnTematicas);
        //=====================================
        
        // Agregar el nuevo grupo al contenedor

        // Crear el modal para temáticas
        var modalTematicas = document.createElement('div');
        modalTematicas.classList.add('modal', 'fade');
        modalTematicas.id = 'tematicasModal-' + contadorCampos; // ID único para el modal
      
        // Contenido del modal para temáticas
        modalTematicas.innerHTML = `
                    <div class="modal-dialog modal-dialog-scrollable modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Agregar Temáticas</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                              <!-- Campos de entrada para temáticas -->
                              <div class="form-control">
                              <div class="row mb-3">
                                <label class="col-sm-2 col-form-label" for="tematicaInput_${contadorCampos}">Temática:</label>
                                <div class="col-sm-10">
                                  <input type="text" class="form-control" id="tematicaInput_${contadorCampos}"  name="tematicaInput_${contadorCampos}">
                                </div>
                              </div>
                              <div class="row mb-3">
                                <label class="col-sm-2 col-form-label" for="desInput_${contadorCampos}">Descripción:</label>
                                <div class="col-sm-10">
                                  <textarea class="form-control" id="desInput_${contadorCampos}" name="desInput_${contadorCampos}" rows="3"></textarea>
                                </div>
                              </div>
                              <div class="row mb-3">
                                <label class="col-sm-2 col-form-label" for="recur_${contadorCampos}">Recursos</label>
                                <div class="col-sm-10">
                                  <textarea class="form-control" id="recur_${contadorCampos}" name="recur_${contadorCampos}" rows="3"></textarea>
                                </div>
                              </div>
                              <div class="row mb-3">
                                <label class="col-sm-2 col-form-label" for="archivo_${contadorCampos}">Agregar archivo</label>
                                <div class="col-sm-10">
                                  <input type="file" class="form-control" name="archivo_${contadorCampos}" id="archivo_${contadorCampos}">
                                </div>
                              </div>
                              </div>
                           
                              <!-- Puedes agregar más campos aquí según tus necesidades -->
                            </div>
                            <div class="modal-footer">
                                <a type="button" class="btn btn-warning" data-bs-dismiss="modal"><i class="bi bi-check-square-fill"></i></a>
                            </div>
                        </div>
                    </div>
                `;

  // Agregar el modal al final del documento
  document.body.appendChild(modalTematicas);

  nuevoGrupo.appendChild(modalTematicas); //este agrega el modal al formulario de lo contrario no aparece
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
      btnDelete.classList.add('col-sm-1', 'btn', 'btn-outline-danger', 'btn-sm', 'mt-2', 'float-end');
      btnDelete.onclick = function() {
      kpiContainer.removeChild(kpiGrupo);
    };
    
    kpiGrupo.appendChild(btnDelete);
    // Agregar el nuevo grupo al contenedor
    kpiContainer.appendChild(kpiGrupo);

  contakpiobj++;
}
    //=======================================

    function editarsesion(){
      let containersesion = document.getElementById('contenedor-sesion');

      var nuevoGrupo = document.createElement('div');
        nuevoGrupo.classList.add('mt-3', 'form-control', 'mb-8'); // Agregar la clase al grupo
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
        fechaInicio.setAttribute('required', 'required');
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
        fechaFinal.setAttribute('required', 'required');
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
        fechaFinal.setAttribute('required', 'required');
        nuevoGrupo.appendChild(inputLugar);

        let labeltema = document.createElement('label');
        labeltema.innerHTML='Tema:';
        labeltema.classList.add('col-sm-2', 'col-form-label');
        nuevoGrupo.appendChild(labeltema);

        let inputtema =  document.createElement('input');
        inputtema.type = 'text';
        inputtema.name = 'tema[]';
        inputtema.classList.add('col-sm-10');
        inputtema.setAttribute('required', 'required');
        nuevoGrupo.appendChild(inputtema);

        let labeldescripcion = document.createElement('label');
        labeldescripcion.innerHTML='Descripcion:';
        labeldescripcion.classList.add('col-sm-2', 'col-form-label');
        nuevoGrupo.appendChild(labeldescripcion);

        let inputdescripcion =  document.createElement('textarea');
        inputdescripcion.type = 'text';
        inputdescripcion.name = 'descripcion[]';
        inputdescripcion.classList.add('col-sm-10');
        inputdescripcion.setAttribute('rows', '3');
        inputdescripcion.setAttribute('required', 'required');
        nuevoGrupo.appendChild(inputdescripcion);

        let labelrecursos = document.createElement('label');
        labelrecursos.innerHTML='Recursos:';
        labelrecursos.classList.add('col-sm-2', 'col-form-label');
        nuevoGrupo.appendChild(labelrecursos);

        let inputrecursos =  document.createElement('textarea');
        inputrecursos.type = 'text';
        inputrecursos.name = 'recursos[]';
        inputrecursos.classList.add('col-sm-10');
        inputrecursos.setAttribute('rows', '3');
        inputrecursos.setAttribute('required', 'required');
        nuevoGrupo.appendChild(inputrecursos);

        let labelarchivo = document.createElement('label');
        labelarchivo.innerHTML='Archivo:';
        labelarchivo.classList.add('col-sm-2', 'col-form-label');
        nuevoGrupo.appendChild(labelarchivo);

        let inputarchivo = document.createElement('input');
        inputarchivo.type = 'file';
        inputarchivo.name = 'archivo[]';
        inputarchivo.classList.add('col-sm-10');
        nuevoGrupo.appendChild(inputarchivo);

         // Botón para eliminar el campo
         var btnEliminarCampo = document.createElement('button');
        btnEliminarCampo.innerHTML = 'X';
        btnEliminarCampo.classList.add('col-sm-1', 'btn', 'btn-danger', 'mt-2', 'float-end');
        btnEliminarCampo.onclick = function() {
          formularioContainer.removeChild(nuevoGrupo);
        };

        nuevoGrupo.appendChild(btnEliminarCampo);

        // Agregar el nuevo grupo al contenedor
        containersesion.appendChild(nuevoGrupo);
 
        editorcontarsesion++;

    }