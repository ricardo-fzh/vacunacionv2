from django import forms
from .models import Hora, Persona, Centro
from .helper import digito_verificador
from django.core.exceptions import ValidationError

class HorasForm(forms.ModelForm):
    class Meta:
        model =  Hora
        fields = '__all__'
        widgets = {
        'hora': forms.TextInput(attrs={'type': 'time'}),
        'dia': forms.TextInput(attrs={'type': 'date'})
        }



    
class PersonaForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(PersonaForm, self).__init__(*args, **kwargs)
        self.fields['dv'].label = False

    class  Meta:
        model =  Persona
        fields = '__all__'
        exclude = [ 'centros','horas',  'inoculacion', 'asistencias']
        widgets = {
        'email' : forms.TextInput(attrs={'placeholder': 'ejemplo@ejemplo.cl'}),
        'fecha_nac': forms.TextInput(attrs={'type': 'date'}),
        'celular': forms.TextInput(attrs={'placeholder': '87654321', 'type': 'tel', 'size':8}),
        'direccion' :forms.TextInput(attrs={'placeholder': 'Ej: Los Aromos 3339, Renca'}),
        'departamento' :forms.TextInput(attrs={'placeholder': 'Ej: 1420'}),
        'block' :forms.TextInput(attrs={'placeholder': 'Ej: Torre A'})
        }
    
    
    #Validaciones se debe validar el rut si existe y es correcto   

            
    def clean_dv(self):
        rut = self.cleaned_data.get('rut')
        dv_valido = digito_verificador(rut)
        dv = self.cleaned_data.get('dv')
        if dv_valido == 10:
            dv_valido = "k"

        if str(dv) != str(dv_valido).lower():
            raise forms.ValidationError("El R.U.T es incorrecto")
        return dv
    
    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data.get('nombre').split())
        return nombre.title()

    def clean_apellido_materno(self):
        apellido_materno = " ".join(self.cleaned_data.get('apellido_materno').split())
        return apellido_materno.title()

    def clean_apellido_paterno(self):
        apellido_paterno = " ".join(self.cleaned_data.get('apellido_paterno').split())
        return apellido_paterno.title()

    def clean_celular(self):
        celular = f"+569{self.cleaned_data.get('celular')}"
        if len(celular) != 12 :
            raise forms.ValidationError('Formato debe ser:87654321')
        return celular