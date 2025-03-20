# Modules/conexion.py

from exchangelib import Account, Configuration, DELEGATE, NTLM
import getpass

def conectar_outlook(server="outlook.office365.com"):
    """
    Se conecta a la cuenta de Outlook usando las credenciales
    del usuario de Windows (NTLM).
    """
    usuario_windows = getpass.getuser()
    # Ajusta el dominio de tu organización si es distinto
    email_organizacional = f"{usuario_windows}@empresa.com"

    config = Configuration(server=server, auth_type=NTLM)
    cuenta = Account(
        primary_smtp_address=email_organizacional,
        autodiscover=True,
        config=config,
        access_type=DELEGATE
    )
    return cuenta
