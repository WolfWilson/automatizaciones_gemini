import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

def categorizar_correo(asunto, cuerpo):
    """
    Utiliza un modelo generativo (p.ej. Google Gemini) para
    sugerir una categoría basada en el asunto y el cuerpo del correo.
    """
    prompt = f"""
    Analiza el siguiente correo y sugiere una categoría general (por ejemplo: 'soporte', 'factura', 'marketing', etc.):
    Asunto: {asunto}
    Cuerpo: {cuerpo}

    Devuelve únicamente la categoría.
    """

    try:
        # Usa GenerativeModel con 'gemini-2.0-flash'
        # (Si no tienes acceso, prueba "text-bison-001" o "chat-bison-001")
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Este es el método correcto en las nuevas versiones:
        response = model.generate_content(prompt)

        # Extrae el texto
        category = response.text.strip()
    except Exception as e:
        print("Error al categorizar con IA:", e)
        category = "ErrorIA"

    # Registrar la categoría en un log
    with open("log_reg_categorias.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"Asunto: {asunto} | Categoría: {category}\n")

    return category
