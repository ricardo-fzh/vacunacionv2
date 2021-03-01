from import_export import resources
from .models import Hora, Centro

class HoraResource(resources.ModelResource):
    class Meta:
        model = Hora

class CentroResource(resources.ModelResource):
    class Meta:
        model = Centro
