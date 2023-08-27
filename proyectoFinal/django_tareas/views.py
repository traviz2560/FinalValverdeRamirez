from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import datosUsuario, tareasInformacion, comentarioTarea
import datetime
import json
import os

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Create your views here.
def index(request):
    if request.method == 'POST':
        nombreUsuario = request.POST.get('nombreUsuario')
        contraUsuario = request.POST.get('contraUsuario')
        usuarioInfo = authenticate(request,username=nombreUsuario,password=contraUsuario)
        if usuarioInfo is not None:
            login(request,usuarioInfo)
            if usuarioInfo.datosusuario.tipoUsuario == 'ADMINISTRADOR':
                return HttpResponseRedirect(reverse('django_tareas:consolaAdministrador'))
            else:
                return HttpResponseRedirect(reverse('django_tareas:verUsuario', kwargs={'ind':usuarioInfo.id}))
        else:
            return HttpResponseRedirect(reverse('django_tareas:index'))
    return render(request,'ingresoUsuario.html')

@login_required(login_url='/')
def cerrarSesion(request):
    logout(request)
    return HttpResponseRedirect(reverse('django_tareas:index'))

@login_required(login_url='/')
def consolaAdministrador(request):
    if request.user.datosusuario.tipoUsuario == 'ADMINISTRADOR':
        if request.method == 'POST':
            usernameUsuario = request.POST.get('usernameUsuario')
            contraUsuario = request.POST.get('contraUsuario')
            nombreUsuario = request.POST.get('nombreUsuario')
            apellidoUsuario = request.POST.get('apellidoUsuario')
            tipoUsuario = request.POST.get('tipoUsuario')
            nroCelular = request.POST.get('nroCelular')
            profesionUsuario = request.POST.get('profesionUsuario')
            perfilUsuario = request.POST.get('perfilUsuario')
            emailUsuario = request.POST.get('emailUsuario')
            usuarioNuevo = User.objects.create(
                username=usernameUsuario,
                email=emailUsuario,
            )
            usuarioNuevo.set_password(contraUsuario)
            usuarioNuevo.first_name = nombreUsuario
            usuarioNuevo.last_name = apellidoUsuario
            usuarioNuevo.is_staff = True
            usuarioNuevo.save()
            datosUsuario.objects.create(
                user=usuarioNuevo,
                tipoUsuario = tipoUsuario,
                nroCelular = nroCelular,
                profesionUsuario=profesionUsuario,
                perfilUsuario = perfilUsuario
            )
            return HttpResponseRedirect(reverse('django_tareas:consolaAdministrador'))
        return render(request,'consolaAdministrador.html',{
            'usuariosTotales':User.objects.all().order_by('id')
        })
    else:
        return HttpResponseRedirect(reverse('django_tareas:verUsuario', kwargs={'ind':request.user.id}))

def eliminarUsuario(request,ind):
    usuarioEliminar = User.objects.get(id=ind)
    datosUsuario.objects.get(user=usuarioEliminar).delete()
    usuarioEliminar.delete()
    return HttpResponseRedirect(reverse('django_tareas:consolaAdministrador'))

@login_required(login_url='/')
def verUsuario(request, ind):
    usuarioInformacion = User.objects.get(id=ind)
    tareasUsuario = tareasInformacion.objects.filter(usuarioRelacionado=usuarioInformacion).order_by('id')
    return render(request,'informacionUsuario.html',{
        'usuarioInfo': usuarioInformacion,
        'tareasUsuario': tareasUsuario
    })

