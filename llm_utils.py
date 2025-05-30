
from transformers import pipeline
from functools import lru_cache
import re

@lru_cache(maxsize=1)
def get_model():
    print("Loading model...")
    model = pipeline("text-generation", model="google/gemma-2b-it")
    print("Model loaded.")
    return model

def get_filtered_code(user_prompt, df_columns):
    llm = get_model()

    base_prompt = f"""
    You are a Python assistant. The user has a pandas DataFrame called df with these columns:
    {', '.join(df_columns)}.

    Your job:
    - Generate only Python code to filter or group df based on the user's request.
    - Assign the result to a variable called 'filtered_df'.
    - Assume 'Order Date' is already a datetime object.
    - DO NOT use date strings like 'September 2017'.
    - Use .dt.month and .dt.year for any date-based logic.
    - Do not include print(), input(), markdown, or explanations — just the Python code.

    User request: "{user_prompt}"
    """

    response = llm(
        base_prompt,
        max_new_tokens=256,
        temperature=0.2,
        truncation=True
    )[0]["generated_text"]

    # Normalize quotes and strip markdown or prose
    cleaned = re.sub(r'[“”‘’]', "'", response)
    cleaned = re.sub(r"```.*?```", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"(?i)(user\\s?(output|request)|note):.*", "", cleaned)
    cleaned = cleaned.strip()

    # Keep only lines that look like real code
    code_lines = []
    for line in cleaned.splitlines():
        if not line.strip().startswith("#") and "=" in line and "(" in line:
            code_lines.append(line)

    llm_code = "\n".join(code_lines)
    return llm_code
