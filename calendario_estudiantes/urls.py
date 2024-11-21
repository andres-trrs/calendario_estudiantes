from django.contrib import admin
from django.urls import path
from calendarioApp.views import eliminar_evento, editar_evento, login, muestrahome, register, agregar_evento, obtener_eventos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login, name='login'),
    path('register/', register, name='register'),
    path('home/', muestrahome, name='home'),
    path('agregar-evento/', agregar_evento, name='agregar_evento'),
    path('api/eventos/', obtener_eventos, name='obtener_eventos'),
    path('editar_evento/<int:event_id>/', editar_evento, name='editar_evento'),
    path('eliminar_evento/<int:event_id>/', eliminar_evento, name='eliminar_evento'),
]
