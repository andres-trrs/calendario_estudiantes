from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario

def muestrahome (request):
    return render (request, 'home.html')

def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        try:
            usuario = Usuario.objects.get(correo=correo, contrasena=contrasena)
            # Acceso concedido, redirige a donde quieras
            return redirect('home')  # Cambia 'home' por tu vista deseada
        except Usuario.DoesNotExist:
            messages.error(request, "Credenciales incorrectas")
    return render(request, 'login.html')
