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
