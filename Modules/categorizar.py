# Modules/categorizar.py
import google.generativeai as genai

def limpiar_texto_ia(asunto, cuerpo):
    """
    Remueve la línea 'Cuidado: Este correo...' y 
    cualquier otra basura que no quieras en el prompt.
    """
    advertencia = "Cuidado: Este correo electronico se originó fuera"
    asunto_limpio = asunto.replace(advertencia, "").strip()
    lineas = cuerpo.split('\n')
    filtradas = []
    for linea in lineas:
        if advertencia.lower() in linea.lower():
            continue
        filtradas.append(linea)
    cuerpo_limpio = "\n".join(filtradas)
    return asunto_limpio, cuerpo_limpio

def categorizar_correo(asunto, cuerpo):
    # Limpieza previa
    asunto_limpio, cuerpo_limpio = limpiar_texto_ia(asunto, cuerpo)

    prompt = f"""
Eres un clasificador de correos para Jubilaciones del INSSSEP. 
Debes devolver siempre UNA de estas categorías (en minúsculas):
- 'supervivencias'
- 'consulta/seguimiento'
- 'documentos/remesas'
- 'trámites/documentación'
- 'solicitud'
- 'soporte'
- 'otro'

Regla prioritaria:
Cualquier mensaje que pida información sobre estado de un trámite, expediente, 
pago de zona, reclamo, etc., se clasifica como 'consulta/seguimiento'.

Algunos ejemplos:
1) "Tengo problemas para acceder al sistema" => 'soporte'
2) "Certificado de supervivencia" => 'supervivencias'
3) "Deseo saber el estado de mi trámite" => 'consulta/seguimiento'
4) "Adjunto remesa" => 'documentos/remesas'
5) "Actualizar datos en mi expediente" => 'trámites/documentación'
6) "Solicito algo general" => 'solicitud'
7) "Algo que no encaja con lo anterior" => 'otro'

Analiza este correo:
Asunto: {asunto_limpio}
Cuerpo: {cuerpo_limpio}

Devuelve solo la categoría en minúsculas.
"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        resp = model.generate_content(prompt)
        cat = resp.text.strip().lower()

        # Asegurar que sea una de las 7
        categorias_validas = {
            "supervivencias", "consulta/seguimiento", "documentos/remesas",
            "trámites/documentación", "solicitud", "soporte", "otro"
        }
        if cat not in categorias_validas:
            cat = "otro"

        return cat
    except Exception as e:
        print("Error IA al clasificar:", e)
        return "otro"
