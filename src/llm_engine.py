# src/llm_engine.py
import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# The "Big 5" Models for the PhD Comparison
# We map friendly names to OpenRouter Model IDs
MODELS = {
    "GPT-4o": "openai/gpt-4o-2024-08-06",
    "Claude-3.5-Sonnet": "anthropic/claude-3.5-sonnet",
    "Gemini-1.5-Pro": "google/gemini-pro-1.5",
    "Llama-3.1-70B": "meta-llama/llama-3.1-70b-instruct",
    "Mistral-Large": "mistralai/mistral-large"
}

# Initialize OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def call_llm(messages, model_friendly_name="GPT-4o"):
    """
    Sends prompts to any of the 5 models via OpenRouter.
    """
    model_id = MODELS.get(model_friendly_name)
    
    if not model_id:
        print(f"❌ Error: Model '{model_friendly_name}' not found.")
        return None

    retries = 3
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                response_format={"type": "json_object"}, 
                temperature=0.1,  # Strict grading
                extra_headers={
                    "HTTP-Referer": "https://fiverr.com", 
                    "X-Title": "PhD Research QURAL"
                }
            )
            content = response.choices[0].message.content
            return json.loads(content)
        
        except Exception as e:
            print(f"⚠️ Error with {model_friendly_name} (Attempt {attempt+1}): {e}")
            time.sleep(2)  # Wait before retry
            
    return None