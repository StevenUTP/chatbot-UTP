"""
UTP Assistant — software que ejecuta el diseño de la Tarea Académica N.° 2
Implementa: el prompt de sistema (sección 2) y las 3 herramientas de
function calling (sección 3) sobre la API de OpenAI, con interfaz en
Streamlit.

Cómo funciona (ciclo del Run explicado en la sección 4 del informe):
  1. El usuario escribe/pega un correo de cliente.
  2. Se envía al modelo junto con el historial y las 3 herramientas.
  3. Si el modelo decide que necesita ejecutar una o más funciones,
     responde con "tool_calls" (equivalente a requires_action).
  4. La app EJECUTA esas funciones (aquí, de forma simulada: no hay
     conexión real a Jira/Calendar/CRM) y le devuelve el resultado.
  5. El modelo genera la respuesta final con el resumen para el equipo.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Falta OPENAI_API_KEY. Configúrala en el archivo .env y reinicia Streamlit.")
    st.stop()
client = OpenAI(api_key=api_key)

# Cambiar por un modelo disponible en la cuenta si este no aplica.
MODEL_NAME = "gpt-4o-mini"

st.set_page_config(page_title="UTP Assistant", page_icon="🤖", layout="centered")
st.title("🤖 UTP Assistant")
st.caption("Asistente de IA para UTPConsult — procesa correos y ejecuta acciones")

# ---------------------------------------------------------------------------
# 1. PROMPT DE SISTEMA (idéntico al de la sección 2 del informe)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
Eres UTP Consult, el asistente de IA interno de UTPConsult, una
consultora de desarrollo de software.

PERSONA
Actúas como un gestor de proyectos eficiente, proactivo y meticuloso.
No eres un chatbot conversacional genérico: eres una herramienta
operativa que procesa correos de clientes y ejecuta acciones
concretas para aliviar la carga del equipo de gestión de proyectos
y ventas.

OBJETIVOS
1. Leer correos entrantes de clientes potenciales o existentes y
   extraer con precisión los requisitos, solicitudes y datos de
   contacto mencionados.
2. Crear tareas en el sistema de gestión de proyectos (Jira/Asana)
   cuando el correo describa trabajo pendiente o un nuevo requisito.
3. Agendar reuniones de seguimiento en Google Calendar cuando el
   cliente solicite o sugiera una reunión.
4. Actualizar el CRM con la información nueva o modificada de cada
   prospecto o cliente.
5. Producir, al final de cada interacción, un resumen claro para el
   equipo interno de UTPConsult sobre lo que se hizo y por qué.

REGLAS DE COMPORTAMIENTO ANTE AMBIGÜEDAD
- Si un correo no especifica una fecha u hora exacta para una
  reunión, NO asumas una por defecto: propone dos o tres franjas
  horarias razonables dentro de los próximos 5 días hábiles y deja
  la decisión final al equipo interno.
- Si los requisitos mencionados en el correo son vagos o
  incompletos, crea la tarea igual, pero márcala explícitamente
  como "requiere aclaración" e incluye en la descripción qué
  información falta.
- Si el correo no corresponde a ninguna de tus funciones (por
  ejemplo, es spam, una queja no relacionada a un proyecto, o una
  consulta general), no ejecutes ninguna herramienta: repórtalo al
  equipo interno para que lo gestione una persona.
- Nunca inventes datos de contacto, nombres de empresa o
  compromisos que el cliente no haya mencionado explícitamente en
  el correo. Si el correo electrónico del cliente no aparece
  explícitamente en el texto, deja ese campo vacío.
- Ante cualquier duda sobre si una acción debe ejecutarse
  automáticamente o requiere aprobación humana, prioriza la opción
  más conservadora: prepara la acción pero indícala como pendiente
  de confirmación.

TONO
Profesional, claro y directo en tus resúmenes internos. Cuando el
resultado de tu trabajo incluya una respuesta que eventualmente se
enviará al cliente, el tono hacia el cliente debe ser cordial,
cercano y orientado a la solución, sin tecnicismos innecesarios.

FORMATO DE SALIDA
Al final de cada Run, entrega siempre: (1) las acciones ejecutadas
o propuestas, (2) los datos extraídos del correo original, y
(3) cualquier alerta o dato faltante que el equipo deba revisar.
"""

 
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "crear_ticket_en_jira",
            "description": "Crea una nueva tarea o ticket en Jira para el seguimiento de requisitos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string", "description": "Título breve de la tarea."},
                    "descripcion": {"type": "string", "description": "Detalle de la solicitud."},
                    "tipo_tarea": {
                        "type": "string",
                        "enum": ["Historia de Usuario", "Tarea", "Error", "Investigación"],
                    },
                    "requiere_aclaracion": {"type": "boolean"},
                },
                "required": ["titulo", "descripcion", "tipo_tarea", "requiere_aclaracion"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "agendar_reunion_en_google_calendar",
            "description": "Agenda una reunión de seguimiento. Si no hay fecha exacta, propone franjas horarias.",
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo_reunion": {"type": "string"},
                    "correo_invitado": {"type": "string", "description": "Vacío si no aparece explícito en el correo."},
                    "rango_fechas_solicitado": {"type": "string"},
                    "fecha_hora_exacta": {"type": "string", "description": "Vacío si el cliente no la especificó."},
                },
                "required": ["titulo_reunion", "correo_invitado", "rango_fechas_solicitado"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_contacto_en_crm",
            "description": "Actualiza o ingresa los datos de un prospecto en el CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_completo": {"type": "string"},
                    "empresa": {"type": "string"},
                    "interes_principal": {"type": "string"},
                },
                "required": ["nombre_completo", "empresa", "interes_principal"],
            },
        },
    },
]

