var contakpiobj = 0;

function agregarCampo() {
    var contenedor = document.getElementById('contenedor-formulario');

    // Crear una nueva fila (div con clase "row")
    var nuevaFila = document.createElement('div');
    nuevaFila.classList.add('row', 'mt-3', 'borderdiv');

    // Asignar un ID único a la fila
    var filaId = 'fila' + contakpiobj;
    nuevaFila.id = filaId;

    // Columna 1: Pregunta (input de texto)
    var columna1 = document.createElement('div');
    columna1.classList.add('col-5');

    //crear columna para el valor 
    var columna15 = document.createElement('div');
    columna15.classList.add('col-2');

    //fila para las respuestas
    var respuestas = document.createElement('div');
    respuestas.classList.add('col-12');

    var divForm = document.createElement('div');
    divForm.classList.add('form');

    var inputPregunta = document.createElement('input');
    inputPregunta.type = 'text';
    inputPregunta.name = 'pregunta_' + filaId;
    inputPregunta.placeholder = 'Pregunta';
    inputPregunta.required = true;
    inputPregunta.classList.add('form-control'); // Agregar la clase al input
    
    var labelNombre = document.createElement('label');
    labelNombre.classList.add('lbl-nombre');

    var spanTextNombre = document.createElement('span');
    spanTextNombre.classList.add('text-nomb');

    labelNombre.appendChild(spanTextNombre);
    divForm.appendChild(inputPregunta);
    divForm.appendChild(labelNombre);

    columna1.appendChild(divForm);

    //crear input para aagregar valor por cada pregunta
    var valorPregunta = document.createElement('input');
    valorPregunta.type = 'number';
    valorPregunta.name = 'valorpreg_' + filaId;
    valorPregunta.placeholder = '0 puntos';
    valorPregunta.required = true;
    valorPregunta.min = '1';
    valorPregunta.classList.add('form-control', 'mt-3'); // Agregar la clase al input

    columna15.appendChild(valorPregunta);
    // Columna 2: Tipo de formulario (select)
    var columna2 = document.createElement('div');
    columna2.classList.add('col-4');

    var selectTipoFormulario = document.createElement('select');
    selectTipoFormulario.classList.add('form-select', 'mt-3');
    selectTipoFormulario.name = 'tipoform_' + filaId;
    selectTipoFormulario.setAttribute('aria-label', 'Default select example');

    var opciones = [
        { value: 0, text: 'Tipo de formulario' },
        { value: 1, text: 'Respuesta corta' },
        { value: 2, text: 'Párrafo' },
        { value: 3, text: 'Encuesta'},
        { value: 5, text: 'Opciones multiples'},
        { value: 6, text: 'Compromiso'},
    ];

    for (var i = 0; i < opciones.length; i++) {
        var opcion = document.createElement('option');
        opcion.value = opciones[i].value;
        opcion.text = opciones[i].text;
        selectTipoFormulario.appendChild(opcion);
    }

    // Contenedor para el mensaje de Respuesta corta
    var divRespuestaCorta = document.createElement('div');
    divRespuestaCorta.innerHTML = 'Respuesta corta ___________________________________________________________________________________';
    divRespuestaCorta.classList.add('form-control', 'mt-3', 'd-none'); // Inicialmente oculto
    
    //contenedor para compromiso
    var divCompromiso = document.createElement('div');
    divCompromiso.classList.add('form-control', 'mt-3', 'd-none'); // Inicialmente oculto

    //crear campos para contenedor
    var divAtributosCompromiso = document.createElement('div');
    divAtributosCompromiso.innerHTML = 'Compromiso:  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ ';
    divAtributosCompromiso.classList.add('form-control', 'mt-2');
    divCompromiso.appendChild(divAtributosCompromiso);
    
    var divAtributosPrioridad = document.createElement('div');
    divAtributosPrioridad.innerHTML = 'Priordidad:  _ _ _ _ _ _ _ _ _ _ _ _ _  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ ';
    divAtributosPrioridad.classList.add('form-control', 'mt-2');
    divCompromiso.appendChild(divAtributosPrioridad);
    
    var divAtributosFecha = document.createElement('div');
    divAtributosFecha.innerHTML = 'Fecha final:  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _  ';
    divAtributosFecha.classList.add('form-control', 'mt-2');
    divCompromiso.appendChild(divAtributosFecha);
    
    var divAtributosConquien = document.createElement('div');
    divAtributosConquien.innerHTML = '¿Con quién?:  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ ';
    divAtributosConquien.classList.add('form-control', 'mt-2');
    divCompromiso.appendChild(divAtributosConquien);

    // Contenedor para el mensaje de Respuesta Larga
    var divRespuestaLarga = document.createElement('div');
    divRespuestaLarga.innerHTML = 'Respuesta larga __________________________________________________________________________________________________________________________________________________________________________________________________';
    divRespuestaLarga.classList.add('form-control', 'mt-3', 'd-none'); // Inicialmente oculto

    //crear contenedor para los input de eleccion multiple
    var divRadios = document.createElement('div');
    divRadios.classList.add('d-none', 'form-control', 'mt-2'); // Inicialmente oculto

    var divcompleto = document.createElement('div');
    divcompleto.classList.add('row');

    var divrow = document.createElement('div');
    divrow.classList.add('col-11');

    var divdelete = document.createElement('div');
    divdelete.classList.add('col-1')

    //crear contendeor para las opciones multiple con unica respuesta
    var divopmultiple = document.createElement('div');
    divopmultiple.classList.add('d-none', 'form-control', 'mt-2'); // Inicialmente oculto

    var divrowmultiple = document.createElement('div');
    divrowmultiple.classList.add('row');

    var filaradios = document.createElement('div');
    filaradios.classList.add('col-2');

    var filaradiosinput = document.createElement('div');
    filaradiosinput.classList.add('col-9');

    var filadeleteradios = document.createElement('div');
    filadeleteradios.classList.add('col-1')
    //crear contenedor para nuevos campos de seleccion multiple con varias respuestas

    var divopmultiple2 = document.createElement('div');
    divopmultiple2.classList.add('d-none', 'form-control', 'mt-2'); // Inicialmente oculto

    var divrowmultiple2 = document.createElement('div');
    divrowmultiple2.classList.add('row');

    var filaradios2 = document.createElement('div');
    filaradios2.classList.add('col-2');

    var filaradiosinput2 = document.createElement('div');
    filaradiosinput2.classList.add('col-9');

    var filadeleteradios2 = document.createElement('div');
    filadeleteradios2.classList.add('col-1')
    // Función para agregar nuevo campo de texto
    function agregarInputTexto() {
        // Crear un nuevo input de tipo texto
        var nuevoInputTexto = document.createElement('input');
        nuevoInputTexto.type = 'text';
        nuevoInputTexto.name = 'opciones_' + filaId + '[]';
        nuevoInputTexto.placeholder = 'Nueva Opción';
        nuevoInputTexto.required = true;
        nuevoInputTexto.classList.add('form-control', 'mt-3');

        // Botón para eliminar el input
        var btnEliminarInput = document.createElement('a');
        btnEliminarInput.type = 'button'
        btnEliminarInput.innerHTML = '<i class="bi bi-trash3-fill"></i>';
        btnEliminarInput.classList.add('btn', 'btn-danger', 'mt-3');
        btnEliminarInput.onclick = function() {
            // Eliminar el input y el botón
            divrow.removeChild(nuevoInputTexto);
            divdelete.removeChild(btnEliminarInput);
        };

        // Agregar el input y el botón al contenedor
        divrow.appendChild(nuevoInputTexto);
        divdelete.appendChild(btnEliminarInput);

        divcompleto.appendChild(divrow);
        divcompleto.appendChild(divdelete);

        divRadios.appendChild(divcompleto);
    }

    //crear la funcion agregar radius
    var containput = 1;
    function agregarradios() {
        // Crear un nuevo input de tipo texto
        // Crear un nuevo elemento radio
        var nuevoInputRadio = document.createElement('input');
        nuevoInputRadio.type = 'radio';
        nuevoInputRadio.name = 'radionum_'+ filaId;
        nuevoInputRadio.value = containput; // Valor único
         // Crear un nuevo campo de texto
        var newTextoradio = document.createElement('input');
        newTextoradio.type = 'text';
        newTextoradio.name = 'radioname_' + filaId + '[]';
        newTextoradio.placeholder = 'Valor para la opción';
        newTextoradio.required = true;
        newTextoradio.classList.add('form-control', 'mt-3');
        // Crear una nueva etiqueta label
        var nuevoLabel = document.createElement('label');
        nuevoLabel.innerHTML = 'Elegir ';
        nuevoLabel.classList.add('mt-3', 'form-control');
        nuevoLabel.appendChild(nuevoInputRadio);
       
        // Botón para eliminar el input
        var btnEliminarradio = document.createElement('a');
        btnEliminarradio.type = 'button'
        btnEliminarradio.innerHTML = '<i class="bi bi-trash3-fill"></i>';
        btnEliminarradio.classList.add('btn', 'btn-danger', 'mt-3');
        btnEliminarradio.onclick = function() {
            // Eliminar el input y el botón
            filaradios.removeChild(nuevoLabel);
            filaradiosinput.removeChild(newTextoradio);
            filadeleteradios.removeChild(btnEliminarradio);
        };

        // Agregar el input y el botón al contenedor
        filaradios.appendChild(nuevoLabel);
        filaradiosinput.appendChild(newTextoradio);
        filadeleteradios.appendChild(btnEliminarradio);

        divrowmultiple.appendChild(filaradios);
        divrowmultiple.appendChild(filaradiosinput);
        divrowmultiple.appendChild(filadeleteradios);

        divopmultiple.appendChild(divrowmultiple);
        containput++;
    }

    //funcion para agregar check list
    var contarcheck = 1;
    function agregarcheclist() {
        // Crear un nuevo elemento radio
        var nuevoInputcheck = document.createElement('input');
        nuevoInputcheck.type = 'checkbox';
        nuevoInputcheck.name = 'checkval_'+ filaId;
        nuevoInputcheck.value = contarcheck; // Valor único
         // Crear un nuevo campo de texto
        var newTextocheck = document.createElement('input');
        newTextocheck.type = 'text';
        newTextocheck.name = 'cheknom_' + filaId + '[]';
        newTextocheck.placeholder = 'Valor para la casilla';
        newTextocheck.required = true;
        newTextocheck.classList.add('form-control', 'mt-3');
        // Crear una nueva etiqueta label
        var nuevoLabelckec = document.createElement('label');
        nuevoLabelckec.innerHTML = 'Elegir ';
        nuevoLabelckec.classList.add('mt-3', 'form-control');
        nuevoLabelckec.appendChild(nuevoInputcheck);
       
        // Botón para eliminar el input
        var btnEliminarcheck = document.createElement('a');
        btnEliminarcheck.type = 'button'
        btnEliminarcheck.innerHTML = '<i class="bi bi-trash3-fill"></i>';
        btnEliminarcheck.classList.add('btn', 'btn-danger', 'mt-3');
        btnEliminarcheck.onclick = function() {
            // Eliminar el input y el botón
            filaradios2.removeChild(nuevoLabelckec);
            filaradiosinput2.removeChild(newTextocheck);
            filadeleteradios2.removeChild(btnEliminarcheck);
        };

        // Agregar el input y el botón al contenedor
        filaradios2.appendChild(nuevoLabelckec);
        filaradiosinput2.appendChild(newTextocheck);
        filadeleteradios2.appendChild(btnEliminarcheck);

        divrowmultiple2.appendChild(filaradios2);
        divrowmultiple2.appendChild(filaradiosinput2);
        divrowmultiple2.appendChild(filadeleteradios2);

        divopmultiple2.appendChild(divrowmultiple2);
        contarcheck++;
    }
    // Botón adicional para Varias opciones
    var btnAgregarOpcion = document.createElement('a');
    btnAgregarOpcion.type = 'button'
    btnAgregarOpcion.innerHTML = 'Agregar Opción';
    btnAgregarOpcion.classList.add('btn', 'btn-success', 'mt-3', 'd-none'); // Inicialmente oculto
    
    //crear boton para agregar multiples opciones con una verdadera
    var btnAgregar2 = document.createElement('a');
    btnAgregar2.type = 'button'
    btnAgregar2.innerHTML = 'Agregar Opción';
    btnAgregar2.classList.add('btn', 'btn-success', 'mt-3', 'd-none'); // Inicialmente oculto

    //crear boton para agregar multiples campos con varias opciones correctas
    var btnAgregar3 = document.createElement('a');
    btnAgregar3.type = 'button'
    btnAgregar3.innerHTML = 'Agregar Opción';
    btnAgregar3.classList.add('btn', 'btn-success', 'mt-3', 'd-none'); // Inicialmente oculto

    // Función para agregar nuevo campo de texto al hacer clic en "Agregar Opción"
    btnAgregarOpcion.onclick = agregarInputTexto;
    //llamar a la funcion crear nuevo input de option al hacer click
    btnAgregar2.onclick = agregarradios;
    //llamar a la funcion para creear nuevos campos con multiples respuestas correctas
    btnAgregar3.onclick = agregarcheclist;


    columna2.appendChild(selectTipoFormulario);
    respuestas.appendChild(divRespuestaCorta);
    respuestas.appendChild(divRespuestaLarga);
    respuestas.appendChild(divRadios);
    respuestas.appendChild(divopmultiple); //agregar el formulario para que se vea en la vista
    respuestas.appendChild(divopmultiple2); //agregar contenedor de multiples respuestas
    respuestas.appendChild(btnAgregarOpcion);
    respuestas.appendChild(btnAgregar2); //se agrega el boton al div
    respuestas.appendChild(btnAgregar3);
    respuestas.appendChild(divCompromiso);//agregar compromisos 
    
    // Agregar evento de escucha al select
    selectTipoFormulario.addEventListener('change', function() {
        // Mostrar u ocultar elementos adicionales según la opción seleccionada
        var valorSeleccionado = selectTipoFormulario.value;

        // Obtener el ID de la fila actual
        var filaId = nuevaFila.id;

        // Ocultar todos los elementos adicionales
        divRespuestaCorta.classList.add('d-none');
        divRespuestaLarga.classList.add('d-none');
        btnAgregarOpcion.classList.add('d-none'); // Ocultar el botón por defecto
        btnAgregar2.classList.add('d-none'); //ocultar boton por defecto
        btnAgregar3.classList.add('d-none');

        divRadios.classList.add('d-none');
        divopmultiple.classList.add('d-none'); //ocultar el contenedor
        divopmultiple2.classList.add('d-none'); // ocultar el contenedor de multiopciones

        divCompromiso.classList.add('d-none'); //ocultar compromisos

        // Mostrar el elemento adicional correspondiente a la opción seleccionada
        console.log(valorSeleccionado);
        if (valorSeleccionado == 1) {
            divRespuestaCorta.classList.remove('d-none');
        } else if (valorSeleccionado == 3) {
            divRadios.classList.remove('d-none');
            btnAgregarOpcion.classList.remove('d-none'); // Mostrar el botón al seleccionar "Varias opciones"
        } else if (valorSeleccionado == 2) {
            divRespuestaLarga.classList.remove('d-none')
        } else if (valorSeleccionado == 4){
           //quitar la propiedad de la clase para que muestre
           divopmultiple.classList.remove('d-none');
           btnAgregar2.classList.remove('d-none');
        } else if (valorSeleccionado == 5){
            divopmultiple2.classList.remove('d-none');
            btnAgregar3.classList.remove('d-none');
        } else if (valorSeleccionado == 6){ //aqui es funcion para agregar compromiso
            divCompromiso.classList.remove('d-none');
        }


    });

    // Botón para eliminar la fila
    // columna 3
    var columna3 = document.createElement('div');
    columna3.classList.add('col-1');

    var btnEliminar = document.createElement('a');
    btnEliminar.innerHTML = '<i class="bi bi-trash3-fill"></i>';
    btnEliminar.classList.add('btn', 'btn-danger', 'mt-3'); // Cambiar float-end a float-start
    btnEliminar.onclick = function() {
        contenedor.removeChild(nuevaFila);
    };

    // Agregar el botón a la fila
    columna3.appendChild(btnEliminar);
    // Agregar las columnas a la fila
    nuevaFila.appendChild(columna1);
    nuevaFila.appendChild(columna15);
    nuevaFila.appendChild(columna2);
    nuevaFila.appendChild(columna3);
    // agregar las respuestas
    nuevaFila.appendChild(respuestas);

    // Agregar la nueva fila al contenedor
    contenedor.appendChild(nuevaFila);

    contakpiobj++;
}
