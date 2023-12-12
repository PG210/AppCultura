import Swal from 'sweetalert2';

const obtenerData = async () =>{
    try{
        let response = await fetch('http://localhost:8000/administrador/api/cursos/');
        let data = await response.json();
        return data
        
    }catch(error){
        console.error('error al leer los datos', error);
    }
    
};

/*const leerdata = async () =>{
    let datos = await obtenerData()
    console.log(datos)
}*/

async function leerdata(){
    let datos = await obtenerData();
    let data = JSON.parse(datos)
    console.log(data)
    console.log(data[0].fields.nombre);
}


const swalWithBootstrapButtons = Swal.mixin({
    customClass: {
      confirmButton: "btn btn-success",
      cancelButton: "btn btn-danger"
    },
    buttonsStyling: false
  });
  swalWithBootstrapButtons.fire({
    title: "Are you sure?",
    text: "You won't be able to revert this!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Yes, delete it!",
    cancelButtonText: "No, cancel!",
    reverseButtons: true
  }).then((result) => {
    if (result.isConfirmed) {
      swalWithBootstrapButtons.fire({
        title: "Deleted!",
        text: "Your file has been deleted.",
        icon: "success"
      });
    } else if (
      /* Read more about handling dismissals below */
      result.dismiss === Swal.DismissReason.cancel
    ) {
      swalWithBootstrapButtons.fire({
        title: "Cancelled",
        text: "Your imaginary file is safe :)",
        icon: "error"
      });
    }
  });