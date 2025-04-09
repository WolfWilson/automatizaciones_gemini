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

def generar_respuesta_humana(categoria, asunto, cuerpo):
    categoria_lower = categoria.lower().strip()
    if categoria_lower in guia_cat_rep:
        accion_sugerida = guia_cat_rep[categoria_lower]["accion"]
        guia_texto = guia_cat_rep[categoria_lower]["guia"]
    else:
        accion_sugerida = accion_por_defecto
        guia_texto = guia_por_defecto

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
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return accion_sugerida, response.text.strip()
    except Exception as e:
        print(f"Error al generar respuesta IA: {e}")
        return accion_sugerida, "Lo sentimos, no pudimos generar la respuesta en este momento."

def obtener_carpeta_jubilaciones(cuenta):
    for carpeta in cuenta.root.walk():
        if carpeta.name.lower() == "jubilaciones":
            return carpeta
    return None

def ejecutar_en_tiempo_real(intervalo_seg=60):
    print(f"📬 Bot iniciado. Revisando carpeta 'Jubilaciones' cada {intervalo_seg} segundos...")

    tz = pytz.timezone("America/Argentina/Buenos_Aires")
    last_check_time = datetime.now(tz) - timedelta(minutes=1)
    last_check_time_ews = EWSDateTime.from_datetime(last_check_time)

    correos_procesados = set()

    while True:
        try:
            cuenta = conectar_outlook()
            carpeta = obtener_carpeta_jubilaciones(cuenta)

            if not carpeta:
                print("❌ No se encontró la carpeta 'Jubilaciones'.")
                time.sleep(intervalo_seg)
                continue

            qs = (
                carpeta
                .filter(datetime_received__gte=last_check_time_ews)
                .order_by('datetime_received')
                .all()
            )

            correos_nuevos = list(qs)
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Encontrados {len(correos_nuevos)} nuevos correos.")

            for email in correos_nuevos:
                if email.id in correos_procesados:
                    continue

                asunto = email.subject or "(Sin asunto)"
                cuerpo = email.text_body or "(Sin contenido)"
                remitente = email.sender.email_address if email.sender else "(Desconocido)"
                correo_id = email.id

                print("--------------------------------------------------------")
                print(f"De: {remitente}")
                print(f"Asunto: {asunto}")

                categoria = categorizar_correo(asunto, cuerpo)
                print(f"  -> Categoría detectada: {categoria}")

                accion, respuesta = generar_respuesta_humana(categoria, asunto, cuerpo)
                print(f"  -> Acción sugerida: {accion}")
                print(f"  -> Respuesta generada:\n{respuesta}")

                with open("log_respuestas.txt", "a", encoding="utf-8") as log_resp:
                    log_resp.write(
                        f"CorreoID: {correo_id}\n"
                        f"Remitente: {remitente}\n"
                        f"Asunto: {asunto}\n"
                        f"Categoría: {categoria}\n"
                        f"Respuesta:\n{respuesta}\n"
                        f"FechaRegistro: {datetime.now().isoformat()}\n"
                        f"---\n"
                    )

                with open("log_acciones.txt", "a", encoding="utf-8") as log_acc:
                    log_acc.write(
                        f"CorreoID: {correo_id}\n"
                        f"Remitente: {remitente}\n"
                        f"Asunto: {asunto}\n"
                        f"Categoría: {categoria}\n"
                        f"Accion: {accion}\n"
                        f"FechaRegistro: {datetime.now().isoformat()}\n"
                        f"---\n"
                    )

                correos_procesados.add(email.id)

                if email.datetime_received > last_check_time_ews:
                    last_check_time_ews = email.datetime_received

            print(f"⏳ Esperando {intervalo_seg} segundos para la próxima revisión...\n")
            time.sleep(intervalo_seg)

        except Exception as e:
            print(f"🛑 ERROR GENERAL: {e}")
            print(f"Esperando {intervalo_seg} segundos antes de reintentar...\n")
            time.sleep(intervalo_seg)

def main():
    ejecutar_en_tiempo_real(intervalo_seg=60)

if __name__ == "__main__":
    main()
