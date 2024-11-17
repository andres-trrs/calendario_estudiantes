from django.contrib import admin
from django.urls import path
from calendarioApp.views import login, muestrahome, register, agregar_evento, obtener_eventos

urlpatterns = [
    path('admin/', admin.site.urls),
    path ('', login, name='login'),
    path('register/', register, name='register'),
    path('home/', muestrahome, name='home'),
    path('agregar-evento/', agregar_evento, name='agregar_evento'),
    path('api/eventos/', obtener_eventos, name='obtener_eventos'),
]
