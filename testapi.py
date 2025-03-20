import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

if not API_KEY:
    print("ERROR: No se encontró la variable GOOGLE_GEMINI_API_KEY en el entorno.")
    exit()

# Configurar la API con la clave correcta
genai.configure(api_key=API_KEY)

def test_api():
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")  # Asegúrate de que tienes acceso a este modelo
        response = model.generate_content("Explain how AI works")

        print("Respuesta de la API:")
        print(response.text)
    except Exception as e:
        print("Error en la conexión a la API:", e)

if __name__ == "__main__":
    test_api()
