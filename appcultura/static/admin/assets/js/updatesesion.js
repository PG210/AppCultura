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
      // Usar la función para obtener la fecha y hora actual
      let fechaActual = getFormattedDateTime();
      fechaInicio.value = fechaActual;
      fechaInicio.min = fechaActual; //restringir fechas diferentes a la actual
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

      //agregar fecha seleccionada en el input de fecini
      let newFecha;
       // Función para actualizar fechaFinal
      const actualizarFechaFinal = (fecha) => {
         fechaFinal.value = fecha; // Actualiza el valor de fechaFinal
         fechaFinal.min = fecha;
       };
       // Agregar el evento de cambio al input de fechaInicio
      agregarEventListenerFecha(fechaInicio).then((fecha) => {
         newFecha = fecha; // Asignar el valor a la variable
         actualizarFechaFinal(newFecha); // Actualiza fechaFinal
       });
        // Si deseas que se actualice cada vez que cambias la fecha en fechaInicio
      fechaInicio.addEventListener('change', function () {
         agregarEventListenerFecha(fechaInicio).then((fecha) => {
           newFecha = fecha; // Asignar el valor a la variable
           actualizarFechaFinal(newFecha); // Actualiza fechaFinal
         });
       });

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

//funcion para obtener la fecha actual
function getFormattedDateTime() {
  let now = new Date();
  let year = now.getFullYear();
  let month = ('0' + (now.getMonth() + 1)).slice(-2); // Mes en formato 2 dígitos
  let day = ('0' + now.getDate()).slice(-2); // Día en formato 2 dígitos
  let hours = '07'; // hora por defecto debe ser 7:00 Am
  let minutes = '00';
  // Formato 'YYYY-MM-DDTHH:MM' para el input 'datetime-local'
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

//funcion para obtener la fecha seleccionada en fechaInicio
function agregarEventListenerFecha(inputElement) {
  return new Promise((resolve) => {
    inputElement.addEventListener('change', function () {
      let fechaSeleccionada = inputElement.value; // Captura el valor del input
      let fecha = new Date(fechaSeleccionada); // Crea un objeto Date

      // Cambiar la hora a 6:00 PM (18:00)
      fecha.setHours(18, 0, 0, 0); // Establecer 18:00 horas

      // Formatear la nueva fecha a 'YYYY-MM-DDTHH:MM'
      let year = fecha.getFullYear();
      let month = (fecha.getMonth() + 1).toString().padStart(2, '0');
      let day = fecha.getDate().toString().padStart(2, '0');
      let hours = fecha.getHours().toString().padStart(2, '0');
      let minutes = fecha.getMinutes().toString().padStart(2, '0');

      // Nueva fecha con hora cambiada
      let nuevaFecha = `${year}-${month}-${day}T${hours}:${minutes}`;

      // Retornar la nueva fecha usando resolve
      resolve(nuevaFecha);
    });
  });
}
