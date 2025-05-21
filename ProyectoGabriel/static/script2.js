
function actualizarDatos() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('temp_ambiente').textContent = data.temp_ambiente;
            document.getElementById('aire_en_uso').textContent = `Aire ${data.aire_en_uso}`;
            document.getElementById('turno_restante').textContent = data.turno_restante;

            for (let i = 1; i <= 2; i++) {
                document.getElementById(`relay_${i}`).textContent = data[`relay_${i}`] ? 'Encendido' : 'Apagado';
                document.getElementById(`corriente_${i}`).textContent = data[`corriente_${i}`];
                document.getElementById(`temp_aire_${i}`).textContent = data[`temp_aire_${i}`];

                const corriente = data[`corriente_${i}`];
                const relay = data[`relay_${i}`];
                const ok = !relay || (corriente > 4.5 && corriente <= 6.5);
                document.getElementById(`corriente_ok_${i}`).textContent = ok ? '✅' : '⚠️';
                document.getElementById(`salud_${i}`).textContent = ok ? 'OK' : 'Revisar';
                document.getElementById(`salud_${i}`).className = ok ? 'ok' : 'alerta';
            }

            // Mostrar alertas
            const alertasDiv = document.getElementById('alertas');
            if (data.alertas.length > 0) {
                alertasDiv.innerHTML = "<strong>⚠️ Alertas:</strong><ul>" + 
                    data.alertas.map(a => `<li>${a}</li>`).join('') + "</ul>";
            } else {
                alertasDiv.innerHTML = "<span class='ok'>✅ Sin alertas</span>";
            }
        });
}

setInterval(actualizarDatos, 5000);
actualizarDatos();

// Función para cambiar el modo (automático/manual)
function cambiarModo() {
    const modo = document.getElementById('modo').value;
    const esManual = modo === 'manual';
    fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ modo_manual: esManual })
    });
}

// Función para cambiar la temperatura deseada
function cambiarTempDeseada() {
    const temp = parseFloat(document.getElementById('temp_deseada').value);
    fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ temp_objetivo: temp })
    });
}

// Función para controlar el encendido/apagado de los aires manualmente
function controlarAire(aire, encender) {
    const estado_manual = [
        aire === 1 ? encender : document.getElementById('relay_1').textContent === 'Encendido',
        aire === 2 ? encender : document.getElementById('relay_2').textContent === 'Encendido'
    ];
    fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ estado_manual: estado_manual })
    });
}

// Función para actualizar el historial de eventos
function actualizarHistorial(pagina = 1) {
    fetch(`/api/historial?pagina=${pagina}`)
        .then(response => response.json())
        .then(data => {
            const historialDiv = document.getElementById('historial');
            if (!data.eventos || data.eventos.length === 0) {
                historialDiv.innerHTML = "<p>No hay eventos registrados.</p>";
                return;
            }

            let html = "<table><thead><tr><th>Fecha y Hora</th><th>Evento</th></tr></thead><tbody>";
            data.eventos.forEach(evento => {
                html += `<tr><td>${evento.timestamp}</td><td>${evento.descripcion}</td></tr>`;
            });
            html += "</tbody></table>";
            historialDiv.innerHTML = html;
        });
}

// Función para cambiar de página en el historial
function cambiarPagina(direccion) {
    const historialDiv = document.getElementById('historial');
    let paginaActual = parseInt(historialDiv.getAttribute('data-pagina'));
    paginaActual += direccion;
    if (paginaActual < 1) paginaActual = 1;
    historialDiv.setAttribute('data-pagina', paginaActual);
    actualizarHistorial(paginaActual);
}

// Función para borrar el historial de eventos
function borrarHistorial() {
    fetch('/api/historial/clear', { method: 'POST' })
        .then(() => actualizarHistorial());
}

// Función para descargar el historial de eventos
function descargarHistorial() {
    fetch('/api/historial/download')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'historial.txt';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        });
}

// Llamar a la función para actualizar el historial al cargar la página
actualizarHistorial();

