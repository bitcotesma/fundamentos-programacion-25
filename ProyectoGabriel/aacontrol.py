from flask import Flask, render_template, jsonify, request
import threading, time, random

app = Flask(__name__)

# Valores de referencia
TEMP_MIN = 22.0
TEMP_MAX = 26.0
CORRIENTE_MIN = 4.5
CORRIENTE_MAX = 6.5

# Variables globales
modo_manual = False
estado_manual = [False, False]
temp_objetivo = 24.0
temp_max_offset = 0.5  # Nuevo: diferencia máxima sobre el objetivo

sensor_data = {
    'temp_aire_1': 24.0,
    'temp_aire_2': 24.5,
    'temp_ambiente': 26.0,
    'corriente_1': 0.0,
    'corriente_2': 0.0,
    'relay_1': False,
    'relay_2': False,
    'aire_en_uso': 1,
    'turno_restante': '12h 32min',
    'alertas': []
}

historial_eventos = []

def agregar_evento(tipo, descripcion):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    historial_eventos.insert(0, {'timestamp': timestamp, 'tipo': tipo, 'descripcion': descripcion})
    if len(historial_eventos) > 100:
        historial_eventos.pop()

def simular_datos():
    temp_salida_ok = 5.0  # Temperatura de salida esperada cuando el aire funciona bien
    histeresis = 0.5      # Medio grado de margen

    while True:
        if modo_manual:
            sensor_data['relay_1'] = estado_manual[0]
            sensor_data['relay_2'] = estado_manual[1]
        else:
            # Control automático con histéresis y offset configurable
            if sensor_data['temp_ambiente'] > temp_objetivo + temp_max_offset:
                # Encender aire en uso
                sensor_data['aire_en_uso'] = 1 if time.localtime().tm_mday % 2 == 0 else 2
                sensor_data['relay_1'] = sensor_data['aire_en_uso'] == 1
                sensor_data['relay_2'] = sensor_data['aire_en_uso'] == 2
            elif sensor_data['temp_ambiente'] < temp_objetivo - histeresis:
                # Apagar ambos aires
                sensor_data['relay_1'] = False
                sensor_data['relay_2'] = False

        # Simulación de corriente y temperatura de salida
        for i in [1, 2]:
            if sensor_data[f'relay_{i}']:
                sensor_data[f'corriente_{i}'] = random.uniform(CORRIENTE_MIN, CORRIENTE_MAX)
                # Si el aire está encendido y corriente es correcta, salida baja
                sensor_data[f'temp_aire_{i}'] = temp_salida_ok + random.uniform(0, 1)
            else:
                sensor_data[f'corriente_{i}'] = 0.0
                sensor_data[f'temp_aire_{i}'] = round(random.uniform(20, 26), 1)

        # Simulación de temperatura ambiente
        if sensor_data['relay_1'] or sensor_data['relay_2']:
            # Si algún aire está funcionando bien, la temperatura ambiente baja
            sensor_data['temp_ambiente'] -= random.uniform(0.1, 0.3)
        else:
            # Si ambos están apagados, la temperatura ambiente sube
            sensor_data['temp_ambiente'] += random.uniform(0.05, 0.2)
        # Limitar valores razonables
        sensor_data['temp_ambiente'] = max(18.0, min(35.0, sensor_data['temp_ambiente']))
        sensor_data['temp_ambiente'] = round(sensor_data['temp_ambiente'], 1)

        # Alertas
        alertas = []
        if sensor_data['temp_ambiente'] > TEMP_MAX:
            alerta = "⚠️ Temperatura ambiente fuera de rango (alta)"
            alertas.append(alerta)
            agregar_evento("Alerta", alerta)
        elif sensor_data['temp_ambiente'] < TEMP_MIN:
            alerta = "⚠️ Temperatura ambiente fuera de rango (baja)"
            alertas.append(alerta)
            agregar_evento("Alerta", alerta)

        for i in [1, 2]:
            corriente = sensor_data[f'corriente_{i}']
            temp_salida = sensor_data[f'temp_aire_{i}']
            if sensor_data[f'relay_{i}']:
                if corriente == 0.0:
                    alerta = f"❌ Aire {i} encendido pero sin consumo eléctrico"
                    alertas.append(alerta)
                    agregar_evento("Alerta", alerta)
                elif corriente > CORRIENTE_MAX:
                    alerta = f"⚠️ Aire {i} consume más de lo normal"
                    alertas.append(alerta)
                    agregar_evento("Alerta", alerta)
                # Verificar temperatura de salida
                if temp_salida > temp_salida_ok + 2:
                    alerta = f"⚠️ Aire {i} encendido pero la temperatura de salida es alta ({temp_salida}°C)"
                    alertas.append(alerta)
                    agregar_evento("Alerta", alerta)

        sensor_data['alertas'] = alertas
        sensor_data['turno_restante'] = "Simulado"

        time.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify(sensor_data)

@app.route('/api/control', methods=['POST'])
def control():
    global modo_manual, estado_manual, temp_objetivo, temp_max_offset
    data = request.get_json()

    if 'modo_manual' in data:
        modo_manual = data['modo_manual']
        agregar_evento("Control", f"Modo manual {'activado' if modo_manual else 'desactivado'}")

    if 'estado_manual' in data:
        estado_manual = data['estado_manual']
        agregar_evento("Control", f"Estado manual: Aire 1 {'ON' if estado_manual[0] else 'OFF'}, Aire 2 {'ON' if estado_manual[1] else 'OFF'}")

    if 'temp_objetivo' in data:
        temp_objetivo = data['temp_objetivo']
        agregar_evento("Control", f"Temperatura objetivo actualizada a {temp_objetivo}°C")

    if 'temp_max_offset' in data:
        temp_max_offset = data['temp_max_offset']
        agregar_evento("Control", f"Offset de temperatura máxima actualizado a +{temp_max_offset}°C")

    return jsonify({'success': True})
    
@app.route('/api/historial')
def historial():
    pagina = int(request.args.get('pagina', 1))
    eventos_por_pagina = 20
    inicio = (pagina - 1) * eventos_por_pagina
    fin = inicio + eventos_por_pagina
    return jsonify({'eventos': historial_eventos[inicio:fin]})

@app.route('/api/historial/clear', methods=['POST'])
def borrar_historial():
    historial_eventos.clear()
    return jsonify({'success': True})

@app.route('/api/historial/download')
def descargar_historial():
    contenido = "Fecha y Hora,Tipo,Descripción\n"
    for evento in historial_eventos:
        contenido += f"{evento['timestamp']},{evento['tipo']},{evento['descripcion']}\n"
    return contenido, 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': 'attachment; filename=\"historial.txt\"'
    }

if __name__ == '__main__':
    thread = threading.Thread(target=simular_datos)
    thread.daemon = True
    thread.start()
    app.run(debug=True)
