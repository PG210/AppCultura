let contarsucursal=1;

function agregarSucursal() {
  let sucursalContainer = document.getElementById('contenedor-sucursals');

  let sucursalGrupo = document.createElement('div');
  sucursalGrupo.classList.add('mt-3', 'form-control');

  //Nombre de la sucursal
  let labelNombre = document.createElement('label');
  labelNombre.innerHTML = 'Nombre Sucursal:';
  labelNombre.classList.add('col-sm-2', 'col-form-label');
  sucursalGrupo.appendChild(labelNombre);

  //Input Nombre de la sucursal
  let inputNombre = document.createElement('input');
  inputNombre.type = 'text';
  inputNombre.name = 'nameSucursal[]';
  inputNombre.classList.add('col-sm-10');
  inputNombre.setAttribute('required', 'required');
  sucursalGrupo.appendChild(inputNombre);
  
  //NIT de la sucursal
  let labelNit = document.createElement('label');
  labelNit.innerHTML = 'NIT:';
  labelNit.classList.add('col-sm-2', 'col-form-label');
  sucursalGrupo.appendChild(labelNit);

  //Input NIT de la sucursal
  let inputNit = document.createElement('input');
  inputNit.type = 'text';
  inputNit.name = 'nameNit[]';
  inputNit.classList.add('col-sm-10');
  inputNit.setAttribute('required', 'required');
  sucursalGrupo.appendChild(inputNit);
	
  //Direccion de la sucursal
  let labelDireccion = document.createElement('label');
  labelDireccion.innerHTML = 'Direccion:';
  labelDireccion.classList.add('col-sm-2', 'col-form-label');
  sucursalGrupo.appendChild(labelDireccion);

  //Input Direccion de la sucursal
  let inputDireccion = document.createElement('input');
  inputDireccion.type = 'text';
  inputDireccion.name = 'nameDireccion[]';
  inputDireccion.classList.add('col-sm-10');
  inputDireccion.setAttribute('required', 'required');
  sucursalGrupo.appendChild(inputDireccion);

  //Correo de la sucursal
  let labelCorreo = document.createElement('label');
  labelCorreo.innerHTML = 'Correo:';
  labelCorreo.classList.add('col-sm-2', 'col-form-label');
  sucursalGrupo.appendChild(labelCorreo);

  //Input Correo de la sucursal
  let inputCorreo = document.createElement('input');
  inputCorreo.type = 'text';
  inputCorreo.name = 'nameCorreo[]';
  inputCorreo.classList.add('col-sm-10');
  inputCorreo.setAttribute('required', 'required');
  sucursalGrupo.appendChild(inputCorreo);

  //Telefono de la sucursal
  let labelTelefono = document.createElement('label');
  labelTelefono.innerHTML = 'Telefono:';
  labelTelefono.classList.add('col-sm-2', 'col-form-label');
  sucursalGrupo.appendChild(labelTelefono);

  //Input Telefono de la sucursal
  let inputTelefono = document.createElement('input');
  inputTelefono.type = 'text';
  inputTelefono.name = 'nameTelefono[]';
  inputTelefono.classList.add('col-sm-10');
  inputTelefono.setAttribute('required', 'required');
  sucursalGrupo.appendChild(inputTelefono);

  /*
  //Grupo Empresarial de la sucursal
  let labelGrpEmp = document.createElement('label');
  labelGrpEmp.innerHTML = 'Grupo Empresarial:';
  labelGrpEmp.classList.add('col-sm-2', 'col-form-label');
  sucursalGrupo.appendChild(labelGrpEmp);

  //Input Grupo empresarial de la sucursal
  let inputGrpEmp = document.createElement('input');
  inputGrpEmp.type = 'text';
  inputGrpEmp.name = 'nameGrpEmp[]';
  inputGrpEmp.classList.add('col-sm-10');
  inputGrpEmp.setAttribute('required', 'required');
  sucursalGrupo.appendChild(inputGrpEmp);
	*/

  //Sector de la sucursal
  let labelSector = document.createElement('label');
  labelSector.innerHTML = 'Sector:';
  labelSector.classList.add('col-sm-2', 'col-form-label');
  sucursalGrupo.appendChild(labelSector);

  //Input Sector de la sucursal
  let selectSector = document.createElement('select');
  selectSector.classList.add('form-select');
  selectSector.classList.add('col-sm-8');
  selectSector.name = 'nameSector[]';
  selectSector.setAttribute('required', 'required');
  //options
  sucursalGrupo.appendChild(selectSector);

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
  labelTamanio.classList.add('col-sm-2', 'col-form-label');
  sucursalGrupo.appendChild(labelTamanio);

  //Input Tamaño de la sucursal
  let selectTamanio = document.createElement('select');
  selectTamanio.classList.add('form-select');
  selectTamanio.classList.add('col-sm-8');
  selectTamanio.name = 'nameTamanio[]';
  selectTamanio.setAttribute('required', 'required');
  //options
  sucursalGrupo.appendChild(selectTamanio);

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
/*
Funcion para hacer una apiFetch a la base de datos

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
*/