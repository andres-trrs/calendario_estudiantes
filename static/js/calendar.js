document.addEventListener('DOMContentLoaded', function() {
    let requestCalendar = "/api/eventos/"; // Nueva URL para obtener los eventos

    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es', // Configuración para español
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        // Personalización de los textos de los botones
        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día'
        },
        // Personalización de los iconos de navegación
        buttonIcons: {
            prev: 'chevron-left',
            next: 'chevron-right'
        },
        events: function(info, successCallback, failureCallback) {
            fetch(requestCalendar)
                .then(response => response.json())
                .then(data => {
                    let eventos = data.events.map(evento => ({
                        title: evento.eventTitle,
                        start: new Date(evento.eventStartDate),
                        end: new Date(evento.eventEndDate),
                        location: evento.eventLocation,
                        timeStart: evento.eventStartTime,
                        timeEnd: evento.eventEndTime
                    }));
                    successCallback(eventos);
                })
                .catch(error => failureCallback(error));
        },

        events: function(info, successCallback, failureCallback) {
            fetch(requestCalendar)
                .then(response => response.json())
                .then(data => {
                    let eventos = data.events.map(evento => ({
                        title: evento.eventTitle,
                        start: new Date(evento.eventStartDate + " " + evento.eventStartTime),
                        end: new Date(evento.eventEndDate + " " + evento.eventEndTime),
                        location: evento.eventLocation,
                        timeStart: evento.eventStartTime,
                        timeEnd: evento.eventEndTime
                    }));
                    successCallback(eventos);
                })
                .catch(error => failureCallback(error));
        },

        eventClick: function(info) {
            // Evita el comportamiento predeterminado
            info.jsEvent.preventDefault();
        
            // Muestra el popup centrado
            const popup = document.getElementById('eventActionPopup');
            popup.style.display = 'flex';
        
            // Añadir evento para cerrar el popup al hacer clic fuera
            popup.addEventListener('click', function(event) {
                if (event.target === popup) {
                    popup.style.display = 'none';
                }
            });
        
            // Botones en el popup (actualmente sin funcionalidad)
            const editButton = document.getElementById('editEventButton');
            const deleteButton = document.getElementById('deleteEventButton');
        
            // Opción de agregar funcionalidad futura aquí
            editButton.addEventListener('click', function() {
                console.log('Editar evento');
            });
        
            deleteButton.addEventListener('click', function() {
                confirmDeleteButton.addEventListener('click', () => {
                    confirmDeleteModal.style.display = 'none';
                    // Aquí puedes agregar la lógica para eliminar el evento
                    alert(info.event.title)
                    alert(info.event.extendedProps.timeStart)
                    alert(info.event.extendedProps.timeEnd)
                    alert(info.event.extendedProps.location)
                });
            });
        },

        eventContent: function(arg) {
            const event = arg.event;
            const location = event.extendedProps.location;
            const timeStart = event.extendedProps.timeStart;
            const timeEnd = event.extendedProps.timeEnd;

            const eventElement = document.createElement('div');
            eventElement.innerHTML = `
                <b>${event.title}</b><br>
                <span>${location}</span><br>
                <span>${timeStart} - ${timeEnd}</span>
            `;
            return { domNodes: [eventElement] };
        }
    });

    calendar.render();

    // Control de botones y formulario
    const addEventButton = document.getElementById('addEventButton');
    const eventPopup = document.getElementById('eventPopup');
    const cancelEventButton = document.getElementById('cancelEventButton');
    const saveEventButton = document.getElementById('saveEventButton');
    const menu = document.getElementById('menu');

    addEventButton.addEventListener('click', () => {
        eventPopup.style.display = 'block';
        menu.style.display = 'none';
    });

    cancelEventButton.addEventListener('click', () => {
        eventPopup.style.display = 'none';
    });

    saveEventButton.addEventListener('click', () => {
        const title = document.getElementById('eventTitle').value.trim();
        const date = document.getElementById('eventDate').value.trim();
        const startTime = document.getElementById('eventStartTime').value.trim();
        const endTime = document.getElementById('eventEndTime').value.trim();
        const location = document.getElementById('eventLocation').value.trim();

         // Validaciones (mantenemos las que ya existen)
    const missingFields = [];
    if (!title) missingFields.push('título');
    if (!date) missingFields.push('fecha');
    if (!startTime) missingFields.push('hora de inicio');
    if (!endTime) missingFields.push('hora de fin');

    if (missingFields.length > 0) {
        alert(`Por favor, complete los siguientes campos: ${missingFields.join(', ')}`);
        return;
    }


        // Validación de horarios
    const startDateTime = new Date(`${date}T${startTime}`);
    const endDateTime = new Date(`${date}T${endTime}`);

    if (endDateTime <= startDateTime) {
        alert('La hora de fin debe ser posterior a la hora de inicio');
        return;
    }
    // Crear objeto del nuevo evento
    const newEvent = {
        eventTitle: title,
        eventStartDate: date,
        eventEndDate: date, // Mismo día para eventos de un día
        eventStartTime: startTime,
        eventEndTime: endTime,
        eventLocation: location,
        eventUrl: "https://fullcalendar.io/" // URL por defecto
    };

    

        // Si todas las validaciones pasan, crear el evento
        calendar.addEvent({
            title: title,
            start: startDateTime,
            end: endDateTime,
            location: location,
            timeStart: startTime,
            timeEnd: endTime
        });

        // Limpiar y cerrar el formulario
        eventPopup.style.display = 'none';
        document.getElementById('eventTitle').value = '';
        document.getElementById('eventDate').value = '';
        document.getElementById('eventStartTime').value = '';
        document.getElementById('eventEndTime').value = '';
        document.getElementById('eventLocation').value = '';
    });

    // Control del botón de menú
    document.getElementById("toggleMenuButton").addEventListener("click", function() {
        if (menu.style.display === "block") {
            menu.style.display = "none";
        } else {
            menu.style.display = "block";
            eventPopup.style.display = 'none';
        }
    });

    // Click fuera para cerrar
    document.addEventListener("click", function(event) {
        if (!menu.contains(event.target) && 
            !document.getElementById("toggleMenuButton").contains(event.target) && 
            !eventPopup.contains(event.target)) {
            menu.style.display = "none";
        }
    });
});

