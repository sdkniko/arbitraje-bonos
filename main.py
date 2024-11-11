import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os

# Variable para almacenar el token Bearer
BEARER_TOKEN = ''

def obtener_token():
    global BEARER_TOKEN
    try:
        response = requests.post('https://api.invertironline.com/token', data={
            'username': 'sdkniko',
            'password': 'Niko2137!',
            'grant_type': 'password'
        })
        response.raise_for_status()
        BEARER_TOKEN = response.json()['access_token']
        print('Token obtenido:', BEARER_TOKEN)
    except requests.exceptions.RequestException as error:
        print(f'Error al obtener el token: {error}')

def obtener_precio_diario(mercado, simbolo, fecha_desde, fecha_hasta):
    url = f"https://api.invertironline.com/api/v2/{mercado}/Titulos/{simbolo}/Cotizacion/seriehistorica/{fecha_desde}/{fecha_hasta}/sinAjustar"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {BEARER_TOKEN}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return None

def graficar_precios(precios):
    fechas = []
    valores = []

    for precio in precios:
        # Ajustar la cadena para quitar 'Z' al final y los milisegundos
        fecha_str = precio['fechaHora'][:-1]  # Remover 'Z' al final
        fecha_str = fecha_str[:-3]  # Remover los últimos 3 caracteres (milisegundos)

        try:
            fecha = datetime.fromisoformat(fecha_str)  # Convertir a datetime
            fecha_sin_hora = fecha.date()  # Quedarse solo con la fecha (sin hora)
            fechas.append(fecha_sin_hora)  # Agregar la fecha sin hora
            valores.append(precio['ultimoPrecio'])  # Agregar el precio
        except ValueError as e:
            print(f"Error al convertir la fecha: {fecha_str}, error: {e}")

    # Ahora puedes graficar con fechas y valores
    plt.figure(figsize=(10, 5))
    plt.plot(fechas, valores, marker='o')
    plt.title('Precio del Activo por Día')
    plt.xlabel('Fecha')
    plt.ylabel('Último Precio')
    plt.xticks(rotation=45)
    plt.grid()
    plt.tight_layout()
    plt.show()

def main():
    # Obtener el token al inicio del script
    obtener_token()
    
    mercado = 'bCBA'
    simbolo = os.getenv('SIMBOLO')
    fecha_desde = os.getenv('FECHA_DESDE')
    fecha_hasta = os.getenv('FECHA_HASTA')

    precios = obtener_precio_diario(mercado, simbolo, fecha_desde, fecha_hasta)

    if precios:
        graficar_precios(precios)

if __name__ == "__main__":
    main()
