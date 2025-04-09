# outlook_reader_jubilaciones_test.py
import os
from datetime import datetime
import pytz
from hashlib import sha1
from dateutil.relativedelta import relativedelta

from exchangelib import EWSDateTime, FileAttachment

from Modules.conexion import conectar_outlook
from Modules.categorizar import categorizar_correo
from Modules.guia_cat_rep import guia_cat_rep, accion_por_defecto, guia_por_defecto
from Modules.config_respuesta import FIRMA, CONTEXTO_BASE
from Modules.acciones import (
    reenviar_supervivencia_a_analisis,
    procesar_consulta_reclamo
)

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

# Meses en español
MESES_ES = {
    "January": "enero", "February": "febrero", "March": "marzo",
    "April": "abril", "May": "mayo", "June": "junio",
    "July": "julio", "August": "agosto", "September": "septiembre",
    "October": "octubre", "November": "noviembre", "December": "diciembre"
}

def limpiar_texto_cuerpo(texto):
    """
    Versión genérica para limpieza 
    si deseas filtrar la advertencia en este script también.
    """
    advertencia = "Cuidado: Este correo electronico se originó fuera"
    lineas = texto.split('\n')
    filtradas = []
    for linea in lineas:
        if advertencia.lower() in linea.lower():
            continue
        filtradas.append(linea)
    return "\n".join(filtradas)

def generar_respuesta_humana(categoria, asunto, cuerpo, fecha_python, info_extra=""):
    categoria_lower = categoria.lower().strip()

    # localizamos la acción y guía
    if categoria_lower in guia_cat_rep:
        accion_sugerida = guia_cat_rep[categoria_lower]["accion"]
        guia_texto = guia_cat_rep[categoria_lower]["guia"]
    else:
        accion_sugerida = accion_por_defecto
        guia_texto = guia_por_defecto

    # Supervivencia => fecha +3 meses
    instruccion_supervivencia = ""
    if categoria_lower == "supervivencias":
        proxima_fecha = fecha_python + relativedelta(months=3)
        mes_en = proxima_fecha.strftime("%B")
        mes_es = MESES_ES.get(mes_en, mes_en).lower()
        anio = proxima_fecha.year
        instruccion_supervivencia = (
            f"\nAdemás, recuerda mencionar que la próxima presentación "
            f"deberá realizarse en el mes de {mes_es} de {anio}.\n"
        )

    cuerpo_limpio = limpiar_texto_cuerpo(cuerpo)

    prompt = f"""
{CONTEXTO_BASE}

Asunto del correo: {asunto}
Contenido recibido (limpio): {cuerpo_limpio}

Este mensaje ha sido clasificado como: {categoria}.
Guía interna para la respuesta (no citar literalmente): {guia_texto}

{instruccion_supervivencia}

Información adicional (si existe):
{info_extra}

Instrucciones importantes:
- No utilices el nombre del remitente ni lo inventes.
- Usa un saludo general como 'Estimado/a'.
- Mantén un tono formal, cordial y claro, siempre en español.
- Cierra siempre con la siguiente firma:

{FIRMA}

Redacta solo la respuesta completa como si fuera a enviarse por correo.
"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return accion_sugerida, response.text.strip()
    except Exception as e:
        print(f"Error IA: {e}")
        return accion_sugerida, "No se pudo generar respuesta."


def obtener_carpeta_jubilaciones(cuenta):
    for carpeta in cuenta.root.walk():
        if carpeta.name.lower() == "jubilaciones":
            return carpeta
    return None

def generar_hash_correo(email):
    asunto = email.subject or ""
    remitente = email.sender.email_address if email.sender else ""
    fecha = email.datetime_received.strftime("%Y%m%d%H%M")
    texto = f"{asunto}{remitente}{fecha}"
    return sha1(texto.encode('utf-8')).hexdigest()

def ews_to_python_datetime(ews_dt):
    from datetime import datetime
    import pytz
    dt = datetime(
        ews_dt.year,
        ews_dt.month,
        ews_dt.day,
        ews_dt.hour,
        ews_dt.minute,
        ews_dt.second,
        ews_dt.microsecond
    )
    tz = pytz.timezone("America/Argentina/Buenos_Aires")
    dt_local = tz.localize(dt)
    dt_naive = dt_local.replace(tzinfo=None)
    return dt_naive

def es_supervivencia_manual(asunto, cuerpo, email):
    texto = (asunto + " " + cuerpo).lower()
    return "supervivencia" in texto and bool(email.attachments)

def main():
    cuenta = conectar_outlook()
    carpeta = obtener_carpeta_jubilaciones(cuenta)
    if not carpeta:
        print("❌ Carpeta 'Jubilaciones' no encontrada en Outlook.")
        return

    # Lee los 5 últimos correos
    qs = carpeta.all().order_by('-datetime_received')[:5]
    procesados = set()

    for email in qs:
        hash_correo = generar_hash_correo(email)
        if hash_correo in procesados:
            continue
        procesados.add(hash_correo)

        asunto = email.subject or "(Sin asunto)"
        cuerpo = email.text_body or "(Sin contenido)"
        remitente = email.sender.email_address if email.sender else "(Desconocido)"
        fecha_python = ews_to_python_datetime(email.datetime_received)

        print("\n--------------------------------------------------------")
        print(f"De: {remitente}")
        print(f"Asunto: {asunto}")

        # 1) Determinar categoría
        from Modules.categorizar import categorizar_correo
        if es_supervivencia_manual(asunto, cuerpo, email):
            categoria = "supervivencias"
        else:
            categoria = categorizar_correo(asunto, cuerpo)

        print(f"Categoría detectada: {categoria}")

        # 2) Lógica de reclamo => "consulta/seguimiento"
        info_extra = ""
        if categoria.lower() in ["consulta/seguimiento"]:
            from Modules.acciones import procesar_consulta_reclamo
            info_extra = procesar_consulta_reclamo(cuenta, asunto, cuerpo)

        # 3) Generar la respuesta IA (para log, etc.)
        accion, respuesta = generar_respuesta_humana(
            categoria, asunto, cuerpo, fecha_python, info_extra
        )
        print(f"Acción sugerida: {accion}")
        print(f"Respuesta generada:\n{respuesta}")

        # 4) Si es 'supervivencias', reenvío a abouvier
        if categoria.lower() == "supervivencias":
            from Modules.acciones import reenviar_supervivencia_a_analisis
            reenviar_supervivencia_a_analisis(email)

if __name__ == "__main__":
    main()
