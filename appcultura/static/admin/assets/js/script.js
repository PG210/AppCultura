var contadorCampos = 1;
var contaobjetivos = 1;
var contarsucursal = 1;

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
  btnEliminarCampo.onclick = function () {
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
  btnDelete.onclick = function () {
    objetivosContainer.removeChild(objetivosGrupo);
  };

  objetivosGrupo.appendChild(btnDelete);
  // Agregar el nuevo grupo al contenedor
  objetivosContainer.appendChild(objetivosGrupo);

  contaobjetivos++;
}

function agregarSucursal() {
  let sucursalContainer = document.getElementById('contenedor-sucursal');

  let sucursalGrupo = document.createElement('div');
  sucursalGrupo.classList.add('mt-3', 'form-control');

  let labelNombre = document.createElement('label');
  labelNombre.innerHTML = 'Nombre Sucursal:';
  labelNombre.classList.add('col-sm-2', 'col-form-label');
  sucursalGrupo.appendChild(labelNombre);

  let inputNombre = document.createElement('input');
  inputNombre.type = 'text';
  inputNombre.name = 'nameSucursal[]';
  inputNombre.classList.add('col-sm-10');
  inputNombre.setAttribute('required', 'required');
  sucursalGrupo.appendChild(inputNombre);

  // Botón para eliminar el campo
  let btnDelete = document.createElement('button');
  btnDelete.innerHTML = 'X';
  btnDelete.classList.add('col-sm-1', 'btn', 'btn-danger', 'mt-2', 'float-end');
  btnDelete.onclick = function () {
    sucursalContainer.removeChild(sucursalGrupo);
  };

  sucursalGrupo.appendChild(btnDelete);
  // Agregar el nuevo grupo al contenedor
  sucursalContainer.appendChild(sucursalGrupo);

  contarsucursal++;
}

function eliminarEmpresa(){
  const btnEliminar = document.getElementById("btnBorrar");
  let opc = confirm("Esta Seguro que desea eliminar este registro?");
  if (opc == true){
    alert("Su registro ha sido borrado satisfactoriamente");
  } 
}