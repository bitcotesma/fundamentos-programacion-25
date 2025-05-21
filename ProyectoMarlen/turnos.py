import csv
from datetime import datetime, timedelta

# Configuración
fecha_inicio = datetime(2025, 5, 13)
cantidad_dias = 5  # Genera turnos para 5 días

with open('turnos.csv', mode='w', newline='', encoding='utf-8') as archivo:
    writer = csv.writer(archivo)
    writer.writerow(['fecha', 'hora', 'tipo', 'disponible'])

    for i in range(cantidad_dias):
        fecha = fecha_inicio + timedelta(days=i)

        # Turnos con contraste (08:00 a 12:30, cada 1 hora)
        hora = datetime.strptime('08:00', '%H:%M')
        fin = datetime.strptime('12:30', '%H:%M')
        while hora <= fin:
            writer.writerow([fecha.date(), hora.strftime('%H:%M'), 'con_contraste', 'si'])
            hora += timedelta(hours=1)

        # Turnos sin contraste (13:00 a 19:30, cada 30 minutos)
        hora = datetime.strptime('13:00', '%H:%M')
        fin = datetime.strptime('19:30', '%H:%M')
        while hora <= fin:
            writer.writerow([fecha.date(), hora.strftime('%H:%M'), 'sin_contraste', 'si'])
            hora += timedelta(minutes=30)

print("Archivo 'turnos.csv' generado con éxito.")
