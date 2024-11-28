from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario, Evento
from django.shortcuts import get_object_or_404
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
import smtplib
from email.message import EmailMessage


def muestrahome(request):
    correo = request.session.get('correo')  # Recuperamos el correo de la sesión
    if correo:
        print(correo)  # Imprimimos el correo en la terminal
    else:
        return redirect('login')  # Si no hay correo, redirigimos a login
    
    return render(request, 'home.html')

def login(request):
    # Limpia los mensajes de la sesión antes de mostrar la vista de login
    messages.get_messages(request).used = True

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





# Crear un programador global
scheduler = BackgroundScheduler()
scheduler.start()

def enviar_correo(remitente, correo, asunto, mensaje_html):
    """Función para enviar correos electrónicos."""
    try:
        email = EmailMessage()
        email["From"] = remitente
        email["To"] = correo
        email["Subject"] = asunto
        email.add_alternative(mensaje_html, subtype="html")

        # Enviar el correo utilizando el servidor SMTP de Gmail
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(remitente, "bkbh bhgt uawl aakf")  # Cambia por tu contraseña de aplicación
        smtp.send_message(email)
        smtp.quit()
        print(f"Correo enviado exitosamente a {correo}.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

def agregar_evento(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        titulo = request.POST.get('titulo')
        fecha = request.POST.get('fecha')  # Fecha en formato 'YYYY-MM-DD'
        hora_inicio = request.POST.get('hora_inicio')  # Hora en formato 'HH:MM'
        hora_fin = request.POST.get('hora_fin')
        ubicacion = request.POST.get('ubicacion')
        correo = request.session.get('correo')

        # Validación básica
        if titulo and fecha and hora_inicio and hora_fin:
            # Crear el evento
            evento = Evento.objects.create(
                titulo=titulo,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                ubicacion=ubicacion,
                correo=correo
            )

            try:
                # Datos del remitente y asunto
                remitente = 'calendarioeventos75@gmail.com'
                asunto_confirmacion = f"Confirmación de Evento: {titulo}"
                asunto_recordatorio = f"Recordatorio de Evento: {titulo}"

                # Contenido del correo de confirmación
                mensaje_confirmacion = f"""
               <html>
                    <body style="background-image: url('https://www.oxfordcollegemitarende.it/wp-content/uploads/2022/10/Come-leggere-e-scrivere-le-date-in-inglese-Blog.jpg'); 
                                background-size: cover; 
                                background-repeat: no-repeat; 
                                background-position: center; 
                                padding: 20px; 
                                font-family: Arial, sans-serif;">
                        <div style="background-color: rgba(0, 0, 0, 0.7); /* Fondo negro con transparencia */
                                    padding: 30px; 
                                    border-radius: 15px; 
                                    max-width: 600px; 
                                    margin: 0 auto; 
                                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h2 style="text-align: center; color: #fff;">Confirmación de Evento</h2>
                            <ul style="list-style: none; padding: 0; color: #fff;">
                                <li><strong>Título:</strong> {titulo}</li>
                                <li><strong>Fecha:</strong> {fecha}</li>
                                <li><strong>Hora de Inicio:</strong> {hora_inicio}</li>
                                <li><strong>Hora de Término:</strong> {hora_fin}</li>
                                <li><strong>Ubicación:</strong> {ubicacion}</li>
                            </ul>
                            <h3 style="text-align: center; color: #fff;">¿Qué tan satisfecho estás con este sistema?</h3>
                            <!-- Usamos una tabla para garantizar la alineación de las estrellas -->
                            <table role="presentation" style="width: 100%; margin: 20px 0;">
                                <tr>
                                    <td style="text-align: center;">
                                        <button style="background-color: transparent; border: none; cursor: pointer; outline: none;" title="1 estrella">
                                            <img src="https://cdn-icons-png.flaticon.com/512/616/616489.png" alt="1 estrella" width="30">
                                        </button>
                                    </td>
                                    <td style="text-align: center;">
                                        <button style="background-color: transparent; border: none; cursor: pointer; outline: none;" title="2 estrellas">
                                            <img src="https://cdn-icons-png.flaticon.com/512/616/616489.png" alt="2 estrellas" width="30">
                                        </button>
                                    </td>
                                    <td style="text-align: center;">
                                        <button style="background-color: transparent; border: none; cursor: pointer; outline: none;" title="3 estrellas">
                                            <img src="https://cdn-icons-png.flaticon.com/512/616/616489.png" alt="3 estrellas" width="30">
                                        </button>
                                    </td>
                                    <td style="text-align: center;">
                                        <button style="background-color: transparent; border: none; cursor: pointer; outline: none;" title="4 estrellas">
                                            <img src="https://cdn-icons-png.flaticon.com/512/616/616489.png" alt="4 estrellas" width="30">
                                        </button>
                                    </td>
                                    <td style="text-align: center;">
                                        <button style="background-color: transparent; border: none; cursor: pointer; outline: none;" title="5 estrellas">
                                            <img src="https://cdn-icons-png.flaticon.com/512/616/616489.png" alt="5 estrellas" width="30">
                                        </button>
                                    </td>
                                </tr>
                            </table>
                            <p style="text-align: center; color: #ccc; margin-top: 20px;">Gracias por usar nuestro sistema de eventos.</p>
                        </div>
                    </body>
                </html>
                """


                # Contenido del correo de recordatorio
                mensaje_recordatorio = f"""
                <html>
                    <body style="background-image: url('https://www.oxfordcollegemitarende.it/wp-content/uploads/2022/10/Come-leggere-e-scrivere-le-date-in-inglese-Blog.jpg'); 
                                background-size: cover; 
                                background-repeat: no-repeat; 
                                background-position: center; 
                                padding: 20px; 
                                font-family: Arial, sans-serif;">
                        <div style="background-color: rgba(0, 0, 0, 0.7); /* Fondo negro con transparencia */
                                    padding: 30px; 
                                    border-radius: 15px; 
                                    max-width: 600px; 
                                    margin: 0 auto; 
                                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h2 style="text-align: center; color: #333;">Recordatorio de Evento</h2>
                            <ul style="list-style: none; padding: 0; color: #333;">
                                <li><strong>Título:</strong> {titulo}</li>
                                <li><strong>Fecha:</strong> {fecha}</li>
                                <li><strong>Hora de Inicio:</strong> {hora_inicio}</li>
                                <li><strong>Hora de Término:</strong> {hora_fin}</li>
                                <li><strong>Ubicación:</strong> {ubicacion}</li>
                            </ul>
                            <h3 style="text-align: center; color: #555;">¿Qué tan satisfecho estás con este sistema?</h3>
                            
                            <!-- Usamos una tabla para garantizar la alineación de las estrellas -->
                            <table role="presentation" style="width: 100%; margin: 20px 0;">
                                <tr>
                                    <td style="text-align: center;">
                                        <button style="background-color: transparent; border: none; cursor: pointer; outline: none;" title="1 estrella">
                                            <img src="https://cdn-icons-png.flaticon.com/512/616/616489.png" alt="1 estrella" width="30">
                                        </button>
                                    </td>
                                    <td style="text-align: center;">
                                        <button style="background-color: transparent; border: none; cursor: pointer; outline: none;" title="2 estrellas">
                                            <img src="https://cdn-icons-png.flaticon.com/512/616/616489.png" alt="2 estrellas" width="30">
                                        </button>
                                    </td>
                                    <td style="text-align: center;">
                                        <button style="background-color: transparent; border: none; cursor: pointer; outline: none;" title="3 estrellas">
                                            <img src="https://cdn-icons-png.flaticon.com/512/616/616489.png" alt="3 estrellas" width="30">
                                        </button>
                                    </td>
                                    <td style="text-align: center;">
                                        <button style="background-color: transparent; border: none; cursor: pointer; outline: none;" title="4 estrellas">
                                            <img src="https://cdn-icons-png.flaticon.com/512/616/616489.png" alt="4 estrellas" width="30">
                                        </button>
                                    </td>
                                    <td style="text-align: center;">
                                        <button style="background-color: transparent; border: none; cursor: pointer; outline: none;" title="5 estrellas">
                                            <img src="https://cdn-icons-png.flaticon.com/512/616/616489.png" alt="5 estrellas" width="30">
                                        </button>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="text-align: center; color: #777; margin-top: 20px;">Gracias por usar nuestro sistema de eventos.</p>
                        </div>
                    </body>
                </html>
                """

                # Enviar el correo de confirmación inmediatamente
                enviar_correo(remitente, correo, asunto_confirmacion, mensaje_confirmacion)

                # Programar el recordatorio para la fecha y hora del evento
                fecha_hora_envio = datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M")
                scheduler.add_job(
                    enviar_correo,
                    trigger=DateTrigger(run_date=fecha_hora_envio),
                    args=[remitente, correo, asunto_recordatorio, mensaje_recordatorio]
                )

                print(f"Recordatorio programado para {fecha_hora_envio}.")

            except Exception as e:
                print(f"Error al procesar el correo: {e}")

            # Mensaje de éxito
            
            return redirect('home')
        else:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('home')

    return render(request, 'home.html')