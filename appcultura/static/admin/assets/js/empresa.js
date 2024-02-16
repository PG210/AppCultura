let contarsucursal=1;
let contaarea=1;
let contadepto=1;

function agregarSucursal() {
  let sucursalContainer = document.getElementById('contenedor-sucursals');

  let sucursalGrupo = document.createElement('div');
  sucursalGrupo.classList.add('mt-2');

  //==================================================
  var divsucursalCom = document.createElement('div');
  divsucursalCom.classList.add('row');

  var divSucur = document.createElement('div');
  divSucur.classList.add('col-12');

  //================================================
  var divcompleto = document.createElement('div');
  divcompleto.classList.add('row');

  var divdir = document.createElement('div');
  divdir.classList.add('col-6');

  var divnit = document.createElement('div');
  divnit.classList.add('col-6')
  // ========================para correo y telefono ========
  var divcompleto2 = document.createElement('div');
  divcompleto2.classList.add('row');

  var divemail = document.createElement('div');
  divemail.classList.add('col-6');

  var divtel = document.createElement('div');
  divtel.classList.add('col-6')
  // ========================para sector y tamanio ========
  var divcompleto3 = document.createElement('div');
  divcompleto3.classList.add('row');

  var divsector = document.createElement('div');
  divsector.classList.add('col-6');

  var divtamanio = document.createElement('div');
  divtamanio.classList.add('col-6')

  //=========================Nombre de la sucursal
  let labelNombre = document.createElement('label');
  labelNombre.innerHTML = 'Nombre Sucursal:';
  labelNombre.classList.add('col-form-label');
  divSucur.appendChild(labelNombre);
  
  //Input Nombre de la sucursal
  let inputNombre = document.createElement('input');
  inputNombre.type = 'text';
  inputNombre.name = 'nameSucursal[]';
  inputNombre.classList.add('form-control');
  inputNombre.setAttribute('required', 'required');
  divSucur.appendChild(inputNombre);

  divsucursalCom.appendChild(divSucur);
  sucursalGrupo.appendChild(divsucursalCom);
  
  //NIT de la sucursal
  let labelNit = document.createElement('label');
  labelNit.innerHTML = 'NIT:';
  labelNit.classList.add('col-form-label');
  divnit.appendChild(labelNit);

  //Input NIT de la sucursal
  let inputNit = document.createElement('input');
  inputNit.type = 'text';
  inputNit.name = 'nameNit[]';
  inputNit.classList.add('form-control');
	divnit.appendChild(inputNit);

  //Direccion de la sucursal
  let labelDireccion = document.createElement('label');
  labelDireccion.innerHTML = 'Direccion:';
  labelDireccion.classList.add('col-form-label');
  divdir.appendChild(labelDireccion);
  //sucursalGrupo.appendChild(labelDireccion);

  //Input Direccion de la sucursal
  let inputDireccion = document.createElement('input');
  inputDireccion.type = 'text';
  inputDireccion.name = 'nameDireccion[]';
  inputDireccion.classList.add('form-control');
  inputDireccion.setAttribute('required', 'required');
  divdir.appendChild(inputDireccion);

  //agregar
  divcompleto.appendChild(divnit);
  divcompleto.appendChild(divdir);
  sucursalGrupo.appendChild(divcompleto);

  //Correo de la sucursal
  let labelCorreo = document.createElement('label');
  labelCorreo.innerHTML = 'Correo:';
  labelCorreo.classList.add('col-form-label');
  divemail.appendChild(labelCorreo);
  //sucursalGrupo.appendChild(labelCorreo);

  //Input Correo de la sucursal
  let inputCorreo = document.createElement('input');
  inputCorreo.type = 'text';
  inputCorreo.name = 'nameCorreo[]';
  inputCorreo.classList.add('form-control');
  inputCorreo.setAttribute('required', 'required');
  divemail.appendChild(inputCorreo);
  //sucursalGrupo.appendChild(inputCorreo);

  //Telefono de la sucursal
  let labelTelefono = document.createElement('label');
  labelTelefono.innerHTML = 'Telefono:';
  labelTelefono.classList.add('col-form-label');
  divtel.appendChild(labelTelefono);

  //Input Telefono de la sucursal
  let inputTelefono = document.createElement('input');
  inputTelefono.type = 'text';
  inputTelefono.name = 'nameTelefono[]';
  inputTelefono.classList.add('form-control');
  inputTelefono.setAttribute('required', 'required');
  divtel.appendChild(inputTelefono);

  divcompleto2.appendChild(divemail);
  divcompleto2.appendChild(divtel);
  sucursalGrupo.appendChild(divcompleto2);

  //Sector de la sucursal
  
  let labelSector = document.createElement('label');
  labelSector.innerHTML = 'Sector:';
  labelSector.classList.add('col-form-label');
  divsector.appendChild(labelSector);

  //Input Sector de la sucursal
  let selectSector = document.createElement('select');
  selectSector.classList.add('form-control');
  selectSector.name = 'nameSector[]';
  selectSector.setAttribute('required', 'required');
  divsector.appendChild(selectSector);
  //options

  let datos = [
  { value: '1', label: 'Comercio'},
  { value: '2', label: 'Industria' },
  { value: '3', label: 'Servicios' },
  { value: '4', label: 'Construcción' },
  { value: '5', label: 'Transporte' },
];

	// Agregar opciones al select
	datos.forEach(opcion => {
	  let option = document.createElement('option');
	  option.value = opcion.value;
	  option.text = opcion.label;
	  selectSector.add(option);
	});

  //Tamaño de la sucursal
  let labelTamanio = document.createElement('label');
  labelTamanio.innerHTML = 'Tamaño:';
  labelTamanio.classList.add('col-form-label');
  divtamanio.appendChild(labelTamanio);
  
  //Input Tamaño de la sucursal
  let selectTamanio = document.createElement('select');
  selectTamanio.classList.add('form-control');
  selectTamanio.name = 'nameTamanio[]';
  selectTamanio.setAttribute('required', 'required');
  divtamanio.appendChild(selectTamanio);
  //options

  let datostam = [
  { value: '1', label: '1 - 10 Empleados' },
  { value: '2', label: '11 - 25 Empleados' },
];

	// Agregar opciones al select
	datostam.forEach(opcion => {
	  let option = document.createElement('option');
	  option.value = opcion.value;
	  option.text = opcion.label;
	  selectTamanio.add(option);
	});

  divcompleto3.appendChild(divsector);
  divcompleto3.appendChild(divtamanio);
  sucursalGrupo.appendChild(divcompleto3);

  // Botón para eliminar el campo
  let btnDelete = document.createElement('button');
  btnDelete.innerHTML = 'X';
  btnDelete.classList.add('btn', 'btn-danger', 'btn-sm', 'mt-2', 'float-end');
  btnDelete.onclick = function () {
    sucursalContainer.removeChild(sucursalGrupo);
  };

  sucursalGrupo.appendChild(btnDelete);
  // Agregar el nuevo grupo al contenedor
  sucursalContainer.appendChild(sucursalGrupo);

  contarsucursal++;
}

