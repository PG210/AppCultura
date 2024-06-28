let currentSection = 0;
const sections = document.querySelectorAll('.seccion');
const butonnext = document.getElementById('butonnext');
const butonback = document.getElementById('butonback'); 

function showSection(index) {
  sections.forEach((seccion, i) => {
    if (i === index) {
      seccion.classList.add('active');
      seccion.style.display = 'block';
    } else {
      seccion.classList.remove('active');
      seccion.style.display = 'none';
    }
  });
  // Mostrar botones adicionales solo en la sección 3
   butonback.style.display = index == 0 ? 'none' : '';
  if (index == 2) {
      butonnext.type = 'submit'; // Cambiar tipo a submit
      butonnext.textContent = 'Guardar'; // Cambiar texto a Guardar
  }
}

function validateSection(index) {
  const section = sections[index];
  const inputs = section.querySelectorAll('input[type="text"], input[type="datetime-local"], select, textarea');
  const checkboxes = section.querySelectorAll('#competencias input[type="checkbox"]');
  const checkgrup = section.querySelectorAll('#gruposn input[type="checkbox"]');
  if (index === 2){
  const tema = document.querySelectorAll('input[input-var="tematica"], textarea[input-var="des"], textarea[input-var="re"]');  
  let seccion3 = true;
    tema.forEach(function(campo) {
        if (!campo.value) {
            seccion3 = false;
            campo.style.borderColor = 'red'; // Marcar el campo vacío
        } else {
            campo.style.borderColor = ''; // Restablecer el estilo si el campo no está vacío
        }
    });
    if(!seccion3){
      messaje(4);
    }
  }
 
  // Validate text inputs, selects, and textareas
  for (const input of inputs) {
    if (!input.value) {
      input.focus();
      return false;
    }
  }
  //
  // Validate checkboxes
  if (checkboxes.length > 0) {
    const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
    if (!anyChecked) {
      messaje(1);
      return false;
    }
  }
   
  //checkboxes de grupos
  if (checkgrup.length > 0) {
      const checkn = Array.from(checkgrup).some(checkbox => checkbox.checked);
      if (!checkn) {
        messaje(2)
        return false;
      }
    }
   //temas 
  return true;
}

function nextSection() {
  if (validateSection(currentSection)) {
    if (currentSection < sections.length - 1) {
      currentSection++;
      showSection(currentSection);
    }
  } else {
    messaje(3);
  }
}

function prevSection() {
  if (currentSection > 0) {
    currentSection--;
    showSection(currentSection);
  }
}

// Inicializa la primera sección
showSection(currentSection);

function messaje(val){
  toastr.options.timeOut = 2000;
  toastr.options.progressBar = true;
  if (val == 1){
    toastr.warning('Por favor, selecciona al menos una competencia.', null, { timeOut: 5000, extendedTimeOut: 5000 });
    return true;
  }
     
  if (val == 2){
    toastr.warning('Por favor, selecciona al menos un grupo.', null, { timeOut: 5000, extendedTimeOut: 5000 });
    return true;
  }
      
  if (val == 3){
    toastr.info('Por favor, completa todos los campos antes de continuar.');
    return true;
  }
  if (val == 4){
    toastr.warning('Por favor, completa las temáticas.', null, { timeOut: 5000, extendedTimeOut: 5000});
    return true;
  }
     
}
