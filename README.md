# UTP Assistant — software

Implementación funcional del diseño presentado en la Tarea Académica N.° 2:
el prompt de sistema y las 3 herramientas de function calling ejecutándose
de verdad sobre la API de OpenAI, con interfaz en Streamlit.

## Cómo correrlo

```bash
# 1. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar la API key
cp .env.example .env
# abrir .env y pegar tu clave real de OpenAI

# 4. Ejecutar
streamlit run app.py
```

## Qué hace

1. Pegas un correo de cliente en el chat (o usas el ejemplo de la barra
   lateral, el mismo del informe: Ana Torres de TechCorp).
2. El modelo, siguiendo el prompt de sistema de la sección 2, decide si
   necesita ejecutar alguna de las 3 herramientas de la sección 3.
3. La app ejecuta esas funciones (simuladas: generan un ticket, un evento
   y una actualización de CRM "de mentira", ya que no hay credenciales
   reales de Jira/Calendar/CRM) y le devuelve el resultado al modelo.
4. El modelo entrega la respuesta final con el resumen para el equipo,
   tal como describe el ciclo del Run en la sección 4 del informe.

## Nota importante

Las funciones en `app.py` (`crear_ticket_en_jira`, etc.) están simuladas:
generan datos falsos y solo los guardan en pantalla, no llaman a Jira,
Calendar ni un CRM real. Eso es intencional — la Tarea Académica N.° 2
pide un *diseño técnico*, no una integración productiva. Si se quisiera
conectar a sistemas reales, ahí es donde irían las llamadas HTTP a la
API de Jira, Google Calendar y el CRM correspondiente.
