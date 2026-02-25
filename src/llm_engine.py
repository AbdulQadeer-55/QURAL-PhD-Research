# src/llm_engine.py
import os
import json
import time
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# MODEL LIST
MODELS = {
    "GPT-4o-Mini": "openai/gpt-4o-mini",
    "Claude-3-Haiku": "anthropic/claude-3-haiku",
    "Llama-3.1-70B": "meta-llama/llama-3.1-70b-instruct",
    "Mistral-Nemo": "mistralai/mistral-nemo",
    "Gemini-2.0-Flash-Lite": "google/gemini-2.0-flash-lite-001" 
}

# Fallback List
GEMINI_FALLBACKS = [
    "google/gemini-flash-1.5",
    "google/gemini-pro-1.5"
]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def clean_json_string(content):
    content = re.sub(r"```json\s*", "", content)
    content = re.sub(r"```\s*$", "", content)
    return content.strip()

def call_llm(messages, model_friendly_name="GPT-4o-Mini"):
    model_id = MODELS.get(model_friendly_name)
    if not model_id:
        return None

    current_model_id = model_id
    
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model=current_model_id,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
                extra_headers={
                    "X-Title": "QURAL PhD Research Pipeline"
                }
            )

            content = response.choices[0].message.content
            if not content:
                continue

            return json.loads(clean_json_string(content), strict=False)

        except Exception as e:
            if "404" in str(e) and "gemini" in model_friendly_name.lower():
                if GEMINI_FALLBACKS:
                    current_model_id = GEMINI_FALLBACKS.pop(0)
                    print(f"⚠️ Switching to fallback: {current_model_id}")
                    continue
            time.sleep(2)

    return None