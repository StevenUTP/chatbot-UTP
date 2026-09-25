import json

tools_schema = [
    {
        "type": "function",
        "name": "crear_ticket_en_jira",
        "description": "Crea un ticket en Jira para seguimiento de requisitos.",
        "parameters": {
            "type": "object",
            "properties": {
                "titulo": {"type": "string"},
                "descripcion": {"type": "string"},
                "tipo_tarea": {"type": "string", "enum": ["Historia de Usuario", "Tarea", "Error", "Investigación"]},
                "requiere_aclaracion": {"type": "boolean"}
            },
            "required": ["titulo", "descripcion", "tipo_tarea", "requiere_aclaracion"]
        }
    },
    {
        "type": "function",
        "name": "agendar_reunion_en_google_calendar",
        "description": "Agenda una reunión en Google Calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "titulo_reunion": {"type": "string"},
                "correo_invitado": {"type": "string"},
                "rango_fechas_solicitado": {"type": "string"}
            },
            "required": ["titulo_reunion", "correo_invitado", "rango_fechas_solicitado"]
        }
    },
    {
        "type": "function",
        "name": "actualizar_contacto_en_crm",
        "description": "Actualiza datos en el CRM.",
        "parameters": {
            "type": "object",
            "properties": {
                "nombre_completo": {"type": "string"},
                "empresa": {"type": "string"},
                "interes_principal": {"type": "string"}
            },
            "required": ["nombre_completo", "empresa", "interes_principal"]
        }
    }
]

def crear_ticket_en_jira(argumentos):
    print(f"-> [JIRA] Ticket creado: {argumentos['titulo']}")
    return json.dumps({"status": "success", "ticket_id": "UTP-105"})

def agendar_reunion_en_google_calendar(argumentos):
    print(f"-> [CALENDAR] Borrador agendado para: {argumentos['correo_invitado']}")
    return json.dumps({"status": "success", "event_id": "cal-9921", "nota": "Pendiente de hora exacta"})

def actualizar_contacto_en_crm(argumentos):
    print(f"-> [CRM] Contacto actualizado: {argumentos['nombre_completo']} ({argumentos['empresa']})")
    return json.dumps({"status": "success", "crm_id": "crm-554"})

funciones_disponibles = {
    "crear_ticket_en_jira": crear_ticket_en_jira,
    "agendar_reunion_en_google_calendar": agendar_reunion_en_google_calendar,
    "actualizar_contacto_en_crm": actualizar_contacto_en_crm
}