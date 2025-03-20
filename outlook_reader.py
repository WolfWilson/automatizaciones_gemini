import time
from datetime import datetime, timedelta

import pytz  # Para manejar la zona horaria
from exchangelib import DELEGATE, EWSDateTime
from Modules.conexion import conectar_outlook
from Modules.categorizar import categorizar_correo

def leer_y_categorizar_correos(max_correos=20, dias=30):
    """
    1. Se conecta a Outlook.
    2. Toma hasta 'max_correos' correos en los últimos 'dias' días.
    3. Categorizarlos con la IA, haciendo una pausa cada 3 correos.
    """

    # Conecta a la cuenta
    cuenta = conectar_outlook()

    # Definir la zona horaria adecuada para tu región (ej. Buenos Aires)
    tz = pytz.timezone("America/Argentina/Buenos_Aires")

    # Calcular fecha de inicio (timezone-aware)
    fecha_inicio = datetime.now(tz) - timedelta(days=dias)
    fecha_inicio_ews = EWSDateTime.from_datetime(fecha_inicio)

    # Filtrar correos desde 'fecha_inicio_ews', más recientes primero, 
    # y tomar hasta 'max_correos'.
    qs = (
        cuenta.inbox
        .filter(datetime_received__gte=fecha_inicio_ews)
        .order_by('-datetime_received')
        .all()
    )

    # Convertir a lista para poder medir su length y slice
    correos_lista = list(qs)  # convertir generador a lista
    correos_lista = correos_lista[:max_correos]  # limitamos a los 'max_correos'

    if not correos_lista:
        print("No hay correos disponibles en el rango especificado.")
        return

    print(f"Encontrados {len(correos_lista)} correos. Procesando...")

    procesados = 0
    for email in correos_lista:
        asunto = email.subject or "(Sin asunto)"
        cuerpo = email.text_body or "(Sin contenido)"
        remitente = email.sender.email_address if email.sender else "(Desconocido)"

        print("\n--------------------------------------------------------")
        print(f"Correo de: {remitente}")
        print(f"Asunto: {asunto}")

        # Llamada a tu función de categorización
        categoria = categorizar_correo(asunto, cuerpo)
        print(f"Categoría sugerida: {categoria}")

        procesados += 1
        # Pausa cada 3 correos para no saturar la API
        if procesados % 3 == 0:
            print("Esperando 2 segundos para evitar saturar la API...")
            time.sleep(6)

    print(f"\nSe procesaron {procesados} correos en total.")

def main():
    leer_y_categorizar_correos(max_correos=10, dias=30)

if __name__ == "__main__":
    main()
