# Modules/categorizar.py

import google.generativeai as genai

def limpiar_texto_ia(asunto, cuerpo):
    """
    Remueve la línea 'Cuidado: Este correo electronico se originó fuera'
    u otras frases no deseadas en el prompt.
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


def ia_clasificar(asunto_limpio, cuerpo_limpio):
    """
    Llama a la IA (Gemini) para obtener una de las categorías definidas,
    con la regla prioritaria: 'cualquier pregunta sobre estado de un trámite => consulta/seguimiento'.
    Además, incluye la nueva categoría 'oficios/judiciales'.
    """
    prompt = f"""
Eres un clasificador de correos para Jubilaciones del INSSSEP. 
Debes devolver siempre UNA de estas categorías (en minúsculas):
- 'supervivencias'
- 'consulta/seguimiento'
- 'documentos/remesas'
- 'trámites/documentación'
- 'solicitud'
- 'soporte'
- 'oficios/judiciales'
- 'otro'

Regla prioritaria:
1) Cualquier mensaje que pida información sobre estado de un trámite, expediente, pago de zona, reclamo, etc., se clasifica como 'consulta/seguimiento'.
2) Cualquier mensaje relativo a oficios judiciales (enviar/diligenciar oficios) => 'oficios/judiciales'.

Algunos ejemplos:
1) "Tengo problemas para acceder al sistema" => 'soporte'
2) "Certificado de supervivencia" => 'supervivencias'
3) "Deseo saber el estado de mi trámite" => 'consulta/seguimiento'
4) "Adjunto remesa" => 'documentos/remesas'
5) "Actualizar datos en mi expediente" => 'trámites/documentación'
6) "Solicito algo general" => 'solicitud'
7) "Oficios judiciales" => 'oficios/judiciales'
8) "Algo que no encaja con lo anterior" => 'otro'

Analiza este correo:
Asunto: {asunto_limpio}
Cuerpo: {cuerpo_limpio}

Devuelve solo la categoría en minúsculas.
"""
    try:
        modelo = genai.GenerativeModel("gemini-2.0-flash")
        resp = modelo.generate_content(prompt)
        cat = resp.text.strip().lower()

        # Asegurar que sea una de las 8
        categorias_validas = {
            "supervivencias", "consulta/seguimiento", "documentos/remesas",
            "trámites/documentación", "solicitud", "soporte", "oficios/judiciales",
            "otro"
        }
        if cat not in categorias_validas:
            cat = "otro"

        return cat
    except Exception as e:
        print("Error IA al clasificar:", e)
        return "otro"


def postprocesar_categoria(categoria, asunto, cuerpo):
    """
    REGLA FORZADA:
    - Si detectamos palabras clave de expedientes => 'consulta/seguimiento'.
    - Si detectamos oficios judiciales => 'oficios/judiciales'.
    """
    texto = (asunto + " " + cuerpo).lower()

    # Triggers para consulta/seguimiento (expediente, ley 6039, contrato de obra, reclamo, etc.)
    triggers_consulta = ["expediente", "ley 6039", "contrato de obra", "pago de zona", "reclamo"]
    for t in triggers_consulta:
        if t in texto:
            return "consulta/seguimiento"

    # Triggers para oficios judiciales
    triggers_oficios = ["oficio judicial", "oficios judiciales", "diligenciar oficio", "correo oficios"]
    for t in triggers_oficios:
        if t in texto:
            return "oficios/judiciales"

    return categoria


def categorizar_correo(asunto, cuerpo):
    # 1) Limpieza
    asunto_limpio, cuerpo_limpio = limpiar_texto_ia(asunto, cuerpo)

    # 2) IA
    cat_ia = ia_clasificar(asunto_limpio, cuerpo_limpio)

    # 3) Reglas finales
    cat_final = postprocesar_categoria(cat_ia, asunto, cuerpo)

    return cat_final
