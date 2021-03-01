import datetime
import os.path
from datetime import date

import pandas as pd
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from tablib import Dataset

from .forms import HorasForm, PersonaForm
from .models import *
from .resources import CentroResource, HoraResource
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.template import Context
import locale

# from rest_framework import viewsets
# from .serializers import PersonFilaSerializer
# Create your views here.

# Sistema
def user_login(request):
    if request.user.is_authenticated:
        return redirect(to="mantenedor-fechas")

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(to='mantenedor-fechas')
        else:
            messages.error(request, 'Credenciales incorrectas')
    return render(request, 'app/login.html')

def logout_user(request):
    logout(request)
    return redirect(to="login")

# Vista usuario
def index(request):
    centros = Centro.objects.all()
    contador = 0

    for c in centros:
        if c.estado == True:
            contador+=1

    data = {
        'contador': contador,
        'centros': centros,
    }
    return render(request, 'app/index.html', data)

# Hardcore function
def reserva(request, pk):
    centro = get_object_or_404(Centro, pk=pk)
    dias = centro.horas.distinct('dia')
    horas = centro.horas.all().order_by('hora')
    form = PersonaForm()
    form.fields['celular'].widget.attrs['maxlength'] = '8'
    distinct_today = []
    hoy = datetime.datetime.today().strftime('%Y-%m-%d')
    hoy = datetime.datetime.strptime(hoy, '%Y-%m-%d').date()
    locale.setlocale(locale.LC_ALL, "es")

    for d in dias:
        if d.dia > hoy: 
            if d.cupos.id == 1:
                distinct_today.append(d)  
            
    data = {
        "form": form,
        'horas': horas,
        'dias': distinct_today,
        'centro': centro,
    }

    if centro.estado == False:
        return redirect(to="/")

    if request.method == 'POST':
        form = PersonaForm(data=request.POST)
        hora_pk = request.POST.get('horas')
        
        if hora_pk == None or hora_pk == '':
            messages.error(request, "Debes seleccionar una hora valida")
            data['form'] = form
            return render(request, 'app/reserva.html', data)
        
        if form.is_valid():
            rut = form.cleaned_data.get('rut')
            persona_habilitada = PersonaHabilitada.objects.filter(rut=rut).exists()
            nombre = form.cleaned_data.get('nombre')
            apellido_paterno = form.cleaned_data.get('apellido_paterno')
            apellido_materno = form.cleaned_data.get('apellido_materno')
            email = form.cleaned_data.get('email')
            rut = form.cleaned_data.get('rut')
            dv = form.cleaned_data.get('dv')
            dia_post= request.POST.get('dias')
            fecha_nacimiento = request.POST.get('fecha_nac')
            hora_id_form = request.POST.get('horas')
            hora_bd = Hora.objects.get(id=hora_id_form)
    
            dia_agendamiento = datetime.datetime.strptime(dia_post,  '%d de %B de %Y').date()
            celular = form.cleaned_data.get('celular')
            existe_hora = Hora.objects.filter(pk=hora_pk).exists()

            if existe_hora == True:
                existe_hora_agendada = Persona.objects.filter(rut=rut).exists()
                hora = Hora.objects.get(pk=hora_pk)
                d = {'nombre': nombre, 'apellido_paterno': apellido_paterno, 'apellido_materno': apellido_materno,
                     'hora': hora, "email": email, 'rut': rut, 'dv': dv, 'celular': celular, 'centro':centro }
                html_message = render_to_string('app/messages/email.html', d)
                plain_message = strip_tags(html_message)
                
                if existe_hora_agendada == False:
                    today = date.today()
                    form.centros = centro
                    form.save(data)
                    hora.cupos = Cupo.objects.get(id=2)
                    hora.save()
                    persona = Persona.objects.get(rut=rut)
                    persona.centros = centro
                    persona.fecha_vacunacion = hora.dia
                    persona.horas = hora
                    persona.save()
                    messages.success(
                        request, "Hora agendada correctamente")
                    send_mail('Vacuna Covid-19', plain_message, from_email='noreply@renca.cl',
                              recipient_list=[persona.email], html_message=html_message)
                    return redirect(to='/')
                else:
                    persona = Persona.objects.get(rut=rut)
                    if len(persona.inoculacion.all())> 0:
                        if len(persona.inoculacion.all()) == 1:
                            inoculacion = persona.inoculacion.first()
                            start_date = inoculacion.fecha_inoculacion.strftime("%Y-%m-%d")
                            date_1 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                            end_date = date_1 + datetime.timedelta(days=28)
                            x = datetime.datetime(2021, 4, 24)
                            today = datetime.datetime.today()
                                
                            if  today < end_date:
                                messages.error(request, f'Debe esperar hasta el dia {end_date.strftime("%d-%m-%Y")}')
                                data['form'] = form
                            else:
                                form = PersonaForm(data=request.POST, instance=persona)
                                form.centros = centro
                                hora.cupos = Cupo.objects.get(id=2)
                                hora.save()
                                persona.centros = centro
                                persona.fecha_vacunacion = hora.dia
                                persona.horas = hora
                                persona.save()

                                send_mail('Vacuna Covid-19', plain_message, from_email='noreply@renca.cl',
                                  recipient_list=[persona.email], html_message=html_message)
                                messages.success(
                                    request, "Hora agendada correctamente")
                                return redirect(to='/')             
                        if len(persona.inoculacion.all()) == 2:
                            if request.user.is_staff >= False:
                                messages.error(request, f"Ya se encuentra con las 2 dosis de la vacuna.")
                                data['form'] = form

                    else:
                        dia = datetime.datetime.strptime(persona.horas.dia.strftime("%Y-%m-%d"), "%Y-%m-%d")
                        x = datetime.datetime(2021, 3, 17)
                        if persona.horas.dia > hoy:
                            messages.error(request, f"Ya tiene una hora agendada para el día {persona.horas.dia.strftime('%d-%m-%Y')}")
                            data['form'] = form
                        else:
                            persona = Persona.objects.get(rut=rut)
                            persona.centros = centro
                            persona.fecha_vacunacion = hora.dia
                            hora.cupos =  Cupo.objects.get(id=1)
                            hora.save()
                            persona.horas = hora
                            persona.save()
                            messages.success(
                                request, "Hora agendada correctamente")
                            send_mail('Vacuna Covid-19', plain_message, from_email='noreply@renca.cl',
                                      recipient_list=[persona.email], html_message=html_message)
                            return redirect(to='/')
            else:
                messages.error(
                    request, "No se encontraron horas para el registro")
                data['form'] = form
        else:
            data['form'] = form

    return render(request, 'app/reserva.html', data)