def crear_ticket_en_jira(titulo, descripcion, tipo_tarea, requiere_aclaracion):
    ticket_id = f"UTP-{uuid.uuid4().hex[:4].upper()}"
    resultado = {
        "ticket_id": ticket_id,
        "titulo": titulo,
        "tipo_tarea": tipo_tarea,
        "requiere_aclaracion": requiere_aclaracion,
        "estado": "creado",
    }
    st.session_state.acciones_log.append(("🎫 Jira", f"Ticket **{ticket_id}** creado — \"{titulo}\""))
    return resultado


def agendar_reunion_en_google_calendar(titulo_reunion, correo_invitado, rango_fechas_solicitado, fecha_hora_exacta=""):
    resultado = {
        "evento": titulo_reunion,
        "invitado": correo_invitado or "(sin correo confirmado — pendiente de validación humana)",
        "rango_propuesto": rango_fechas_solicitado,
        "fecha_hora_exacta": fecha_hora_exacta or "(no especificada — se deben proponer franjas)",
        "estado": "borrador de evento generado",
    }
    st.session_state.acciones_log.append(("📅 Calendar", f"Evento \"{titulo_reunion}\" — {rango_fechas_solicitado}"))
    return resultado


def actualizar_contacto_en_crm(nombre_completo, empresa, interes_principal):
    resultado = {
        "contacto": nombre_completo,
        "empresa": empresa,
        "interes_principal": interes_principal,
        "actualizado_en": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "estado": "actualizado",
    }
    st.session_state.acciones_log.append(("🗂️ CRM", f"Contacto **{nombre_completo}** ({empresa}) actualizado"))
    return resultado


FUNCIONES_DISPONIBLES = {
    "crear_ticket_en_jira": crear_ticket_en_jira,
    "agendar_reunion_en_google_calendar": agendar_reunion_en_google_calendar,
    "actualizar_contacto_en_crm": actualizar_contacto_en_crm,
}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "acciones_log" not in st.session_state:
    st.session_state.acciones_log = []

for msg in st.session_state.messages[1:]:
    if msg["role"] in ("user", "assistant") and msg.get("content"):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def ejecutar_run():
    respuesta = client.chat.completions.create(
        model=MODEL_NAME,
        messages=st.session_state.messages,
        tools=TOOLS,
    )
    mensaje = respuesta.choices[0].message

    if mensaje.tool_calls:
        st.session_state.messages.append(
            {"role": "assistant", "content": mensaje.content, "tool_calls": mensaje.tool_calls}
        )
        for tool_call in mensaje.tool_calls:
            nombre_funcion = tool_call.function.name
            argumentos = json.loads(tool_call.function.arguments)
            funcion = FUNCIONES_DISPONIBLES[nombre_funcion]
            resultado = funcion(**argumentos)

            st.session_state.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(resultado, ensure_ascii=False),
                }
            )
        return ejecutar_run()

    st.session_state.messages.append({"role": "assistant", "content": mensaje.content})
    return mensaje.content



correo = st.chat_input("Pega aquí el correo del cliente a procesar")

if correo:
    st.session_state.messages.append({"role": "user", "content": correo})
    with st.chat_message("user"):
        st.markdown(correo)

    with st.chat_message("assistant"):
        with st.spinner("Procesando correo y ejecutando acciones..."):
            respuesta_final = ejecutar_run()
        st.markdown(respuesta_final)

if st.session_state.acciones_log:
    st.divider()
    st.subheader("📋 Acciones ejecutadas en este Run")
    for sistema, detalle in st.session_state.acciones_log:
        st.markdown(f"**{sistema}** — {detalle}")

with st.sidebar:
    st.subheader("Correo de ejemplo (informe)")
    st.caption("Cópialo y pégalo en el chat para reproducir el ejemplo del informe.")
    st.code(
        "Hola equipo de UTP Consult, gracias por la propuesta. "
        "Nos interesa avanzar. ¿Podríamos tener una reunión la "
        "próxima semana para discutir los detalles técnicos del "
        "módulo de pagos? Adjunto un documento con algunos "
        "requisitos iniciales. Saludos, Ana Torres de TechCorp.",
        language=None,
    )
    if st.button("🔄 Reiniciar conversación"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.session_state.acciones_log = []
        st.rerun()
