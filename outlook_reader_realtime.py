import time
from datetime import datetime, timedelta
import pytz
from exchangelib import DELEGATE, EWSDateTime

from Modules.conexion import conectar_outlook
from Modules.categorizar import categorizar_correo
from Modules.guia_cat_rep import guia_cat_rep, accion_por_defecto, guia_por_defecto

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

# -----------------------------------------------------------------------------------
# Función para generar respuesta "humana" usando la guía según la categoría detectada
# -----------------------------------------------------------------------------------
def generar_respuesta_humana(categoria, asunto, cuerpo):
    """
    Toma la 'categoría' que dio la IA, busca en 'guia_cat_rep' la acción y la guía,
    y llama a Gemini para obtener un texto más natural y humano,
    sin citar textualmente la guía.
    """
    categoria_lower = categoria.lower().strip()
    if categoria_lower in guia_cat_rep:
        accion_sugerida = guia_cat_rep[categoria_lower]["accion"]
        guia_texto = guia_cat_rep[categoria_lower]["guia"]
    else:
        accion_sugerida = accion_por_defecto
        guia_texto = guia_por_defecto

    # Creamos un prompt para que la IA elabore una respuesta acorde a la guía
    prompt = f"""
El usuario envió un correo con:
Asunto: {asunto}
Contenido: {cuerpo}

Se ha clasificado el correo en la categoría: {categoria}.
Tienes la siguiente guía interna para responder, pero NO la cites textualmente. 
Guía: {guia_texto}

Genera una respuesta:
- Usa un lenguaje amigable y profesional.
- Sé conciso.
- No cites la guía literalmente, pero sigue sus recomendaciones.
    """

    try:
        # Ajusta el modelo, por ejemplo "gemini-2.0-flash"
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        respuesta_humana = response.text.strip()
    except Exception as e:
        print(f"Error al generar respuesta IA: {e}")
        respuesta_humana = "Lo sentimos, no pudimos generar la respuesta en este momento."

    return accion_sugerida, respuesta_humana

# -----------------------------------------------------------------------------------
# Bucle principal: escucha en "tiempo real" y procesa solo correos nuevos
# -----------------------------------------------------------------------------------
def ejecutar_en_tiempo_real(intervalo_seg=60):
    """
    Revisa la bandeja cada 'intervalo_seg' segundos para ver si hay correos NUEVOS
    (es decir, con fecha posterior a last_check_time).
    Clasifica y genera una respuesta en base a la guía externa.
    """
    print(f"Bot iniciado. Revisando cada {intervalo_seg} segundos...")

    # Usamos zona horaria local. Ajusta si requieres
    tz = pytz.timezone("America/Argentina/Buenos_Aires")

    # Al iniciar, consideramos los próximos correos (por ejemplo, 1 min atrás).
    # Para evitar procesar lo que ya está en la bandeja.
    last_check_time = datetime.now(tz) - timedelta(minutes=1)
    last_check_time_ews = EWSDateTime.from_datetime(last_check_time)

    # Para no procesar el mismo correo dos veces
    correos_procesados = set()

    while True:
        try:
            cuenta = conectar_outlook()

            # Filtramos correos con fecha >= last_check_time_ews
            qs = (
                cuenta.inbox
                .filter(datetime_received__gte=last_check_time_ews)
                .order_by('datetime_received')  # más antiguos primero
                .all()
            )
            correos_nuevos = list(qs)
            if correos_nuevos:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Encontrados {len(correos_nuevos)} nuevos correos.")
            else:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sin correos nuevos.")

            for email in correos_nuevos:
                # Verifica si ya lo procesamos
                if email.id in correos_procesados:
                    continue

                asunto = email.subject or "(Sin asunto)"
                cuerpo = email.text_body or "(Sin contenido)"
                remitente = email.sender.email_address if email.sender else "(Desconocido)"
                correo_id = email.id

                print("--------------------------------------------------------")
                print(f"De: {remitente}")
                print(f"Asunto: {asunto}")

                # 1) Categorizar con IA
                categoria = categorizar_correo(asunto, cuerpo)
                print(f"  -> Categoría detectada: {categoria}")

                # 2) Generar respuesta "humana" según la guía
                accion_sugerida, respuesta_humana = generar_respuesta_humana(categoria, asunto, cuerpo)
                print(f"  -> Acción sugerida: {accion_sugerida}")
                print(f"  -> Respuesta generada:\n{respuesta_humana}")

                # 3) Guardar en logs
                with open("log_respuestas.txt", "a", encoding="utf-8") as log_resp:
                    log_resp.write(
                        f"CorreoID: {correo_id}\n"
                        f"Asunto: {asunto}\n"
                        f"Categoría: {categoria}\n"
                        f"Respuesta:\n{respuesta_humana}\n"
                        f"FechaRegistro: {datetime.now().isoformat()}\n"
                        f"---\n"
                    )
                with open("log_acciones.txt", "a", encoding="utf-8") as log_acc:
                    log_acc.write(
                        f"CorreoID: {correo_id}\n"
                        f"Asunto: {asunto}\n"
                        f"Categoría: {categoria}\n"
                        f"Accion: {accion_sugerida}\n"
                        f"FechaRegistro: {datetime.now().isoformat()}\n"
                        f"---\n"
                    )

                # Marcar como procesado
                correos_procesados.add(email.id)

                # Actualizar last_check_time si este correo es más reciente
                if email.datetime_received > last_check_time_ews:
                    last_check_time_ews = email.datetime_received

            # Esperar antes de la próxima revisión
            print(f"Esperando {intervalo_seg} segundos para la próxima revisión...")
            time.sleep(intervalo_seg)

        except Exception as e:
            print(f"ERROR GENERAL: {e}")
            print(f"Esperando {intervalo_seg} segundos antes de reintentar...")
            time.sleep(intervalo_seg)

def main():
    ejecutar_en_tiempo_real(intervalo_seg=60)

if __name__ == "__main__":
    main()
