from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario, Evento
from django.shortcuts import get_object_or_404
import json


def muestrahome(request):
    correo = request.session.get('correo')  # Recuperamos el correo de la sesión
    if correo:
        print(correo)  # Imprimimos el correo en la terminal
    else:
        return redirect('login')  # Si no hay correo, redirigimos a login
    
    return render(request, 'home.html')

def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        
        try:
            usuario = Usuario.objects.get(correo=correo, contrasena=contrasena)
            # Guardamos el correo en la sesión
            request.session['correo'] = usuario.correo
            return redirect('home')
        except Usuario.DoesNotExist:
            messages.error(request, "Credenciales incorrectas")
    
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        
        # Verificar si el correo ya está registrado
        if Usuario.objects.filter(correo=correo).exists():
            messages.error(request, "El correo ya está registrado.")
        else:
            # Crear el usuario
            Usuario.objects.create(
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                contrasena=contrasena,
                fecha_nacimiento=fecha_nacimiento
            )
            messages.success(request, "Usuario registrado exitosamente.")
            return redirect('login')  # Redirige a la página de login tras registrarse
    
    return render(request, 'registration.html')

def agregar_evento(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        ubicacion = request.POST.get('ubicacion')
        correo = request.session.get('correo')
        # Verificamos si el usuario está autenticado
        #if request.user.is_authenticated:
            # Imprimimos el correo del usuario autenticado
        #    correo = request.user.email
        #    print(f"Correo del usuario logueado: {correo}")
        #else:
        #    print("No hay usuario autenticado.")

        # Validación básica
        if titulo and fecha and hora_inicio and hora_fin:
            Evento.objects.create(
                titulo=titulo,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                ubicacion=ubicacion,
                correo=correo,
            )
        else:
            messages.error(request, "Todos los campos son obligatorios.")

        return redirect('home')  # Redirige a la página principal después de agregar un evento
    
    return render(request, 'home.html')

def obtener_eventos(request):
    # Obtener el correo del usuario autenticado
    correo_usuario = request.session.get('correo')

    # Consultar los eventos asociados al usuario
    eventos = Evento.objects.filter(correo=correo_usuario)

    # Transformar los eventos al formato esperado por FullCalendar
    eventos_json = []
    for evento in eventos:
        eventos_json.append({
            "eventTitle": evento.titulo,
            "eventStartDate": evento.fecha.strftime('%m/%d/%Y'),  # Formato de fecha MM/DD/YYYY
            "eventEndDate": evento.fecha.strftime('%m/%d/%Y'),    # Asumiendo que el evento dura 1 día
            "eventStartTime": evento.hora_inicio.strftime('%I:%M %p'),  # Formato de hora 12H AM/PM
            "eventEndTime": evento.hora_fin.strftime('%I:%M %p'),       # Formato de hora 12H AM/PM
            "eventLocation": evento.ubicacion or "",  # Ubicación puede ser opcional
        })

    # Devolver los datos como JSON
    return JsonResponse({"events": eventos_json})

@csrf_exempt
def editar_evento(request, event_id):
    # Obtener el evento por ID
    evento = get_object_or_404(Evento, id=event_id)

    if request.method == 'GET':
        # Si es una solicitud GET, retornar los datos del evento para mostrar en el popup
        event_data = {
            'title': evento.titulo,
            'start': evento.fecha,
            'start_time': evento.hora_inicio,
            'end_time': evento.hora_fin,
            'location': evento.ubicacion
        }
        return JsonResponse(event_data)

    elif request.method == 'PUT':
        # Si es una solicitud PUT, actualizar los datos del evento
        try:
            data = json.loads(request.body)  # Obtener los datos del cuerpo de la solicitud

            # Actualizar los campos del evento con los datos proporcionados
            evento.titulo = data.get('title', evento.titulo)
            evento.fecha = data.get('start', evento.fecha)
            evento.hora_inicio = data.get('start_time', evento.hora_inicio)
            evento.hora_fin = data.get('end_time', evento.hora_fin)
            evento.ubicacion = data.get('location', evento.ubicacion)

            evento.save()  # Guardar los cambios en la base de datos
            return JsonResponse({'status': 'success', 'message': 'Evento actualizado correctamente'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)



@csrf_exempt  # O utiliza el token CSRF en el frontend
def eliminar_evento(request):
    if request.method == "POST":
        # Obtener el correo de la sesión
        correo = request.session.get('correo')
        if not correo:
            return JsonResponse({"mensaje": "No hay usuario activo"}, status=403)

        # Decodificar los datos enviados desde JavaScript
        datos = json.loads(request.body)
        titulo = datos.get('title')
        fecha = datos.get('date')  # Fecha del evento
        hora_inicio = datos.get('timeStart')
        hora_fin = datos.get('timeEnd')
        ubicacion = datos.get('location')

        # Validar que los datos requeridos estén presentes
        if not all([titulo, fecha, hora_inicio, hora_fin]):
            return JsonResponse({"mensaje": "Datos incompletos para eliminar el evento"}, status=400)

        # Buscar y eliminar el evento en la base de datos
        try:
            evento = Evento.objects.get(
                titulo=titulo,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                ubicacion=ubicacion,
                correo=correo,
            )
            evento.delete()
            return JsonResponse({"mensaje": "Evento eliminado correctamente"})
        except Evento.DoesNotExist:
            return JsonResponse({"mensaje": "Evento no encontrado"}, status=404)

    return JsonResponse({"mensaje": "Método no permitido"}, status=405)
