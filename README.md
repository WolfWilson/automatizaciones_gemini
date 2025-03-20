# 📩 Automatización de Correos con Gemini - INSSSEP  

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Google Gemini](https://img.shields.io/badge/Google-Gemini%202.0-ffca28?style=for-the-badge&logo=google)
![Exchangelib](https://img.shields.io/badge/Outlook-Exchangelib-blue?style=for-the-badge&logo=microsoftoutlook)
![Natural Language Processing](https://img.shields.io/badge/NLP-Processing-green?style=for-the-badge&logo=deepmind)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Enabled-orange?style=for-the-badge&logo=pytorch)
![Windows](https://img.shields.io/badge/OS-Windows-lightgrey?style=for-the-badge&logo=windows)
![Status](https://img.shields.io/badge/Estado-En%20Desarrollo-orange?style=for-the-badge)

📢 **Automatización Inteligente de Correos para el INSSSEP**  
Este sistema monitorea en **tiempo real** los correos entrantes de Outlook, los **categorizando con IA**, generando **respuestas automatizadas** y **acciones recomendadas** basadas en reglas predefinidas.  

---

## 🚀 **Características del Proyecto**
✔ **Lectura en Tiempo Real**: Detecta nuevos correos entrantes sin procesar.  
✔ **Clasificación Inteligente** con **Google Gemini 2.0**.  
✔ **Generación de Respuestas**: Usa **lenguaje natural** basado en una **guía de respuesta dinámica**.  
✔ **Registro de Acciones**: Sugiere pasos a seguir según la categoría detectada.  
✔ **No Requiere Intervención Humana**: Puede ejecutarse en segundo plano indefinidamente.  
✔ **Registros de Actividad** en archivos **log_respuestas.txt** y **log_acciones.txt**.  

---

## 🔧 **Tecnologías Utilizadas**
- ![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python) **Python 3.12**
- ![Google Gemini](https://img.shields.io/badge/Gemini-2.0-red?style=flat-square&logo=google) **Google Gemini AI** (Clasificación y respuestas)
- ![NLP](https://img.shields.io/badge/NLP-Processing-green?style=flat-square&logo=deepmind) **Procesamiento de Lenguaje Natural (NLP)**
- ![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Enabled-orange?style=flat-square&logo=pytorch) **Machine Learning**
- ![Exchangelib](https://img.shields.io/badge/Exchangelib-Outlook-blue?style=flat-square&logo=microsoftoutlook) **Exchangelib** (Conexión con Outlook)
- **pytz** (Manejo de zonas horarias)
- **dotenv** (Carga de variables de entorno)

---

## 📦 **Instalación y Uso**
### 1️⃣ **Clonar el repositorio**
```sh
git clone https://github.com/tu_usuario/abm_numeros_confianza.git
cd abm_numeros_confianza
```

###  2️⃣ **Crear y activar un entorno virtual**

```sh
python -m venv venv
```

###  3️⃣ **Instalar dependencias**

```sh
pip install -r requirements.txt

```
###4️⃣ **Ejecutar la aplicación**
```sh
python main.py

```

## 📂 Estructura del Proyecto
```sh

📂 automatizacion_gemini/
│
├── 📂 Modules/                # Módulos principales del sistema
│   ├── conexion.py            # Conexión con Outlook
│   ├── categorizar.py         # Clasificación con IA
│   ├── guia_cat_rep.py        # Guía de respuestas y acciones
│
├── 📂 logs/                   # Carpeta de logs generados
│   ├── log_respuestas.txt     # Registro de respuestas generadas
│   ├── log_acciones.txt       # Registro de acciones recomendadas
│
├── .gitignore                 # Ignorar archivos innecesarios en Git
├── README.md                  # Documentación del proyecto
├── requirements.txt           # Dependencias del proyecto
├── outlook_reader_realtime.py  # Script principal que ejecuta el bot en tiempo real
│
└── venv/                      # Entorno virtual de Python (no incluido en Git)


```
## 🔄 Flujo de Trabajo del Bot

1️⃣ Detecta un nuevo correo en Outlook.
2️⃣ Clasifica el correo con Google Gemini.
3️⃣ Consulta la guía de respuestas para determinar qué hacer.
4️⃣ Genera un mensaje humano basado en la guía, sin citarla textualmente.
5️⃣ Guarda la respuesta y la acción en logs, sin enviar correos aún.
6️⃣ Continúa ejecutándose en un bucle esperando más correos.

## 📄 Ejemplo de Registro en Log
### 📂 log_respuestas.txt

```yaml
CorreoID: A23JK9X
Asunto: Problema con mi cuenta
Categoría: Soporte
Respuesta:
Hola, gracias por contactarnos. Hemos recibido su solicitud y la estamos analizando.
Un representante se comunicará con usted pronto.
FechaRegistro: 2025-03-20T14:30:00
---
```
### 📂 log_acciones.txt
```yaml
CorreoID: A23JK9X
Asunto: Problema con mi cuenta
Categoría: Soporte
Accion: Abrir ticket de soporte en el sistema interno.
FechaRegistro: 2025-03-20T14:30:00
---

```


## 🚧 Funcionalidades en Desarrollo 
🔜 Enviar Respuestas Automáticas por Correo con Exchangelib.  
🔜 Integración con Sistemas de Ticketing (Jira, OTRS, etc.).  
🔜 Dashboard para Monitoreo de Correos Procesados.  