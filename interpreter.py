
from transformers import pipeline
from functools import lru_cache
import re
import json

@lru_cache(maxsize=1)
def get_interpreter_model():
    print("Loading model...")
    model = pipeline("text-generation", model="google/gemma-2b-it")
    print("Model loaded.")
    return model

def interpret_query(user_input):
    llm = get_interpreter_model()

    prompt = f"""
Translate the following natural language request into a JSON-like filter.
Only return the JSON object. Do not include any explanation or markdown.
Example: "sales in September 2017" ➝ {{ "month": 9, "year": 2017 }}

Request: "{user_input}"
"""

    response = llm(prompt, max_new_tokens=128, temperature=0.2, truncation=True)[0]["generated_text"]

    cleaned = re.sub(r"[“”‘’]", '"', response)
    json_str = re.findall(r"{.*}", cleaned)

    try:
        return json.loads(json_str[0])
    except Exception as e:
        print("Could not parse JSON:", e)
        return {}
