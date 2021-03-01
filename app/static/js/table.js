$(document).ready(function() {
    // $.fn.dataTable.ext.errMode = 'throw';

    $('#table').DataTable({
        "oLanguage": {
            "oPaginate": {
            "sFirst": "Primera", // This is the link to the first page
            "sPrevious": "Anterior", // This is the link to the previous page
            "sNext": "Siguiente", // This is the link to the next page
            "sLast": "Última", // This is the link to the last page
            },
         "sLengthMenu": "Mostrar _MENU_ registros",
         "sSearch": "Buscar:",
         "sInfo": "Mostrando _TOTAL_ registros de (_END_)"

        }
    });
    
} );