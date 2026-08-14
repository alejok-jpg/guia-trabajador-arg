# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI()

# Permitir que tu web en GitHub Pages consulte a este servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar la API Key desde las variables de entorno privadas del servidor (Render)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class QuestionRequest(BaseModel):
    prompt: str

@app.post("/api/ask")
async def ask_gemini(request: QuestionRequest):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        system_instruction = (
            "Sos exclusivamente un asistente especializado en legislacion laboral, derechos del trabajador "
            "y liquidacion de sueldos de Argentina (Ley de Contrato de Trabajo 20.744, CCT, licencias, recibos de sueldo, etc.).\n"
            "REGLAS ESTRICTAS DE SEGURIDAD Y FOCO:\n"
            "1. Responde SOLO preguntas vinculadas al ambito laboral y liquidacion de haberes en Argentina.\n"
            "2. Si el usuario pregunta sobre cualquier otro tema (recetas, programacion, deportes, historia, tareas escolares, chistes, etc.), "
            "debes rechazar la consulta amablemente con el siguiente mensaje exacto:\n"
            "'Esta herramienta esta disenada unicamente para responder dudas sobre derechos laborales y liquidacion de sueldos en Argentina. Por favor, realiza una consulta vinculada a este tema.'\n"
            "3. Manten un tono claro, profesional y comprensible para cualquier trabajador."
        )
        
        full_prompt = f"{system_instruction}\n\nPregunta del usuario: {request.prompt}"
        response = model.generate_content(full_prompt)
        
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}