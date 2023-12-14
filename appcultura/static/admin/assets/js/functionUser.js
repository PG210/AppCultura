
//listarCompromisos();

$('.fj-date').datepicker({
    format: "dd/mm/yyyy",
    startDate: '-3d'
});

const refrescar = () => {
    location.reload()
}
// Inicio formulario de inscripcion de asistencia
function ocultarcontrasena1(){
    let passwordField = document.getElementById("password1");
    

    if (passwordField.type === "password") {
    passwordField.type = "text";
    } else {
    passwordField.type = "password";
    }
}

function ocultarcontrasena2(){
    let passwordField = document.getElementById("password2");

    if (passwordField.type === "password") {
    passwordField.type = "text";
    } else {
    passwordField.type = "password";
    }
}

//Fin de inscripcion de asistencias