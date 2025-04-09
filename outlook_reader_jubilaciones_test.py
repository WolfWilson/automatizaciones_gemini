from datetime import datetime
import pytz
from hashlib import sha1
from dateutil.relativedelta import relativedelta

from exchangelib import EWSDateTime

from Modules.conexion import conectar_outlook
from Modules.categorizar import categorizar_correo
from Modules.guia_cat_rep import guia_cat_rep, accion_por_defecto, guia_por_defecto
from Modules.config_respuesta import FIRMA, CONTEXTO_BASE

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

def limpiar_texto_cuerpo(texto):
    """
    Elimina líneas automáticas. Ajusta si detectas más frases.
    """
    lineas = texto.split('\n')
    filtradas = []
    for linea in lineas:
        l = linea.strip().lower()
        if 'cuidado: este correo electronico se originó fuera' in l:
            continue
        filtradas.append(linea)
    return '\n'.join(filtradas)

def generar_respuesta_humana(categoria, asunto, cuerpo, fecha_python):
    """
    Crea un prompt detallado para la IA.
    fecha_python es un objeto datetime de Python (no EWSDateTime).
    """
    categoria_lower = categoria.lower().strip()
    if categoria_lower in guia_cat_rep:
        accion_sugerida = guia_cat_rep[categoria_lower]["accion"]
        guia_texto = guia_cat_rep[categoria_lower]["guia"]
    else:
        accion_sugerida = accion_por_defecto
        guia_texto = guia_por_defecto

    # Para supervivencias, sumar 3 meses.
    instruccion_supervivencia = ""
    if categoria_lower == "supervivencias":
        proxima_fecha = fecha_python + relativedelta(months=3)
        mes = proxima_fecha.strftime("%B").capitalize()
        anio = proxima_fecha.year
        instruccion_supervivencia = (
            f"\nAdemás, recuerda mencionar que la próxima presentación deberá realizarse "
            f"en el mes de {mes} de {anio} (3 meses desde la fecha de recepción).\n"
        )

    cuerpo_limpio = limpiar_texto_cuerpo(cuerpo)

    prompt = f"""
{CONTEXTO_BASE}

Asunto del correo: {asunto}
Contenido recibido (limpio): {cuerpo_limpio}

Este mensaje ha sido clasificado como: {categoria}.
Guía interna para la respuesta (no citar literalmente): {guia_texto}

{instruccion_supervivencia}

Instrucciones importantes:
- No utilices el nombre del remitente ni lo inventes.
- Usa un saludo general como 'Estimado/a'.
- Mantén un tono formal, cordial y claro.
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
    """
    Busca la carpeta 'Jubilaciones' en la raíz del buzón.
    """
    for carpeta in cuenta.root.walk():
        if carpeta.name.lower() == "jubilaciones":
            return carpeta
    return None

def generar_hash_correo(email):
    asunto = email.subject or ""
    remitente = email.sender.email_address if email.sender else ""
    # Minuto
    fecha = email.datetime_received.strftime("%Y%m%d%H%M")
    texto = f"{asunto}{remitente}{fecha}"
    return sha1(texto.encode('utf-8')).hexdigest()

def es_supervivencia_manual(asunto, cuerpo, email):
    """
    Detección previa: si contiene 'supervivencia' y hay adjuntos => 'supervivencias'.
    """
    texto = (asunto + " " + cuerpo).lower()
    return "supervivencia" in texto and bool(email.attachments)

def ews_to_python_datetime(ews_dt):
    """
    Convierte un EWSDateTime en datetime nativo de Python.
    1) Creamos un datetime manualmente con año, mes, etc.
    2) Ajustamos zona horaria a América/Argentina/Buenos_Aires
    3) Quitamos tzinfo si queremos un naive datetime.
    """
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
    dt_local = tz.localize(dt)  # dt con la tz
    # dt sin zona horaria, si deseas manipular con relativedelta sin tz:
    dt_naive = dt_local.replace(tzinfo=None)
    return dt_naive

def main():
    cuenta = conectar_outlook()
    carpeta = obtener_carpeta_jubilaciones(cuenta)
    if not carpeta:
        print("❌ Carpeta 'Jubilaciones' no encontrada.")
        return

    # Últimos 5 correos
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

        # Convertir EWSDateTime => datetime de Python
        fecha_python = ews_to_python_datetime(email.datetime_received)

        print("\n--------------------------------------------------------")
        print(f"De: {remitente}")
        print(f"Asunto: {asunto}")

        # Detección previa vs IA
        if es_supervivencia_manual(asunto, cuerpo, email):
            categoria = "supervivencias"
        else:
            categoria = categorizar_correo(asunto, cuerpo)

        print(f"Categoría detectada: {categoria}")

        accion, respuesta = generar_respuesta_humana(categoria, asunto, cuerpo, fecha_python)
        print(f"Acción sugerida: {accion}")
        print(f"Respuesta generada:\n{respuesta}")

if __name__ == "__main__":
    main()