def nuevaTarea(request, ind):
    if request.method == 'POST':
        usuarioRelacionado = User.objects.get(id=ind)
        fechaInicio = request.POST.get('fechaInicio')
        fechaFin = request.POST.get('fechaFin')
        descripcionTarea = request.POST.get('descripcionTarea')
        fechaSeparada = fechaInicio.split('-')
        ini_dia = int(fechaSeparada[2])
        ini_mes = int(fechaSeparada[1])
        ini_anho = int(fechaSeparada[0])
        fechaSeparada = fechaFin.split('-')
        fin_dia = int(fechaSeparada[2])
        fin_mes = int(fechaSeparada[1])
        fin_anho = int(fechaSeparada[0])
        fechaInicioRegistro = datetime.datetime(ini_anho, ini_mes, ini_dia)
        fechaFinRegistro = datetime.datetime(fin_anho, fin_mes, fin_dia)
        tareasInformacion.objects.create(
            fechaInicio=fechaInicioRegistro,
            fechaFin=fechaFinRegistro,
            descripcionTarea=descripcionTarea,
            usuarioRelacionado=usuarioRelacionado,
        )
        return HttpResponseRedirect(reverse('django_tareas:verUsuario', kwargs={'ind':ind}))

def devolverMensaje(request):
    print(request.GET)
    nombre = request.GET.get('nombre')
    apellido = request.GET.get('apellido')
    edad = request.GET.get('edad')
    profesion = request.GET.get('profesion')
    print(nombre)
    print(apellido)
    print(edad)
    print(profesion)
    return JsonResponse({
        "nombre":nombre,
        "edad":edad,
        "apellido":apellido,
        "profesion":profesion,
        "funcion":"devolverMensaje",
        "fechaEjecuacion":"2023-04-14",
    })

def conseguirInfoTarea(request):
    comentariosTotales = []
    idTarea = request.GET.get('idTarea')
    tareaSeleccionada = tareasInformacion.objects.get(id=idTarea)
    comentariosTarea = tareaSeleccionada.comentariotarea_set.all()
    for comentario in comentariosTarea:
        comentariosTotales.append([str(comentario.usuarioRelacionado.first_name + ' ' + comentario.usuarioRelacionado.last_name),comentario.comentarioTarea])
    print(comentariosTotales)
    return JsonResponse({
        'descripcionTarea':tareaSeleccionada.descripcionTarea,
        'estadoTarea':tareaSeleccionada.estadoTarea,
        'fechaInicio':tareaSeleccionada.fechaInicio.strftime("%d-%m-%Y"),
        'fechaFin':tareaSeleccionada.fechaFin.strftime("%d-%m-%Y"),
        'idTarea':str(tareaSeleccionada.id),
        'comentariosTotales':comentariosTotales,
    })

def eliminarTarea(request,idTarea,idUsuario):
    tareasInformacion.objects.get(id=idTarea).delete()
    return HttpResponseRedirect(reverse('django_tareas:verUsuario', kwargs={'ind':idUsuario}))

