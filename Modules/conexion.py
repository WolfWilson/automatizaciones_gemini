from exchangelib import Account, Configuration, DELEGATE, NTLM, Credentials
import getpass
import os

def conectar_outlook(server="outlook.office365.com"):
    """
    Se conecta a Outlook utilizando las credenciales del usuario de Windows.
    """
    usuario_windows = getpass.getuser()  # Obtiene el usuario actual de Windows
    email_organizacional = f"{usuario_windows}@insssep.gov.ar"  # Ajusta tu dominio

    # Usa autenticación con las credenciales del usuario de Windows
    credentials = Credentials(username=usuario_windows, password=None)  # NTLM usa credenciales de Windows
    config = Configuration(server=server, credentials=credentials, auth_type=NTLM)

    cuenta = Account(
        primary_smtp_address=email_organizacional,
        autodiscover=True,
        config=config,
        access_type=DELEGATE
    )
    return cuenta