# mantenedor_fechas
def mantenedor_fecha(request):
    if not request.user.is_authenticated:
        return redirect(to='login')

    try:
        if request.user.is_staff:
            centros = Centro.objects.all()
            data = { 
                'centros': centros,
            } 
            if request.method == 'POST':
                centro_id = request.POST.get('centros')
                if centro_id != None:
                    centro = Centro.objects.get(id=centro_id)
                    horas = centro.horas.all()
                    data['horas'] = horas
                    data['centro_id'] = centro_id
            return render(request, 'app/mantenedor_fechas.html', data)
        else: 
            centro = Centro.objects.get(
                nombre__icontains=request.user.profile.centro.nombre)
            centros = Centro.objects.all()
            horas = centro.horas.all()
            data = {'centros': centro, 'horas': horas}
            return render(request, 'app/mantenedor_fechas.html', data)
    except ObjectDoesNotExist:
        logout(request)
        messages.error(request, 'Usuario no tiene un centro asociado')
        return redirect(to='login')
#ok
def update_fecha_admin(request, pk, pk_centro):
    if not request.user.is_authenticated:
        return redirect(to='login')
    if request.user.is_staff:
        centro = Centro.objects.get(pk=pk_centro)
        hora = get_object_or_404(Hora, pk=pk)
        form = HorasForm(instance=hora)
        data = {
            "horas": hora,
            "centros": centro,
            "form": form,
        }
        if request.method == 'POST':
            form = HorasForm(data=request.POST, instance=hora)
            if form.is_valid():
                form.save(data)
                return redirect(to='mantenedor-fechas')
            else:
                data['form'] = form
        return render(request, 'app/update-fecha.html', data)
