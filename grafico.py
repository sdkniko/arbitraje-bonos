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
    
def graficar_ratio(precios_activo1, precios_activo2):
    fechas_activo1 = []
    valores_activo1 = []
    for precio in precios_activo1:
        fecha_str = precio['fechaHora'][:-1]
        fecha_str = fecha_str[:-3]
        try:
            fecha = datetime.fromisoformat(fecha_str)
            fecha_sin_hora = fecha.date()
            fechas_activo1.append(fecha_sin_hora)
            valores_activo1.append(precio['ultimoPrecio'])
        except ValueError as e:
            print()

    fechas_activo2 = []
    valores_activo2 = []
    for precio in precios_activo2:
        fecha_str = precio['fechaHora'][:-1]
        fecha_str = fecha_str[:-3]
        try:
            fecha = datetime.fromisoformat(fecha_str)
            fecha_sin_hora = fecha.date()
            fechas_activo2.append(fecha_sin_hora)
            valores_activo2.append(precio['ultimoPrecio'])
        except ValueError as e:
            print(f"Error al convertir la fecha: {fecha_str}, error: {e}")

    # Crear un DataFrame con las fechas y los precios de ambos activos
    df = pd.DataFrame({'Fecha': fechas_activo1, 'Precio_Activo1': valores_activo1})
    df2 = pd.DataFrame({'Fecha': fechas_activo2, 'Precio_Activo2': valores_activo2})

    # Combinar los DataFrames por fecha
    df_merged = pd.merge(df, df2, on='Fecha', how='inner')

    # Calcular el ratio entre los precios
    df_merged['Ratio'] = df_merged['Precio_Activo1'] / df_merged['Precio_Activo2']

    # Calcular la media móvil del ratio
    df_merged['MediaMovil'] = df_merged['Ratio'].rolling(window=20).mean()

    # Calcular la desviación estándar del ratio
    df_merged['DesviacionEstandar'] = df_merged['Ratio'].rolling(window=20).std()

    # Calcular las bandas de Bollinger
    df_merged['BandaSuperior'] = df_merged['MediaMovil'] + 2 * df_merged['DesviacionEstandar']
    df_merged['BandaInferior'] = df_merged['MediaMovil'] - 2 * df_merged['DesviacionEstandar']

    # Graficar el ratio, la media móvil y las bandas de Bollinger
    plt.figure(figsize=(10, 5))
    plt.plot(df_merged['Fecha'], df_merged['Ratio'], label='Ratio', marker='o')
    plt.plot(df_merged['Fecha'], df_merged['MediaMovil'], label='Media Móvil', linestyle='--')
    plt.plot(df_merged['Fecha'], df_merged['BandaSuperior'], label='Banda Superior', linestyle=':')
    plt.plot(df_merged['Fecha'], df_merged['BandaInferior'], label='Banda Inferior', linestyle=':')
    plt.title('Ratio entre Activos con Media Móvil y Bandas de Bollinger')
    plt.xlabel('Fecha')
    plt.ylabel('Ratio')
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    # Obtener el token al inicio del script
    obtener_token()
    
    mercado = 'bCBA'
    simbolo1 = os.getenv('SIMBOLO1')
    simbolo2 = os.getenv('SIMBOLO2')
    fecha_desde = os.getenv('FECHA_DESDE')
    fecha_hasta = os.getenv('FECHA_HASTA')

    precios_activo1 = obtener_precio_diario(mercado, simbolo1, fecha_desde, fecha_hasta)
    precios_activo2 = obtener_precio_diario(mercado, simbolo2, fecha_desde, fecha_hasta)

    if precios_activo1 and precios_activo2:
        graficar_ratio(precios_activo1, precios_activo2)

if __name__ == "__main__":
    main()