def descargarTareas(request,idUsuario):
    usuarioInformacion = User.objects.get(id=idUsuario)
    tareasUsuario = tareasInformacion.objects.filter(usuarioRelacionado=usuarioInformacion).order_by('id')
    nombreArchivo = 'tareas-' + f'{usuarioInformacion.username}' + '.pdf'

    archivoPdf = canvas.Canvas(nombreArchivo,A4)

    logoApp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/logoApp.png')
    logoPUCP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/logoPUCP.png')

    archivoPdf.drawImage(logoApp,20, 700, width=140, height=80)
    archivoPdf.drawImage(logoPUCP,430, 700, width=140, height=80)
    
    archivoPdf.setFont('Helvetica-Bold',25)
    archivoPdf.drawCentredString(297.5,730,'Reporte de tareas')

    #Informacion del usuario
    archivoPdf.setFont('Helvetica-Bold',12)
    archivoPdf.drawString(40,620, 'Nombre de usuario')
    archivoPdf.drawString(40,605, 'Primer nombre')
    archivoPdf.drawString(40,590, 'Apellido')
    archivoPdf.drawString(40,575, 'Email')

    archivoPdf.drawString(155,620, ':')
    archivoPdf.drawString(155,605, ':')
    archivoPdf.drawString(155,590, ':')
    archivoPdf.drawString(155,575, ':')

    archivoPdf.setFont('Helvetica',12)
    archivoPdf.drawString(160,620, f'{usuarioInformacion.username}')
    archivoPdf.drawString(160,605, f'{usuarioInformacion.first_name}')
    archivoPdf.drawString(160,590, f'{usuarioInformacion.last_name}')
    archivoPdf.drawString(160,575, f'{usuarioInformacion.email}')

    archivoPdf.setFont('Helvetica-Bold',12)
    archivoPdf.drawString(300,620, 'Tipo de usuario')
    archivoPdf.drawString(300,605, 'Profesion del usuario')
    archivoPdf.drawString(300,590, 'Nro de celular')
    archivoPdf.drawString(300,575, 'Fecha de ingreso')

    archivoPdf.drawString(425,620, ':')
    archivoPdf.drawString(425,605, ':')
    archivoPdf.drawString(425,590, ':')
    archivoPdf.drawString(425,575, ':')

    archivoPdf.setFont('Helvetica',12)
    archivoPdf.drawString(430,620, f'{usuarioInformacion.datosusuario.tipoUsuario}')
    archivoPdf.drawString(430,605, f'{usuarioInformacion.datosusuario.profesionUsuario}')
    archivoPdf.drawString(430,590, f'{usuarioInformacion.datosusuario.nroCelular}')
    archivoPdf.drawString(430,575, f'{usuarioInformacion.datosusuario.fechaIngreso.strftime("%d-%m-%Y")}')

    lista_x = [40,550]
    lista_y = [500,540]
    archivoPdf.setStrokeColorRGB(0,0,1)

    for tarea in tareasUsuario:
        archivoPdf.grid(lista_x,lista_y)
        archivoPdf.setFont('Helvetica',12)
        archivoPdf.drawString(lista_x[0] + 20, lista_y[1]-15, f'{tarea.fechaInicio}')
        archivoPdf.drawString(lista_x[0] + 120, lista_y[1]-15, f'{tarea.fechaFin}')
        archivoPdf.drawString(lista_x[0] + 220, lista_y[1]-15, f'{tarea.estadoTarea}')
        archivoPdf.drawString(lista_x[0] + 20, lista_y[1]-35, f'{tarea.descripcionTarea}')
        lista_y[0] = lista_y[0] - 60
        lista_y[1] = lista_y[1] - 60
    archivoPdf.save()

    archivoTareas = open(nombreArchivo,'rb')
    return FileResponse(archivoTareas,as_attachment=True)

def react(request):
    return render(request,'react.html')

def iterarReact(request):
    return render(request,'iterarReact.html')


def publicarComentario(request):
    datos = json.load(request)
    idTarea = datos.get('idTarea')
    comentario = datos.get('comentario')
    usuarioRelacionado = request.user
    tareaRelacionada = tareasInformacion.objects.get(id=idTarea)
    comentarioTarea(
        usuarioRelacionado=usuarioRelacionado,
        tareaRelacionada=tareaRelacionada,
        comentarioTarea=comentario
    ).save()
    return JsonResponse({
        'resp':'ok'
    })