#ok
def update_fecha(request, pk):
    centro = Centro.objects.get(
        nombre__icontains=request.user.profile.centro.nombre)
    hora = get_object_or_404(Hora, pk=pk)
    form = HorasForm(instance=hora)
    data = {
        "horas": hora,
        "centros": centro,
        "form": form,
    }
    if request.method == 'POST':
        form = HorasForm(data=request.POST, instance=hora)
        if form.is_valid():
            form.save(data)
            return redirect(to='mantenedor-fechas')
        else:
            data['form'] = form
    return render(request, 'app/update-fecha.html', data)
#ok
def add_fecha_admin(request, pk):
    if not request.user.is_authenticated:
        return redirect(to='login')

    if request.user.is_staff:
        centro = Centro.objects.get(pk=pk)

        if request.method == 'POST':
            data = pd.read_csv(request.FILES['myfile'])
            data_ext = request.FILES['myfile']
            extension = os.path.splitext(str(data_ext))[1]

            if extension != '.csv':
                messages.error(request, 'El archivo debe ser de extensión .CSV')
                return redirect(to="mantenedor-fechas")

            horas = [
                Hora(
                    hora=row['hora'],
                    dia=row['dia'],
                    cupos=Cupo.objects.get(id=2),
                    created_at=date.today(),
                    updated_at=date.today(),
                )
                for i, row in data.iterrows()
            ]

            try:
                hora = Hora.objects.bulk_create(horas)
                for h in hora:
                    centro.horas.add(h.id)
                
                messages.success(request, f"Horas cargadas exitosamente")
                return redirect(to="mantenedor-fechas")
            except:
                messages.error(
                    request, f"Error al cargar archivo, verifique la estructura del archivo")
                return redirect(to="mantenedor-fechas")

        return render(request, 'app/add-fecha.html')
#ok
def add_fecha(request):
    if not request.user.is_authenticated:
        return redirect(to='login')

    centro = Centro.objects.get(
        nombre__icontains=request.user.profile.centro.nombre)

    if request.method == 'POST':
        data = pd.read_csv(request.FILES['myfile'])
        data_ext = request.FILES['myfile']
        extension = os.path.splitext(str(data_ext))[1]

        if extension != '.csv':
            messages.error(request, 'El archivo debe ser de extensión .CSV')
            return redirect(to="add-fecha")

        horas = [
            Hora(
                hora=row['hora'],
                dia=row['dia'],
                cupos=row['cupos'],
                created_at=date.today(),
                updated_at=date.today(),
            )
            for i, row in data.iterrows()
        ]

        try:
            hora = Hora.objects.bulk_create(horas)
            for h in hora:
                centro.horas.add(h.id)
            messages.success(request, f"Horas cargadas exitosamente")
            return redirect(to="mantenedor-fechas")
        except:
            messages.error(
                request, f"Error al cargar archivo, verifique la estructura del archivo")
            return redirect(to="add-fecha")

    return render(request, 'app/add-fecha.html')
#ok
def delete_fecha(request, pk):
    if not request.user.is_authenticated:
        return redirect(to='login')
    hora = get_object_or_404(Hora, pk=pk)
    hora.delete()
    return redirect(to='mantenedor-fechas')
 #ok
#ok
def mantenedor_persona_admin(request):
    if not request.user.is_authenticated:
        return redirect(to='login')
    
    if request.user.is_staff:
        centros_all = Centro.objects.all()
        data = { 
            'centros_all': centros_all,
        } 
        if request.method == 'POST':
            centro_id = request.POST.get('centros')
            if centro_id == None:
                messages.error(request,'Debe seleccionar un instituto')
                return render(request, 'app/mantenedor_persona_admin.html', data)
            return redirect(to="mantenedor-personas-admin-inst",pk=centro_id)

        return render(request, 'app/mantenedor_persona_admin.html', data)