// Funcion agregar Dpartamentos
function agregardepto() {
  
  const deptoContainer = document.getElementById('contenedor-deptos');

  // Crear un nuevo grupo de inputs
  let deptoGrupo = document.createElement('div');
  deptoGrupo.classList.add('mt-3', 'form-control'); // Agregar la clase al grupo
  // Crear tres inputs y agregarlos al grupo

  // Etiqueta y campo para la fecha de inicio
  let labelnombre = document.createElement('label');
  labelnombre.innerHTML = 'Nombre de Departamento:';
  labelnombre.classList.add('col-sm-2', 'col-form-label');
  deptoGrupo.appendChild(labelnombre);

  let desarea = document.createElement('input');
  desarea.type = 'text';
  desarea.name = 'nomdepto[]';
  desarea.classList.add('col-sm-10');
  desarea.setAttribute('required', 'required');
  deptoGrupo.appendChild(desarea);

  // Etiqueta y campo para lugar
  let labeldescrip = document.createElement('label');
  labeldescrip.innerHTML = 'Descripción:';
  labeldescrip.classList.add('col-sm-2', 'col-form-label');
  deptoGrupo.appendChild(labeldescrip);

  let inputDes = document.createElement('textarea');
  inputDes.type = 'text';
  inputDes.name = 'desdepto[]';
  inputDes.classList.add('col-sm-10');
  inputDes.setAttribute('rows', '3');
  inputDes.setAttribute('required', 'required');
  deptoGrupo.appendChild(inputDes);

   // Botón para eliminar el campo
   let btnDelete = document.createElement('button');
   btnDelete.innerHTML = 'X';
   btnDelete.classList.add('col-sm-1', 'btn', 'btn-danger', 'mt-2', 'float-end');
   btnDelete.onclick = function() {
    deptoContainer.removeChild(deptoGrupo);
  };
  deptoGrupo.appendChild(btnDelete);
  // Agregar el nuevo grupo al contenedor
  deptoContainer.appendChild(deptoGrupo);

contadepto++;
}

//Funcion agregar areas
function guardararea(){
  const name = document.getElementById('inputnombre');
  const description = document.getElementById('inputdes');
  const selectarea = document.getElementById("selectarea");

  let optionarea = document.createElement('option');
  optionarea.selected = true;
  optionarea.text=name.value;
  selectarea.add(optionarea);
}

function MostrarOcultarform() {
  const checkbox = document.getElementById("checkdepto");
  const containerdepto = document.getElementById("accordionExample");

  containerdepto.style.display = checkbox.checked ? 'block' : 'none';
}



//Funcion para hacer una apiFetch a la base de datos

function llamaroptions(){
	fetch('administracion/empresa/api')
	.then(response => response.json())
	.then(data => {
		console.log(data);
		data.forEach(item =>{
			console.log(item);
		});
	})
	//.catch(error => console.error('No se pudo acceder a los datos', error));
}
/*
function mostrarAreas(){
  document.getElementById('formulario-empresa').addEventListener('submit', function (event){
    event.preventDefault();

    let empresaId = document.getElementById('selectEmp');

    fetch(`administracion/empresa/obtener-areas/${empresaId}/`)
    .then(response => response.json())
    .then(data => {
      console.log(data);
      data.forEach(area => {
        console.log(area.id);
        console.log(area.nombre)
    });
  })
  .catch(error => {
    console.error('Error en la solicitud fetch', error);
  });
  });
}
*/

function copiarlink(texto){

  
  const btn = document.getElementById('btnlink');

  console.log(texto);

  let areaDeTexto = document.createElement("textarea");
  areaDeTexto.value = texto;

  // Agregar el área de texto al DOM
  document.body.appendChild(areaDeTexto);

  // Seleccionar y copiar el texto
  areaDeTexto.select();
  document.execCommand("copy");

  // Eliminar el área de texto
  document.body.removeChild(areaDeTexto);
  
  Swal.fire({
    icon: 'success',
    title: 'Copiado exitoso',
    text:'Enlace copiado',
  });


  // Puedes agregar aquí lógica adicional, como mostrar un mensaje de éxito
  //alert("Texto copiado al portapapeles: " + texto);

}