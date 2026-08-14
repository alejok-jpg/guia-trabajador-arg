# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI()

# Permitir peticiones desde tu web en GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar la API Key desde las variables de entorno privadas
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class QuestionRequest(BaseModel):
    prompt: str

@app.post("/api/ask")
async def ask_gemini(request: QuestionRequest):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        system_instruction = (
            "Sos un asistente experto en legislacion laboral y liquidacion de sueldos "
            "de Argentina (Ley de Contrato de Trabajo 20.744). Responde de forma clara, "
            "concisa y comprensible para cualquier trabajador."
        )
        
        full_prompt = f"{system_instruction}\n\nPregunta del usuario: {request.prompt}"
        response = model.generate_content(full_prompt)
        
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}