def mantenedor_persona_admin_instituto(request, pk):
    if not request.user.is_authenticated:
        return redirect(to='login')

    if request.user.is_staff:
        centros = Centro.objects.get(pk=pk)
        centros_all = Centro.objects.all()
        personas = Persona.objects.filter(centros__nombre=centros.nombre)
        data = { 
            'centros_all': centros_all, 'centros':centros, 'usuarios':personas, 'centro_id':pk
        } 
        if request.method == 'POST':
            delete = request.POST.get('del')
 
            if delete == 'del':
                centro_id = request.POST.get('centros')
                user_id = request.POST.get('id')
                persona = Persona.objects.get(id=user_id)
                if len(persona.inoculacion.all()) == 0:
                    # persona.asistencias.all()[0].delete()
                    if len(persona.asistencias.all()) > 0:                                                                                  
                        try:
                            persona.asistencias.all()[0].delete()
                            persona_fila = PersonaFila.objects.get(rut = persona.rut)
                            persona_fila.delete()   
                            messages.success(request, 'Hora anulada')
                        except PersonaFila.DoesNotExist:
                            pass
   
                if len(persona.inoculacion.all()) == 1:
                    try:
                        persona.inoculacion.all()[0].delete()
                        persona.asistencias.all()[0].delete()
                        persona.save()
                        persona_fila = PersonaFila.objects.get(rut = persona.rut)
                        persona_fila.delete()   
                        messages.success(request, 'Hora anulada')
                    except PersonaFila.DoesNotExist:
                        pass

                if len(persona.inoculacion.all()) == 2:
                    
                    try:
                        persona.inoculacion.all()[1].delete()
                        persona.asistencias.all()[1].delete()
                        persona.save()
                        persona_fila = PersonaFila.objects.get(rut = persona.rut)
                        persona_fila.delete()   
                        messages.success(request, 'Hora anulada')
                    except PersonaFila.DoesNotExist:
                        pass
            else:
                centro_id = request.POST.get('centros')
                user_id = request.POST.get('id')

                if user_id != None:
                    persona = Persona.objects.get(id=user_id)

                    if len(persona.asistencias.all()) >= 2:
                        messages.error(request, 'Error al intentar ingresar paciente')
                        
                    else:

                        obj, created = PersonaFila.objects.get_or_create(
                            nombre=persona.nombre,
                            apellido_paterno=persona.apellido_paterno,
                            apellido_materno=persona.apellido_materno,
                            rut=persona.rut,
                            dv=persona.dv
                        )
                        if created == True:
                            asistencia = persona.asistencias.create(
                                fecha_asistencia = date.today()
                            )
                            persona.asistencias.add(asistencia)
                            messages.success(
                                request, 'Persona verificada')
                        else:
                            messages.error(
                                request, 'Persona se encuentra en procedimiento')

        return render(request, 'app/mantenedor_persona_admin_i.html', data)

