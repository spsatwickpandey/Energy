import os
import time
from groq import Groq
from dotenv import load_dotenv, find_dotenv

# Always reload .env fresh on every call — prevents stale cached values
def _get_groq_key():
    load_dotenv(find_dotenv(), override=True)
    return os.getenv('GROQ_API_KEY', '').strip()

def _get_groq_model():
    return os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile').strip()

# Placeholder keys to detect unconfigured state
_GROQ_PLACEHOLDER_KEYS = {'your_groq_api_key_here', '', 'gsk_REPLACE_ME'}


def call_groq_llama_api(prompt, max_retries=3):
    # Read key fresh every time (picks up .env changes without restart)
    GROQ_API_KEY = _get_groq_key()
    GROQ_MODEL   = _get_groq_model()

    if not GROQ_API_KEY or GROQ_API_KEY in _GROQ_PLACEHOLDER_KEYS:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. "
            "Please set a valid Groq API key (starting with 'gsk_') in your .env file. "
            "Get a free key at https://console.groq.com"
        )

    client = Groq(api_key=GROQ_API_KEY)

    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert energy consultant. Give actionable, personalized, and professional advice."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=1,
                max_completion_tokens=8192,
                top_p=1,
                stream=False
            )

            if not completion.choices or len(completion.choices) == 0:
                raise ValueError("No choices in API response")

            if not completion.choices[0].message or not completion.choices[0].message.content:
                raise ValueError("Invalid response format from API")

            return completion.choices[0].message.content

        except Exception as e:
            error_str = str(e)
            # Non-retryable: model not found / decommissioned
            if any(k in error_str.lower() for k in ('model_not_found', 'model_decommissioned', 'does not exist')):
                raise RuntimeError(
                    f"Model '{GROQ_MODEL}' is not available or has been decommissioned. "
                    "Valid models: llama-3.3-70b-versatile, llama3-70b-8192, llama3-8b-8192"
                )

            if attempt < max_retries - 1:
                print(f'[groq_client] Error (attempt {attempt + 1}/{max_retries}): {error_str}')
                time.sleep(2 ** attempt)
                continue
            else:
                raise RuntimeError(f"Groq API error: {error_str}")
