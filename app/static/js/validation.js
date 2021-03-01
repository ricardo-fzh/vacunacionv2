

const validacion = () => {
    $(".reserva").submit(function () {
        
        const select = $("#horas").val();

        if (select == null) {
            Swal.fire({
                "title": "Error",
                "text": "Debe seleccionar una fecha de reserva",
                "icon": "error"
              });

              return false;
            
        }

        //  else {
        //     $('.errors').hide();
        //     alert('OK');
        //     return true;
        // }
        });
}

validacion();
