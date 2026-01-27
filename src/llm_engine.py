# src/llm_engine.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize Client (Ensure API Key is in .env)
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def call_llm(messages, model="gpt-4o-mini"):
    """
    Sends the prompt to OpenAI and returns the JSON response.
    Uses 'gpt-4o-mini' by default to save cost.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2  # Low temp for consistent grading
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return None