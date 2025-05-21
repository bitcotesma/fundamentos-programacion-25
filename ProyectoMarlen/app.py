from flask import Flask, render_template, request, redirect
import csv
from datetime import datetime

app = Flask(__name__)

CSV_PATH = 'turnos.csv'

def cargar_turnos(tipo):
    turnos_disponibles = []
    with open(CSV_PATH, newline='', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            if fila['tipo'] == tipo and fila['disponible'] == 'si':
                turnos_disponibles.append(f"{fila['fecha']} {fila['hora']}")
    return turnos_disponibles

def marcar_turno_como_tomado(fecha, hora, datos_paciente):
    filas_actualizadas = []
    with open(CSV_PATH, newline='', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            if fila['fecha'] == fecha and fila['hora'] == hora:
                fila['disponible'] = 'no'
                fila ['nombre'] = datos_paciente.get('nombre',' ')
                fila['apellido'] = datos_paciente.get('apellido', '')
                fila['documento'] = datos_paciente.get('documento', '')
                fila['obra_social'] = datos_paciente.get('obra_social', '')
                fila['medicacion'] = datos_paciente.get('medicacion', '')
                fila['consentimiento'] = datos_paciente.get('consentimiento', '')
            filas_actualizadas.append(fila)

    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as archivo:
        campos = ['fecha', 'hora', 'tipo', 'disponible', 'nombre', 'apellido', 'documento', 'obra_social', 'medicacion', 'consentimiento']
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas_actualizadas)

@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        datos = request.form
        turno_completo = datos.get('turno_contraste')
        
        if turno_completo:
            fecha, hora = turno_completo.split("T")
            marcar_turno_como_tomado(fecha, hora, datos)
        return render_template('confirmacion.html', datos=datos)

    tipo = request.args.get('tipo')
    turnos = []
    if tipo:
        turnos = cargar_turnos(tipo)
    return render_template('formulario.html', turnos=turnos, tipo=tipo)

if __name__ == '__main__':
    app.run(debug=True)
