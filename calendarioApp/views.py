from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario, Evento
from django.http import JsonResponse

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


