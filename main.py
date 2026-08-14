from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.environ.get("GEMINI_API_KEY")

class QuestionRequest(BaseModel):
    prompt: str

@app.post("/api/ask")
async def ask_gemini(request: QuestionRequest):
    try:
        if not api_key:
            return {"response": "Error: No se encontro la GEMINI_API_KEY en Render."}

        client = genai.Client(api_key=api_key)

        system_instruction = (
            "Sos exclusivamente un asistente especializado en legislacion laboral, derechos del trabajador "
            "y liquidacion de sueldos de Argentina (Ley de Contrato de Trabajo 20.744, CCT, licencias, recibos de sueldo, etc.).\n"
            "REGLAS ESTRICTAS DE SEGURIDAD Y FOCO:\n"
            "1. Responde SOLO preguntas vinculadas al ambito laboral y liquidacion de haberes en Argentina.\n"
            "2. Si el usuario pregunta sobre cualquier otro tema (recetas, programacion, deportes, historia, tareas escolares, chistes, etc.), "
            "debes rechazar la consulta amablemente indicando que la herramienta es solo para consultas laborales.\n"
            "3. Manten un tono claro, profesional y comprensible para cualquier trabajador."
        )

        # Lista de modelos vigentes ordenados por preferencia
        candidate_models = ["gemini-3.5-flash", "gemini-3-flash-preview", "gemini-2.5-flash"]
        
        last_error = None
        for model_name in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=request.prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                if response.text:
                    return {"response": response.text}
            except Exception as err:
                last_error = err
                continue

        # Si ninguno respondio, devuelve el ultimo error detallado
        return {"response": f"Hubo un inconveniente al conectar con los modelos disponibles: {str(last_error)}"}

    except Exception as e:
        print(f"Error interno en la API: {e}")
        return {"response": f"Hubo un inconveniente al conectar con el servicio: {str(e)}"}