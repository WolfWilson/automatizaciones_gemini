# Modules/acciones.py

import re
from exchangelib import Message, Mailbox
from Modules.conexion_db import buscar_por_dni

# -------------------------------------------------------------------
# SUPERVIVENCIAS
# -------------------------------------------------------------------
def reenviar_supervivencia_a_analisis(email):
    """
    Reenvía el correo original a abouvier@insssep.gov.ar con subject, body y destinatario.
    Versión actual => forward(...) envía y retorna bool.
    """
    success = email.forward(
        subject=f"FW: {email.subject or '(Sin asunto)'}",
        body=(
            "Se reenvía este correo con documentación de supervivencia "
            "para su verificación. Por favor, si no cumple estándares, "
            "responder con las correcciones necesarias."
        ),
        to_recipients=["abouvier@insssep.gov.ar"]
    )
    if success:
        print("Correo reenviado exitosamente a abouvier@insssep.gov.ar")


# -------------------------------------------------------------------
# CONSULTAS / RECLAMOS
# -------------------------------------------------------------------
def limpiar_texto_cuerpo_al_reenviar(texto):
    """
    Borra la advertencia antes de reenvío.
    """
    advertencia = "Cuidado: Este correo electronico se originó fuera"
    lineas = texto.split('\n')
    filtradas = []
    for linea in lineas:
        if advertencia.lower() in linea.lower():
            continue
        filtradas.append(linea)
    return "\n".join(filtradas)

def extraer_dni_de_texto(texto):
    """
    Busca un entero (6-10 dígitos) => DNI.
    """
    patron = r"\b(\d{6,10})\b"
    match = re.search(patron, texto)
    if match:
        return int(match.group(1))
    return None

def consultar_estado_expediente(cuerpo):
    """
    Extraer DNI => llamar SP => retorna dict con datos o vacío.
    """
    dni = extraer_dni_de_texto(cuerpo)
    if not dni:
        print("No se encontró DNI en el cuerpo. SP no se llamará.")
        return {}

    datos = buscar_por_dni(dni)
    if isinstance(datos, dict) and "error" in datos:
        print(f"Error al consultar SP: {datos['error']}")
        return {}
    if not datos:
        print(f"No se hallaron datos para DNI={dni}.")
        return {}

    return datos[0]  # primera fila

def armar_fragmento_informacion(datos_sp):
    """
    Genera texto con la info del SP para incrustar en la respuesta o en aviso.
    """
    if not datos_sp:
        return ""
    exp = datos_sp.get("Expediente", "")
    est = datos_sp.get("Estado", "")
    return (
        f"\nInformación del Expediente:\n"
        f" - Nº: {exp}\n"
        f" - Estado: {est}\n"
    )

def enviar_aviso_reclamo(cuenta, asunto_original, cuerpo_correo, datos_sp, respuesta_ia):
    """
    Envía un correo a abouvier y cgianneschi con el 'cuerpo_correo' limpio + 
    la respuesta generada por IA.
    """
    cuerpo_limpio = limpiar_texto_cuerpo_al_reenviar(cuerpo_correo)
    fragmento = armar_fragmento_informacion(datos_sp)

    aviso_body = (
        f"Se recibió una consulta/reclamo sobre estado de expediente.\n"
        f"Asunto original: {asunto_original}\n\n"
        f"Cuerpo del correo (limpio):\n{cuerpo_limpio}\n\n"
        f"{fragmento}"
        f"\nLa respuesta automática generada fue:\n{respuesta_ia}\n\n"
        "Por favor, tomar las acciones correspondientes.\n"
    )

    aviso = Message(
        account=cuenta,
        subject=f"Aviso de reclamo por estado de expediente: {asunto_original}",
        to_recipients=[
            Mailbox(email_address="abouvier@insssep.gov.ar"),
            Mailbox(email_address="cgianneschi@insssep.gov.ar"),
            Mailbox(email_address="mpividori@insssep.gov.ar")
        ],
        body=aviso_body
    )
    aviso.send()
    print("Correo de aviso de reclamo enviado a mpividori + abouvier + cgianneschi.")

def procesar_consulta_reclamo(cuenta, asunto, cuerpo, respuesta_ia):
    """
    1) Extrae DNI y llama SP (si hay)
    2) Envía correo de aviso a abouvier + cgianneschi, incluyendo la 'respuesta_ia'
    3) Retorna un fragmento con info SP, para insertar en la respuesta final 
       si así se desea.
    """
    datos_sp = consultar_estado_expediente(cuerpo)
    enviar_aviso_reclamo(cuenta, asunto, cuerpo, datos_sp, respuesta_ia)
    return armar_fragmento_informacion(datos_sp)
