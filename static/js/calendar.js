document.addEventListener('DOMContentLoaded', function() {
    let requestCalendar = "/api/eventos/"; // Nueva URL para obtener los eventos

    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es', // Configuración para español
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

            // Muestra los detalles del evento
            alert(
                `Nombre del evento: ${info.event.title}\n` +
                `Ubicación: ${info.event.extendedProps.location}\n` +
                `Fecha: ${info.event.start.toLocaleDateString()}\n` +
                `Hora: ${info.event.extendedProps.timeStart} - ${info.event.extendedProps.timeEnd}`
            );
        },

        eventContent: function(arg) {
            // Personaliza el contenido que se muestra en el calendario
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

    // Opciones adicionales: mostrar un popup para agregar eventos manualmente
    const addEventButton = document.getElementById('addEventButton');
    const eventPopup = document.getElementById('eventPopup');
    const cancelEventButton = document.getElementById('cancelEventButton');
    const saveEventButton = document.getElementById('saveEventButton');

    addEventButton.addEventListener('click', () => {
        eventPopup.style.display = eventPopup.style.display === 'none' ? 'block' : 'none';
    });

    cancelEventButton.addEventListener('click', () => {
        eventPopup.style.display = 'none';
    });

    saveEventButton.addEventListener('click', () => {
        // Esta parte no guarda eventos directamente en el calendario,
        // sino que se puede personalizar para enviar datos al backend.
        eventPopup.style.display = 'none';
    });
});