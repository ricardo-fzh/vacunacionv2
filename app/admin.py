from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import *


class PersonaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido_paterno', 'apellido_materno' , 'rut', 'centros') 
 

@admin.register(Hora)
class HoraAdmin(ImportExportModelAdmin):
    pass

class PersonaResource(resources.ModelResource):

    fecha_vacunacion = fields.Field(
        attribute='fecha_vacunacion',
        column_name='Fecha vacunacion',
    )

    horas = fields.Field(
        attribute='horas',
        column_name='Hora agendada',
        widget=ForeignKeyWidget(Hora, 'hora')
    )

    centros = fields.Field(
        attribute='centros',
        column_name='Centro',
        widget=ForeignKeyWidget(Centro, 'nombre')
    )

    class Meta:
        model = Persona
        exclude= ('id',)

@admin.register(Persona)
class PersonaImport(ImportExportModelAdmin, PersonaAdmin):  
    resource_class = PersonaResource

admin.site.register(Centro) 
# admin.site.register(Profile)
admin.site.register(PersonaHabilitada)
admin.site.register(PersonaFila)
admin.site.register(Cupo)
admin.site.register(Asistencia)
admin.site.register(Inoculacion)

