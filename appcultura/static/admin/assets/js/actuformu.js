var contadoresInputs = {};  // Objeto para almacenar contadores por contenedor
var contanewInput = {};
var contanewradio = {};
var contarlista = 0;

function addCampovar(contenedorID) {
    // Verificar si ya hay un contador para el contenedor
    if (!contadoresInputs[contenedorID]) {
        contadoresInputs[contenedorID] = 0;
    }

    // Incrementar el contador para darle un ID único a cada nuevo input
    contadoresInputs[contenedorID]++;

    var contenedorInputs = document.getElementById(contenedorID);

    var divRadios = document.createElement('div');
    divRadios.classList.add('d-none', 'form-control', 'mt-2'); // Inicialmente oculto

    var divcompleto = document.createElement('div');
    divcompleto.classList.add('row');

    var divrow = document.createElement('div');
    divrow.classList.add('col-11');

    var divdelete = document.createElement('div');
    divdelete.classList.add('col-1')

    // Crear un nuevo input de tipo texto
    var nuevoInputTexto = document.createElement('input');
    nuevoInputTexto.type = 'text';
    nuevoInputTexto.name = 'opcionesmul_' + contenedorID + '[]';
    nuevoInputTexto.placeholder = 'Nueva Opción';
    nuevoInputTexto.required = true;
    nuevoInputTexto.classList.add('form-control');

    // Botón para eliminar el input
    var btnEliminarInput = document.createElement('a');
    btnEliminarInput.type = 'button'
    btnEliminarInput.innerHTML = '<b>x</b>';
    btnEliminarInput.classList.add('btn', 'btn-warning', 'mt-1');
    btnEliminarInput.onclick = function() {
        // Eliminar el input y el botón
        divrow.removeChild(nuevoInputTexto);
        divdelete.removeChild(btnEliminarInput);
        contadoresInputs[contenedorID]--;  // Decrementar el contador al eliminar
    };

    divrow.appendChild(nuevoInputTexto);
    divdelete.appendChild(btnEliminarInput);

    divcompleto.appendChild(divrow);
    divcompleto.appendChild(divdelete);

    contenedorInputs.appendChild(divcompleto);
}

// aqui debe ir para varias respuestas 


function addVariasOpcion(idopcion) {

    var containern = document.getElementById(idopcion);
    if (!containern) {
        console.error("El contenedor con ID " + idopcion + " no se encontró.");
        return;
    }
    // Verificar si ya hay un contador para el contenedor
    if (!contanewInput[idopcion]) {
        contanewInput[idopcion] = 0;
    }

    // Incrementar el contador para darle un ID único a cada nuevo input
    contanewInput[idopcion]++;

    var divRadios = document.createElement('div');
    divRadios.classList.add('d-none', 'form-control', 'mt-2'); // Inicialmente oculto

    var divcompleto = document.createElement('div');
    divcompleto.classList.add('row');

    var divrowcheck = document.createElement('div');
    divrowcheck.classList.add('col-1', 'mt-3');

    var divrow = document.createElement('div');
    divrow.classList.add('col-10');

    var divdelete = document.createElement('div');
    divdelete.classList.add('col-1');

    // Crear un nuevo input de tipo texto
    var nuevoInputcheck = document.createElement('input');
    nuevoInputcheck.type = 'checkbox';
    nuevoInputcheck.name = 'checkval_' + idopcion;
    nuevoInputcheck.value = contanewInput[idopcion]; // Valor único
    nuevoInputcheck.classList.add('mt-2');

    // Crear un nuevo campo de texto
    var newTextocheck = document.createElement('input');
    newTextocheck.type = 'text';
    newTextocheck.name = 'cheknom_' + idopcion + '[]';
    newTextocheck.placeholder = 'Valor para la casilla';
    newTextocheck.required = true;
    newTextocheck.classList.add('form-control', 'mt-3');

    // Botón para eliminar el input
    var btnEliminarInput = document.createElement('a');
    btnEliminarInput.innerHTML = '<b>x</b>';
    btnEliminarInput.classList.add('btn', 'btn-warning', 'mt-1');
    btnEliminarInput.onclick = function () {
        // Eliminar el contenedor principal y decrementar el contador al eliminar
        divcompleto.remove();
        contanewInput[idopcion]--;
    };

    divrowcheck.appendChild(nuevoInputcheck);
    divrow.appendChild(newTextocheck);
    divdelete.appendChild(btnEliminarInput);

    divcompleto.appendChild(divrowcheck);
    divcompleto.appendChild(divrow);
    divcompleto.appendChild(divdelete);

    containern.appendChild(divcompleto);
}

// aqui codigo para una opcion con una opcion verdadera 
function addOneOpcion(idverdadera){
  console.log(idverdadera);
  var containern = document.getElementById(idverdadera);
    if (!containern) {
        console.error("El contenedor con ID " + idverdadera + " no se encontró.");
        return;
    }
    // Verificar si ya hay un contador para el contenedor
    if (!contanewradio[idverdadera]) {
      contanewradio[idverdadera] = 0;
    }

    // Incrementar el contador para darle un ID único a cada nuevo input
    contanewradio[idverdadera]++;

    var divRadios = document.createElement('div');
    divRadios.classList.add('d-none', 'form-control', 'mt-2'); // Inicialmente oculto

    var divcompleto = document.createElement('div');
    divcompleto.classList.add('row');

    var divrowcheck = document.createElement('div');
    divrowcheck.classList.add('col-1', 'mt-3');

    var divrow = document.createElement('div');
    divrow.classList.add('col-10');

    var divdelete = document.createElement('div');
    divdelete.classList.add('col-1');

    // Crear un nuevo input de tipo texto
    var nuevoInputcheck = document.createElement('input');
    nuevoInputcheck.type = 'radio';
    nuevoInputcheck.name = 'radionum_' + idverdadera;
    nuevoInputcheck.value = contanewradio[idverdadera]; // Valor único
    nuevoInputcheck.classList.add('mt-2');

    // Crear un nuevo campo de texto
    var newTextocheck = document.createElement('input');
    newTextocheck.type = 'text';
    newTextocheck.name = 'radioname_' + idverdadera + '[]';
    newTextocheck.placeholder = 'Valor para la casilla';
    newTextocheck.required = true;
    newTextocheck.classList.add('form-control', 'mt-3');

    // Botón para eliminar el input
    var btnEliminarInput = document.createElement('a');
    btnEliminarInput.innerHTML = '<b>x</b>';
    btnEliminarInput.classList.add('btn', 'btn-warning', 'mt-1');
    btnEliminarInput.onclick = function () {
        // Eliminar el contenedor principal y decrementar el contador al eliminar
        divcompleto.remove();
        contanewInput[idverdadera]--;
    };

    divrowcheck.appendChild(nuevoInputcheck);
    divrow.appendChild(newTextocheck);
    divdelete.appendChild(btnEliminarInput);

    divcompleto.appendChild(divrowcheck);
    divcompleto.appendChild(divrow);
    divcompleto.appendChild(divdelete);

    containern.appendChild(divcompleto);
 }

// Obtén el elemento del checkbox y la sección
var checkbox = document.getElementById('mostrarCampos');
var seccionCampos = document.getElementById('seccionCampos');

// Agrega un listener al evento de cambio del checkbox
checkbox.addEventListener('change', function() {
    // Muestra u oculta la sección según el estado del checkbox
    seccionCampos.style.display = checkbox.checked ? 'block' : 'none';
});
