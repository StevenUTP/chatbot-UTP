import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from app.tools import tools_schema, funciones_disponibles

load_dotenv(Path(__file__).with_name(".env"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_SISTEMA = """Eres UTP Assistant, el asistente interno de UTPConsult.
Actúas como un gestor de proyectos eficiente.
OBJETIVOS:
1. Extraer requisitos de correos.
2. Crear tareas en Jira.
3. Agendar reuniones.
4. Actualizar el CRM.
5. Producir un resumen interno de las acciones tomadas.
FORMATO: Al final, entrega (1) Acciones ejecutadas, (2) Datos extraídos, (3) Borrador de respuesta al cliente.
"""

def inicializar_asistente():
    return None

def procesar_correo(asistente_id, contenido_correo):
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=PROMPT_SISTEMA,
        input=contenido_correo,
        tools=tools_schema,
    )

    while True:
        tool_outputs = []
        for item in response.output:
            if item.type == "function_call":
                argumentos = json.loads(item.arguments)
                funcion_a_ejecutar = funciones_disponibles[item.name]
                resultado_str = funcion_a_ejecutar(argumentos)
                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": resultado_str,
                })

        if not tool_outputs:
            return response.output_text

        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=PROMPT_SISTEMA,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=tools_schema,
        )