# outlook_reader.py

from Modules.conexion import conectar_outlook
from Modules.categorizar import categorizar_correo
from exchangelib import Message

def leer_correos_no_leidos(max_correos=10):
    """
    Conecta a la cuenta de Outlook y devuelve
    los correos no leídos más recientes.
    """
    cuenta = conectar_outlook()
    bandeja_entrada = cuenta.inbox.filter(is_read=False).order_by('-datetime_received')[:max_correos]

    correos = []
    for email in bandeja_entrada:
        correos.append({
            "remitente": email.sender.email_address if email.sender else "",
            "asunto": email.subject or "",
            "cuerpo": email.text_body or "",
            "id": email.id
        })
    return correos

def main():
    correos = leer_correos_no_leidos()
    if not correos:
        print("No hay correos nuevos.")
        return

    for correo in correos:
        asunto = correo["asunto"]
        cuerpo = correo["cuerpo"]

        print(f"Correo recibido de {correo['remitente']} - Asunto: {asunto}")

        # Categorización con IA
        categoria = categorizar_correo(asunto, cuerpo)
        print(f"  -> Categoría asignada: {categoria}")

        # Aquí podrías llamar a otros módulos, por ejemplo:
        #   acciones.realizar_accion(categoria, correo)
        #   respuestas.responder(categoria, correo)
        # según la lógica que vayas implementando más adelante.

if __name__ == "__main__":
    main()
