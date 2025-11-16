# app/services/llm_service.py
import os
import httpx
from dotenv import load_dotenv
from app.core.system_prompt import SYSTEM_PROMPT

# ============================================================
# 🔧 CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
# ============================================================
load_dotenv()

OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", 0.3))
MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", 1500))

if not API_KEY:
    raise ValueError("⚠️ OPENAI_API_KEY manquant dans le fichier .env")

# ============================================================
# 🧠 SERVICE D’APPEL AU MODÈLE IA
# ============================================================
async def call_llm_api(messages: list[dict]) -> str:
    """
    Appelle le modèle d'IA (OpenAI ou local) avec un contexte juridique KONAN.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(OPENAI_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    except httpx.HTTPStatusError as e:
        error_detail = f"Erreur HTTP {e.response.status_code} : {e.response.text}"
        print("[❌ ERREUR HTTP LLM]", error_detail)
        return f"⚠️ {error_detail}"

    except Exception as e:
        print("[❌ ERREUR INTERNE LLM]", str(e))
        return f"⚠️ Erreur interne du modèle : {str(e)}"
