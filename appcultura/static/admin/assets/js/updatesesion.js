var contadorCampos = 1;
var contadorTemas = 1;
var contaobjetivos = 1;
let editorcontarsesion = 1;

function editarsesion() {
    var formularioContainer = document.getElementById('contenedor-sesion');
      // Crear un nuevo grupo de inputs
      var nuevoGrupo = document.createElement('div');
      nuevoGrupo.classList.add('mt-3', 'mb-8'); // Agregar la clase al grupo
      // Crear tres inputs y agregarlos al grupo
      var lineaHorizontal = document.createElement('hr');
      lineaHorizontal.classList.add('mt-2');
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
      btnEliminarCampo.innerHTML = '<i class="bi bi-x-circle-fill"></i>';
      btnEliminarCampo.classList.add('btn', 'btn-outline-danger', 'btn-sm', 'mt-2', 'float-end');
      btnEliminarCampo.onclick = function() {
        formularioContainer.removeChild(nuevoGrupo);

      };

      nuevoGrupo.appendChild(btnEliminarCampo);
     
      //================abrir modal ===============
      // Botón para abrir modal de temáticas
      var btnTematicas = document.createElement('button');
      btnTematicas.type = 'button';
      btnTematicas.innerHTML = 'Tematicas';
      btnTematicas.classList.add('btn', 'btn-outline-primary', 'btn-sm', 'mt-2', 'float-end', 'me-2');
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
nuevoGrupo.appendChild(lineaHorizontal);
formularioContainer.appendChild(nuevoGrupo);


contadorCampos++;
}
 
//============== funcion para objetivos =============
function agregarObjetivo() {
    var objetivosContainer = document.getElementById('contenedor-objetivos');

    // Crear un nuevo grupo de inputs
    var objetivosGrupo = document.createElement('div');
    objetivosGrupo.classList.add('mt-3'); // Agregar la clase al grupo
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
     btnDelete.innerHTML = '<i class="bi bi-x-circle-fill"></i>';
     btnDelete.classList.add('btn', 'btn-outline-danger', 'btn-sm', 'mt-2', 'float-end');
     btnDelete.onclick = function() {
      objetivosContainer.removeChild(objetivosGrupo);
    };
    objetivosGrupo.appendChild(btnDelete);
    // Agregar el nuevo grupo al contenedor
    var lineaHorizontal = document.createElement('hr');
    objetivosGrupo.appendChild(lineaHorizontal);//crear linea horizontal despues del boton eliminar
    objetivosContainer.appendChild(objetivosGrupo);

  contaobjetivos++;
}