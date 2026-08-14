from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuracion de la API Key
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class QuestionRequest(BaseModel):
    prompt: str

@app.post("/api/ask")
async def ask_gemini(request: QuestionRequest):
    try:
        if not api_key:
            return {"response": "Error: No se encontro la GEMINI_API_KEY en Render."}

        # Modelo oficial compatible
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        
        system_instruction = (
            "Sos exclusivamente un asistente especializado en legislacion laboral, derechos del trabajador "
            "y liquidacion de sueldos de Argentina (Ley de Contrato de Trabajo 20.744, CCT, licencias, recibos de sueldo, etc.).\n"
            "REGLAS ESTRICTAS DE SEGURIDAD Y FOCO:\n"
            "1. Responde SOLO preguntas vinculadas al ambito laboral y liquidacion de haberes en Argentina.\n"
            "2. Si el usuario pregunta sobre cualquier otro tema (recetas, programacion, deportes, historia, tareas escolares, chistes, etc.), "
            "debes rechazar la consulta amablemente indicando que la herramienta es solo para consultas laborales.\n"
            "3. Manten un tono claro, profesional y comprensible para cualquier trabajador."
        )
        
        full_prompt = f"{system_instruction}\n\nPregunta del usuario: {request.prompt}"
        response = model.generate_content(full_prompt)
        
        return {"response": response.text}

    except Exception as e:
        print(f"Error interno en la API: {e}")
        return {"response": f"Hubo un inconveniente al conectar con el servicio: {str(e)}"}