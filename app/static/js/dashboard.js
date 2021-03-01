const createTable = (url) => {
	$.fn.dataTable.ext.errMode = 'throw';

	tabla = $("#tabla-dashboard").DataTable({
		stateSave: true,
		responsive: true,
		bDestroy: true,
		aLengthMenu: [
			[25, 50, 75, -1],
			[25, 50, 75, "All"],
		],
		iDisplayLength: -1,
		order: [[3, "desc"]],
		ajax: {
			url: url,
			dataSrc: "",
		},
		columns: [
			"nombre",
			"apellido_paterno",
			"rut",
			"dv",
		].map((header) => ({ title: header, data: header })),
	});
};