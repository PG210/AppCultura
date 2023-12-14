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


