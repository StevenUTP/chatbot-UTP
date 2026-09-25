from fastapi import FastAPI
from pydantic import BaseModel
from app.assistant import inicializar_asistente, procesar_correo

app = FastAPI(title="UTPConsult AI Integration")

asistente_activo = inicializar_asistente()

class CorreoRequest(BaseModel):
    remitente: str
    cuerpo: str

@app.post("/procesar-correo")
async def endpoint_procesar_correo(correo: CorreoRequest):
    texto_completo = f"De: {correo.remitente}\n\n{correo.cuerpo}"
    respuesta_ia = procesar_correo(asistente_activo, texto_completo)
    
    return {
        "status": "completado",
        "resumen_asistente": respuesta_ia
    }