def descargarReporteUsuarios(request):
    """
    PREGUNTA 1
    En esta funcion debe generar un pdf con utilizando la libreria reportlab
    Este reporte debe contener la informacion de todos los usuarios a excepcion
    de la contraseña y debe mostrar tambien la cantidad de tareas de cada 
    usuarios (Solo la cantidad no es necesario la descripcion de todas)

    Usuarios Nombre Apellido
    Username        Fecha de ingreso       Numero de celular
    Cantidad de tareas              Tipo de usuario

    Agregar una descripcion de cabecera de la siguiente forma

    Logo de DJANGO      Titulo: Reporte de usuarios     Logo de PUCP
    Fecha de creacion del reporte
    Cantidad de usuarios
    Usuario que genera el reporte
    Tipo de usuarios que genera el reporte
    
    """
    # Datos
    usuarioInformacion = request.user
    usuarios = User.objects.order_by('id')
    nombreArchivo = 'reporteUsuarios.pdf'
    archivoPdf = canvas.Canvas(nombreArchivo,A4)

    # Cabecera
    logoApp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/logoApp.png')
    logoPUCP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/logoPUCP.png')

    archivoPdf.drawImage(logoApp,20, 700, width=140, height=80)
    archivoPdf.drawImage(logoPUCP,430, 700, width=140, height=80)
    
    archivoPdf.setFont('Helvetica-Bold',25)
    archivoPdf.drawCentredString(297.5,730,'Reporte de Usuarios')

    archivoPdf.setFont('Helvetica-Bold',12)
    archivoPdf.drawString(40,620, 'Fecha de creacion del reporte')
    archivoPdf.drawString(40,605, 'Cantidad de usuarios')
    archivoPdf.drawString(40,590, 'Usuario que genera el reporte')
    archivoPdf.drawString(40,575, 'Tipo de usuario que genera el reporte')

    archivoPdf.drawString(260,620, ':')
    archivoPdf.drawString(260,605, ':')
    archivoPdf.drawString(260,590, ':')
    archivoPdf.drawString(260,575, ':')

    archivoPdf.setFont('Helvetica',12)
    archivoPdf.drawString(265,620, f'{datetime.datetime.now().strftime("%d-%m-%y")}')
    archivoPdf.drawString(265,605, f'{User.objects.count()}')
    archivoPdf.drawString(265,590, f'{usuarioInformacion.username}')
    archivoPdf.drawString(265,575, f'{usuarioInformacion.datosusuario.tipoUsuario}')

    # Informacion
    lista_x = [40,550]
    lista_y = [500,560]
    archivoPdf.setStrokeColorRGB(0,0,1)

    for usuario in usuarios:
        archivoPdf.grid(lista_x,lista_y)
        archivoPdf.setFont('Helvetica',12)
        archivoPdf.drawString(lista_x[0] + 20, lista_y[1]-15, f'Usuario: {usuario.first_name} {usuario.last_name}')
        archivoPdf.drawString(lista_x[0] + 20, lista_y[1]-35, f'{usuario.username}')
        archivoPdf.drawString(lista_x[0] + 120, lista_y[1]-35, f'{usuario.datosusuario.fechaIngreso.strftime("%d-%m-%Y")}')
        archivoPdf.drawString(lista_x[0] + 220, lista_y[1]-35, f'{usuario.datosusuario.nroCelular}')
        tareasUsuario = tareasInformacion.objects.filter(usuarioRelacionado=usuario)
        archivoPdf.drawString(lista_x[0] + 20, lista_y[1]-55, f'Cantidad de tareas: {tareasUsuario.count()}')
        archivoPdf.drawString(lista_x[0] + 170, lista_y[1]-55, f'{usuario.datosusuario.tipoUsuario}')
        lista_y[0] = lista_y[0] - 80
        lista_y[1] = lista_y[1] - 80

    archivoPdf.save()
    reporteUsuarios=open(nombreArchivo,'rb')
    return FileResponse(reporteUsuarios,as_attachment=True)

def conseguirInfoUsuario(request):
    idEditar = request.GET.get('idEditar')
    usuario = User.objects.get(id=idEditar)
    return JsonResponse({
        'nombreUsuario':usuario.first_name,
        'apellidoUsuario':usuario.last_name,
        'profesionUsuario':usuario.datosusuario.profesionUsuario,
        'emailUsuario':usuario.email,
        'tipoUsuario':usuario.datosusuario.tipoUsuario,
        'nroCelularUsuario':usuario.datosusuario.nroCelular,
        'idUsuario':str(idEditar),
        'perfilUsuario': usuario.datosusuario.perfilUsuario,
    })

def actualizarUsuario(request):
    datos = json.load(request)
    profesion = datos.get('profesion')
    nroCelular = datos.get('nroCelular')
    idUsuario = datos.get('idUsuario')
    usuario = User.objects.get(id=idUsuario)

    usuario.datosusuario.profesionUsuario = profesion
    usuario.datosusuario.nroCelular = nroCelular
    usuario.datosusuario.save()
    return JsonResponse({
        'resp':'ok'
    })

def actualizarTarea(request):
    idTarea = request.GET.get('idTarea')
    tarea = tareasInformacion.objects.get(id=idTarea)
    datos = json.load(request)
    estadoTarea = datos.get('estadoTarea')
    
    tarea.estadoTarea = estadoTarea
    tarea.save()
    return JsonResponse({
        'resp':'ok'
    })