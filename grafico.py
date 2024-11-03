import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os



def obtener_precio_diario(mercado, simbolo, fecha_desde, fecha_hasta):
    url = f"https://api.invertironline.com/api/v2/{mercado}/Titulos/{simbolo}/Cotizacion/seriehistorica/{fecha_desde}/{fecha_hasta}/sinAjustar"
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6ImF0K2p3dCJ9.eyJzdWIiOiI1NzI4MTkiLCJJRCI6IjU3MjgxOSIsImp0aSI6ImI5NWVmYjBlLTY1M2MtNDhmMy1iY2M2LWExNGIwMTkzYzRjZCIsImNvbnN1bWVyX3R5cGUiOiIxIiwidGllbmVfY3VlbnRhIjoiVHJ1ZSIsInRpZW5lX3Byb2R1Y3RvX2J1cnNhdGlsIjoiVHJ1ZSIsInRpZW5lX3Byb2R1Y3RvX2FwaSI6IlRydWUiLCJ0aWVuZV9UeUMiOiJUcnVlIiwibmJmIjoxNzMwNjY3ODE2LCJleHAiOjE3MzA2Njg3MTYsImlhdCI6MTczMDY2NzgxNiwiaXNzIjoiSU9MT2F1dGhTZXJ2ZXIiLCJhdWQiOiJJT0xPYXV0aFNlcnZlciJ9.A-xbqYIhV8wWb72yxMWMSYct7Ax3aExx8Fxykx-JMko8x71kBvOKzXWp0jpP4J7jpcj28PNYtAfEdsBmUSpCV0M9pa42AvVfjcRmuZRy3wH65c5G_qP9IBE34pjLqsVhIzCp0NcSPZI0LC5dxEGLczNLdqWeb3Zsnrmw-YvY_XRQSU4kYoYcse5KncLbw79vCRYcmI-AZpItCQ9K7L8oytfRoCwTKxfnb5PHWZyDZgyBcc9Loxw1xriQOJWWBGBc7GISTyRm5EfKH6QI9mUDheS3bQVK0jNGcMLT_h-1CR9UczhuYOZGCJ34JRWnaCajR4fjRnofzlAyjkc8eZ_e_Q'
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