// Agregar después de la declaración de los otros botones
const logoutButton = document.getElementById('logoutButton');

// Agregar el evento click
logoutButton.addEventListener('click', () => {
    if (confirm('¿Estás seguro que deseas cerrar sesión?')) {
        // Aquí puedes agregar la lógica para cerrar sesión
        alert('Cerrando sesión...'); // Placeholder

        // Obtener la URL de login desde el atributo 'data-login-url'
        const loginUrl = logoutButton.getAttribute('data-login-url');

        // Redirigir al usuario a la página de login
        window.location.href = loginUrl;
    }
    menu.style.display = 'none'; // Cerrar el menú
});
document.addEventListener("DOMContentLoaded", function () {
    // Inicialización del calendario
    let requestCalendar = "/api/eventos/";
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        // Configuración del calendario
    });

    calendar.render();

    // Lógica del botón para abrir/cerrar el menú
    const toggleMenuButton = document.getElementById("toggleMenuButton");
    const menu = document.getElementById("menu");

    toggleMenuButton.addEventListener("click", function () {
        // Mostrar u ocultar el menú
        if (menu.style.display === "block") {
            menu.style.display = "none";
        } else {
            menu.style.display = "block";
        }
    });

    // Cierra el menú al hacer clic fuera
    document.addEventListener("click", function (event) {
        if (!menu.contains(event.target) && 
            !toggleMenuButton.contains(event.target)) {
            menu.style.display = "none";
        }
    });
});

// Abrir el popup de edición de eventos
document.querySelector('#editEventButton').addEventListener('click', () => {
    document.querySelector('#editEventPopup').classList.add('show');
});

// Cerrar el popup al hacer clic en el botón "Cancelar"
document.querySelector('#cancelEditButton').addEventListener('click', () => {
    document.querySelector('#editEventPopup').classList.remove('show');
});

// Cerrar el popup si se hace clic fuera del contenido
document.addEventListener('click', (e) => {
    const popup = document.querySelector('#editEventPopup');
    if (!popup.contains(e.target) && e.target.id !== 'editEventButton') {
        popup.classList.remove('show');
    }
});
const deleteEventButton = document.getElementById('deleteEventButton');
        const confirmDeleteModal = document.getElementById('confirmDeleteModal');
        const confirmDeleteButton = document.getElementById('confirmDeleteButton');
        const cancelDeleteButton = document.getElementById('cancelDeleteButton');

        // Mostrar el modal al hacer clic en "Eliminar evento"
        deleteEventButton.addEventListener('click', () => {
            confirmDeleteModal.style.display = 'block';
        });

        // Cerrar el modal al hacer clic en "Cancelar"
        cancelDeleteButton.addEventListener('click', () => {
            confirmDeleteModal.style.display = 'none';
        });

        // Acción de confirmación de eliminación
        confirmDeleteButton.addEventListener('click', () => {
            confirmDeleteModal.style.display = 'none';
            // Aquí puedes agregar la lógica para eliminar el evento
            alert('Evento eliminado correctamente.');
        });

const saveChangesButton = document.getElementById('saveChangesButton');

saveChangesButton.addEventListener('click', () => {
    const eventId = document.getElementById('editEventId').value; // ID del evento que se está editando
    const title = document.getElementById('editEventTitle').value.trim();
    const date = document.getElementById('editEventDate').value.trim();
    const startTime = document.getElementById('editEventStartTime').value.trim();
    const endTime = document.getElementById('editEventEndTime').value.trim();
    const location = document.getElementById('editEventLocation').value.trim();

    // Validar datos
    if (!title || !date || !startTime || !endTime) {
        alert('Por favor, complete todos los campos obligatorios.');
        return;
    }

    // Validar horario
    const startDateTime = new Date(`${date}T${startTime}`);
    const endDateTime = new Date(`${date}T${endTime}`);
    if (endDateTime <= startDateTime) {
        alert('La hora de fin debe ser posterior a la hora de inicio.');
        return;
    }

    // Datos a enviar al backend
    const updatedEvent = {
        title: title,
        start: date,
        start_time: startTime,
        end_time: endTime,
        location: location,
    };

    // Realizar la solicitud PUT al backend
    fetch(`/editar_evento/${eventId}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedEvent),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === 'success') {
                // Mostrar mensaje de éxito
                alert('Los datos han sido actualizados correctamente.');

                // Cerrar el popup
                document.querySelector('#editEventPopup').classList.remove('show');

                // Recargar el calendario para reflejar los cambios
                calendar.refetchEvents();
            } else {
                alert(`Error: ${data.message || 'No se pudo actualizar el evento.'}`);
            }
        })
        .catch((error) => {
            console.error('Error al actualizar el evento:', error);
            alert('Ocurrió un error inesperado.');
        });
});