def mantenedor_persona(request):
    if not request.user.is_authenticated:
        return redirect(to='login')

    try:
        centros = Centro.objects.get(
            nombre__icontains=request.user.profile.centro.nombre)
        personas = Persona.objects.filter(centros__nombre=centros.nombre)
        data = {'centros': centros, 'usuarios': personas}
        if request.method == 'POST':
            delete = request.POST.get('del')
 
            if delete == 'del':
                centro_id = request.POST.get('centros')
                user_id = request.POST.get('id')
                persona = Persona.objects.get(id=user_id)
                if persona.vacuna_disponible == 1:
                    persona.fecha_primer_registro = None
                    persona.vacuna_disponible = 2
                    persona.save()
                    persona.save()
                    persona_fila = PersonaFila.objects.get(rut = persona.rut)
                    messages.success(request, 'Hora anulada')

                if persona.vacuna_disponible == 0:
                    persona.fecha_seg_vacunacion = None
                    persona.horas_seg_v = '00:00:00'
                    persona.fecha_segundo_registro =None
                    persona.vacuna_disponible = 1
                    persona.save()
                    persona.save()
                    persona_fila = PersonaFila.objects.get(rut = persona.rut)
                    messages.success(request, 'Hora anulada')
            else:
                user_id = request.POST.get('id')
                if user_id != None:
                    persona = Persona.objects.get(id=user_id)
                    if persona.vacuna_disponible == 2:
                        x = datetime.date(2021, 3, 26)
                        # date.today()
                        if date.today() >= persona.fecha_vacunacion:
                            persona.vacuna_disponible = persona.vacuna_disponible - 1
                            persona.fecha_primer_registro = date.today()
                            persona.fecha_segundo_registro = date.today()
                            time_diference = persona.fecha_segundo_registro - persona.fecha_nac
                            age = int(time_diference.days / 365)
                            persona.edad_primer_registro = age
                            persona.save()
                            PersonaFila.objects.create(
                                nombre=persona.nombre,
                                apellido_paterno=persona.apellido_paterno,
                                apellido_materno=persona.apellido_materno,
                                rut=persona.rut,
                                dv=persona.dv
                            )
                            messages.success(
                                request, 'Persona registrada en el sistema')
                        else:
                            messages.error(
                                request, f'Debe esperar 28 días para la proxima vacuna')
                    elif persona.vacuna_disponible == 1:
                        start_date = persona.fecha_primer_registro.strftime(
                            "%Y-%m-%d")
                        date_1 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                        end_date = date_1 + datetime.timedelta(days=28)
                        x = datetime.datetime(2021, 3, 23)
                        # datetime.datetime.today()
                        if datetime.datetime.today() >= end_date:
                            persona.vacuna_disponible = persona.vacuna_disponible - 1
                            persona.fecha_vacunacion = persona.fecha_vacunacion
                            persona.fecha_primer_registro = persona.fecha_primer_registro
                            persona.fecha_seg_vacunacion = persona.fecha_seg_vacunacion
                            persona.fecha_segundo_registro = date.today()
                            time_diference = persona.fecha_segundo_registro - persona.fecha_nac
                            age = int(time_diference.days / 365)
                            persona.edad_segundo_registro = age
                            persona.save()
                            PersonaFila.objects.create(
                                nombre=persona.nombre,
                                apellido_paterno=persona.apellido_paterno,
                                apellido_materno=persona.apellido_materno,
                                rut=persona.rut,
                                dv=persona.dv
                            )
                            messages.success(
                                request, 'Persona registrada en el sistema')
                        else:
                            messages.error(
                                request, f'Debe esperar 28 días para la proxima vacuna {end_date}')
                    else:
                        messages.error(request, 'Persona ya se encuentra vacunada')
                else:
                    messages.error(
                        request, 'Persona no se encuentra registrada sistema')
        return render(request, 'app/mantenedor_persona.html', data)
    except ObjectDoesNotExist:
        logout(request)
        messages.error(request, 'Usuario no tiene un centro asociado')
        return redirect(to='login')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect(to='login')
    persona_fila = PersonaFila.objects.all()
    data = {
        'persona_fila': persona_fila
    }
    if request.method == 'POST':
        uid = request.POST.get('id')
        rut = request.POST.get('rut')
        dv = request.POST.get('dv')
        persona = Persona.objects.get(rut=rut)
        inoculacion = Inoculacion.objects.create(
            fecha_inoculacion = date.today()
        )
        persona.inoculacion.add(inoculacion) 
        persona.save()
        persona_f = PersonaFila.objects.get(id = uid)
        persona_f.delete()
    return render(request, 'app/dashboard.html', data)
     


# Api
# class PersonaFilaViewSet(viewsets.ModelViewSet):
    # queryset = PersonaFila.objects.all()
    # serializer_class = PersonFilaSerializer