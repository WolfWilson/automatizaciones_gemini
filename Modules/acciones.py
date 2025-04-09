# Modules/acciones.py
import re
from exchangelib import Message, Mailbox
from Modules.conexion_db import buscar_por_dni


#:::::::::::::::::::::::: SECCION PARA TRATAR SUPERVIVENCIAS :::::::::::::::::::::::::::::
def reenviar_supervivencia_a_analisis(email):
    """
    Reenvía el correo original a abouvier@insssep.gov.ar con asunto, body y destinatarios.
    Este método ya envía el correo directamente y devuelve True o lanza error.
    """
    success = email.forward(
        subject=f"FW: {email.subject or '(Sin asunto)'}",
        body=(
            "Estimado/a, se reenvía este correo con documentación de supervivencia "
            "para su verificación. En caso de que la supervivencia no cumpla los estándares, "
            "por favor responda con las correcciones correspondientes."
        ),
        to_recipients=["abouvier@insssep.gov.ar"]
    )
    if success:
        print("Correo reenviado exitosamente a abouvier@insssep.gov.ar")


#:::::::::::::::::::::: SECCION PARA TRATAR CONSULTAS  ::::::::::::::::::::::::::::

# Modules/acciones.py
import re
from exchangelib import Message, Mailbox

from Modules.conexion_db import buscar_por_dni

def limpiar_texto_cuerpo_al_reenviar(texto):
    """
    Borra la advertencia 'Cuidado: Este correo...' antes de reenviar.
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
    Busca un entero (6 a 10 dígitos) que sea el DNI.
    """
    patron = r"\b(\d{6,10})\b"
    match = re.search(patron, texto)
    if match:
        return int(match.group(1))
    return None

def consultar_estado_expediente(cuerpo):
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

    # datos es una lista de dict
    return datos[0]  # Tomamos la primera fila

def armar_fragmento_informacion(datos_sp):
    """
    Convierte los datos del SP en un pequeño texto
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

def enviar_aviso_reclamo(cuenta, asunto_original, cuerpo_correo, datos_sp):
    """
    Envía correo a abouvier y cgianneschi con un resumen
    """
    # Limpiar la advertencia en el cuerpo
    cuerpo_limpio = limpiar_texto_cuerpo_al_reenviar(cuerpo_correo)
    fragmento = armar_fragmento_informacion(datos_sp)

    aviso = Message(
        account=cuenta,
        subject=f"Aviso de reclamo por estado de expediente: {asunto_original}",
        to_recipients=[
            Mailbox(email_address="abouvier@insssep.gov.ar"),
            Mailbox(email_address="cgianneschi@insssep.gov.ar"),
            Mailbox(email_address="mpividori@insssep.gov.ar")
        ],
        body=(
            f"Se recibió una consulta/reclamo sobre estado de expediente.\n"
            f"Asunto original: {asunto_original}\n\n"
            f"Cuerpo del correo (limpio):\n{cuerpo_limpio}\n\n"
            f"{fragmento}"
            "Por favor, tomar las acciones correspondientes.\n"
        )
    )
    aviso.send()
    print("Correo de aviso de reclamo enviado a abouvier + cgianneschi.")

def procesar_consulta_reclamo(cuenta, asunto, cuerpo):
    """
    Llama SP para traer datos (si hay DNI),
    envía correo a abouvier + cgianneschi,
    retorna un texto con info adicional para la respuesta IA.
    """
    datos_sp = consultar_estado_expediente(cuerpo)
    enviar_aviso_reclamo(cuenta, asunto, cuerpo, datos_sp)
    return armar_fragmento_informacion(datos_sp)

def reenviar_supervivencia_a_analisis(email):
    """
    Reenvía el correo a abouvier con una leyenda propia.
    Versión actual de exchangelib => forward() 
    requiere subject, body, to_recipients y 
    ya envía el correo (devuelve bool).
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
        print(f"Correo reenviado exitosamente a abouvier@insssep.gov.ar")    
