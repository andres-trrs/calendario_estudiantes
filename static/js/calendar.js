document.addEventListener('DOMContentLoaded', function() {
    let requestCalendar = "./events.json"; // Ruta al archivo de eventos

    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es',
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
        const title = document.getElementById('eventTitle').value;
        const date = document.getElementById('eventDate').value;
        const startTime = document.getElementById('eventStartTime').value;
        const endTime = document.getElementById('eventEndTime').value;
        const location = document.getElementById('eventLocation').value;

        if (title && date && startTime && endTime) {
            const eventStart = new Date(`${date}T${startTime}:00`);
            const eventEnd = new Date(`${date}T${endTime}:00`);

            calendar.addEvent({
                title: title,
                start: eventStart,
                end: eventEnd,
                location: location,
                timeStart: startTime,
                timeEnd: endTime
            });

            eventPopup.style.display = 'none';
            document.getElementById('eventTitle').value = '';
            document.getElementById('eventDate').value = '';
            document.getElementById('eventStartTime').value = '';
            document.getElementById('eventEndTime').value = '';
            document.getElementById('eventLocation').value = '';
        } else {
            alert('Por favor, complete todos los campos requeridos.');
        }
    });
});




