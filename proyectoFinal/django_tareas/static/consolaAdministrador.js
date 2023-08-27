function editarUsuario(idEditar)
{
    /*
    PREGUNTA 3
    Capturar informacion del usuario desde base de datos y llenar
    inputs dentro de la ventana modal de editar usuario, permiter que
    el usuario pueda editar los datos. No olvida de cargar el ID en el innerHTML
    dentro del elemento H1 cuyo id es cargaId

    Los campos a editar son:
    Nro de celular
    Profesion del usuario

    El resto de campos:
    Nombre
    Apellido
    Email
    Fecha Ingreso
    Colocarlos como solo lectura (propiedad readonly en el tag HTML)
    
    */
    fetch(`/conseguirInfoUsuario?idEditar=${idEditar}`)
    .then(response => response.json())
    .then(data => {
        let nombreUsuarioDetalle = document.getElementById('nombreUsuarioDetalle')
        let apellidoUsuarioDetalle = document.getElementById('apellidoUsuarioDetalle')
        let profesionUsuarioDetalle = document.getElementById('profesionUsuarioDetalle')
        let emailUsuarioDetalle = document.getElementById('emailUsuarioDetalle')
        let tipoUsuarioDetalle = document.getElementById('tipoUsuarioDetalle')
        let nroCelularDetalle = document.getElementById('nroCelularDetalle')
        let perfilUsuarioDetalle = document.getElementById('perfilUsuarioDetalle')
        let cargaId = document.getElementById('cargaId')

        cargaId.innerHTML = data.idUsuario
        nombreUsuarioDetalle.value = data.nombreUsuario
        apellidoUsuarioDetalle.value = data.apellidoUsuario
        profesionUsuarioDetalle.value = data.profesionUsuario
        emailUsuarioDetalle.value = data.emailUsuario
        tipoUsuarioDetalle.value = data.tipoUsuario
        nroCelularDetalle.value = data.nroCelularUsuario
        perfilUsuarioDetalle.innerHTML = data.perfilUsuario
    })
}

function actualizarUsuario()
{
    /*
    PREGUNTA 4
    Capturar los datos de los campos input's de la ventana de editar usuario,
    el id del usuario lo puedes capturar de la carga realizada en el elemento
    H1 cuyo id es cargaId. Con los datos capturados postearlos en la base de datos
    y actualizar la informacion del usuario
    */
    let profesionUsuarioDetalle = document.getElementById('profesionUsuarioDetalle')
    let nroCelularDetalle = document.getElementById('nroCelularDetalle')
    let cargaId = document.getElementById('cargaId')

    datos = {
        'profesion':profesionUsuarioDetalle.value,
        'nroCelular':nroCelularDetalle.value,
        'idUsuario':cargaId.innerHTML
    }

    fetch('/actualizarUsuario',{
        method:"POST",
        headers:{
            "X-Requested-With":"XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body:JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
    })
}

function getCookie(name)
{
    let cookieValue = null;
    if(document.cookie && document.cookie !== "")
    {
        const cookies = document.cookie.split(';');
        for(let i = 0; i < cookies.length; i++)
        {
            const cookie = cookies[i].trim();
            if(cookie.substring(0,name.length + 1) === (name + "="))
            {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue 
}