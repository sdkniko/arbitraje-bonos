import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os

def obtener_precio_diario(mercado, simbolo, fecha_desde, fecha_hasta):
    url = f"https://api.invertironline.com/api/v2/{mercado}/Titulos/{simbolo}/Cotizacion/seriehistorica/{fecha_desde}/{fecha_hasta}/sinAjustar"
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6ImF0K2p3dCJ9.eyJzdWIiOiI1NzI4MTkiLCJJRCI6IjU3MjgxOSIsImp0aSI6ImI5NWVmYjBlLTY1M2MtNDhmMy1iY2M2LWExNGIwMTkzYzRjZCIsImNvbnN1bWVyX3R5cGUiOiIxIiwidGllbmVfY3VlbnRhIjoiVHJ1ZSIsInRpZW5lX3Byb2R1Y3RvX2J1cnNhdGlsIjoiVHJ1ZSIsInRpZW5lX3Byb2R1Y3RvX2FwaSI6IlRydWUiLCJ0aWVuZV9UeUMiOiJUcnVlIiwibmJmIjoxNzMwNjY3ODE2LCJleHAiOjE3MzA2Njg3MTYsImlhdCI6MTczMDY2NzgxNiwiaXNzIjoiSU9MT2F1dGhTZXJ2ZXIiLCJhdWQiOiJJT0xPYXV0aFNlcnZlciJ9.A-xbqYIhV8wWb72yxMWMSYct7Ax3aExx8Fxykx-JMko8x71kBvOKzXWp0jpP4J7jpcj28PNYtAfEdsBmUSpCV0M9pa42AvVfjcRmuZRy3wH65c5G_qP9IBE34pjLqsVhIzCp0NcSPZI0LC5dxEGLczNLdqWeb3Zsnrmw-YvY_XRQSU4kYoYcse5KncLbw79vCRYcmI-AZpItCQ9K7L8oytfRoCwTKxfnb5PHWZyDZgyBcc9Loxw1xriQOJWWBGBc7GISTyRm5EfKH6QI9mUDheS3bQVK0jNGcMLT_h-1CR9UczhuYOZGCJ34JRWnaCajR4fjRnofzlAyjkc8eZ_e_Q'  # Reemplaza 'YOUR_API_TOKEN' con tu token de autorización
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
    mercado = 'bCBA'
    simbolo = os.getenv('SIMBOLO')
    fecha_desde = os.getenv('FECHA_DESDE')
    fecha_hasta = os.getenv('FECHA_HASTA')

    precios = obtener_precio_diario(mercado, simbolo, fecha_desde, fecha_hasta)

    if precios:
        graficar_precios(precios)

if __name__ == "__main__":
    main()
