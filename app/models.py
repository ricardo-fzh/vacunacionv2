from django.db import models
import datetime
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator

# Create your models here.

#ok
class Cupo(models.Model):
    ESTADO_CHOICES = (
        ('Citado', 'Citado'),
        ('Disponible', 'Disponible'),
    )
    estado =  models.CharField('Estado',max_length=10, choices=ESTADO_CHOICES)
    created_at = models.DateTimeField('Fecha creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Cupo'
        verbose_name_plural = 'Cupos'

    def __str__(self):
        return str(self.estado)
#ok
class Hora(models.Model):
    hora = models.TimeField('Horas', default='00:00')
    dia = models.DateField('Día', default=datetime.date.today)
    cupos = models.ForeignKey(Cupo, on_delete = models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField('Fecha creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Hora'
        verbose_name_plural = 'Horas'

    def __str__(self):
        return str(self.hora)
#ok
class Centro(models.Model):
    nombre = models.CharField('Centro', max_length=180)
    horas = models.ManyToManyField(Hora, null=True, blank=True)
    direccion = models.CharField('Dirección', max_length=255, null=True, blank=True)
    mapa = models.TextField('Mapa')
    estado = models.BooleanField('Estado', default=False)
    created_at = models.DateTimeField('Fecha creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Centro'
        verbose_name_plural = 'Centros'

    def __str__(self):
        return self.nombre
#ok
class Edad(models.Model):
    edad = models.IntegerField('Edad', null=True, blank=True)
    created_at = models.DateTimeField('Fecha creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Edad'
        verbose_name_plural = 'Edades'

    def __str__(self):
        return str(self.edad)
#ok
class Asistencia(models.Model):
    fecha_asistencia= models.DateField('Fecha Asistencia', null=True, blank=True)
    created_at = models.DateTimeField('Fecha creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'

    def __str__(self):
        return str(self.fecha_asistencia)
#ok
class Inoculacion(models.Model):
    fecha_inoculacion= models.DateField('Fecha Inoculación', null=True, blank=True)
    created_at = models.DateTimeField('Fecha creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Inoculacion'
        verbose_name_plural = 'Inoculaciones'

    def __str__(self):
        return str(self.fecha_inoculacion)
#ok
class Persona(models.Model):
    GENDER_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    )
    nombre = models.CharField('nombres', max_length=100,  validators=[RegexValidator(r'\w', 'Formato incorreccto')])
    apellido_paterno = models.CharField('apellido paterno', max_length=100, validators=[RegexValidator(r'[a-z]', 'Formato incorreccto')] )
    apellido_materno = models.CharField('apellido materno', max_length=100,  validators=[RegexValidator(r'[a-z]', 'Formato incorreccto')])
    rut = models.CharField('Rut',max_length=8, validators=[RegexValidator(r'^[0-9]{7}', 'Formato incorrecto')] )
    dv = models.CharField('Dv', max_length=1, validators=[RegexValidator(r'[0-9kK]{1}', 'Formato incorrecto debe ser digito o K')])
    fecha_nac = models.DateField('fecha nacimiento')
    genero = models.CharField('Género',max_length=1, choices=GENDER_CHOICES)
    email = models.EmailField('email', max_length=250)
    celular = models.CharField('Celular',max_length=12)
    centros = models.ForeignKey(Centro, on_delete=models.CASCADE, null=True, blank=True) 
    horas = models.ForeignKey(Hora, verbose_name="Hora agendamiento", on_delete=models.CASCADE, null=True, blank=True)
    edad = models.IntegerField('Edad', null=True, blank=True)
    asistencias = models.ManyToManyField(Asistencia, null=True, blank=True)
    inoculacion = models.ManyToManyField(Inoculacion, null=True, blank=True)
    direccion = models.CharField('Dirección', max_length=255)
    block = models.CharField('Block', max_length=255, null=True, blank=True)
    departamento = models.CharField('Departamento', max_length=255, null=True, blank=True)
    created_at = models.DateTimeField('Fecha creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    def __str__(self):
        return self.nombre
#ok
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return str(self.user)
#ok
class PersonaHabilitada(models.Model):
    rut = models.CharField('Rut',max_length=8, validators=[RegexValidator(r'^[0-9]{7}', 'Formato incorrecto')] )
    dv = models.CharField('Dv', max_length=1, validators=[RegexValidator(r'[0-9kK]{1}', 'Formato incorrecto debe ser digito o K')])
    fecha_vacunacion = models.DateField('Fecha primera vacunación', null=True, blank=True)
    created_at = models.DateTimeField('Fecha creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
#ok
class PersonaFila(models.Model):
    nombre = models.CharField('nombres', max_length=100,  validators=[RegexValidator(r'\w', 'Formato incorreccto')])
    apellido_paterno = models.CharField('apellido paterno', max_length=100, validators=[RegexValidator(r'[a-z]', 'Formato incorreccto')] )
    apellido_materno = models.CharField('apellido materno', max_length=100,  validators=[RegexValidator(r'[a-z]', 'Formato incorreccto')])
    rut = models.CharField('Rut',max_length=8, validators=[RegexValidator(r'^[0-9]{7}', 'Formato incorrecto')] )
    dv = models.CharField('Dv', max_length=1, validators=[RegexValidator(r'[0-9kK]{1}', 'Formato incorrecto debe ser digito o K')])