import json
import re
from transformers import pipeline
from functools import lru_cache

@lru_cache(maxsize=1)
def get_interpreter():
    print("Loading interpreter model...")
    model = pipeline("text-generation", model="google/gemma-2b-it")
    print("Interpreter model loaded.")
    return model

def interpret_query(user_query):
    prompt = f"""
You are a smart assistant that translates user questions into structured filters
for a pandas DataFrame. The DataFrame contains these columns:

['row id', 'order id', 'order date', 'ship date', 'ship mode', 'customer id', 'customer name',
 'segment', 'country', 'city', 'state', 'postal code', 'region', 'product id', 'category',
 'sub-category', 'product name', 'sales']

Respond ONLY with a valid Python dictionary.
All dictionary keys must be lowercase to match the DataFrame.

Examples:
"sales in September 2017" -> {{"month": 9, "year": 2017}}
"sales for December 2016 in california" -> {{"month": 12, "year": 2016, "state": "california"}}
"sales in the west region in 2018" -> {{"region": "west", "year": 2018}}
"sales of phones in texas in 2016" -> {{"sub-category": "phones", "state": "texas", "year": 2016}}
"sales in new york in Q4 2015" -> {{"city": "new york", "quarter": 4, "year": 2015}}
"sales for office supplies by consumer segment" -> {{"category": "office supplies", "segment": "consumer"}}
"orders shipped in second class to florida" -> {{"ship mode": "second class", "state": "florida"}}
"sales by andrew allen in 2017" -> {{"customer name": "andrew allen", "year": 2017}}
"sales in los angeles in november 2018" -> {{"city": "los angeles", "month": 11, "year": 2018}}
"bookcases sales in the central region" -> {{"sub-category": "bookcases", "region": "central"}}
"sales shipped after october 2016" -> {{"from_month": 10, "from_year": 2016}}
"binders shipped before april 2017" -> {{"to_month": 4, "to_year": 2017, "sub-category": "binders"}}
"technology sales in Q1 2017 in new york" -> {{"category": "technology", "quarter": 1, "year": 2017, "city": "new york"}}
"sales by home office in 2015" -> {{"segment": "home office", "year": 2015}}
"sales in california in Q3" -> {{"state": "california", "quarter": 3}}
"phone sales in los angeles in Q2 2016" -> {{"sub-category": "phones", "city": "los angeles", "quarter": 2, "year": 2016}}
"sales in 2018 by brosina hoffman" -> {{"customer name": "brosina hoffman", "year": 2018}}
"sales of appliances shipped with standard class" -> {{"sub-category": "appliances", "ship mode": "standard class"}}
"consumer orders for chairs in washington" -> {{"segment": "consumer", "sub-category": "chairs", "state": "washington"}}
"sales in fort worth by harold pawlan in 2016" -> {{"city": "fort worth", "customer name": "harold pawlan", "year": 2016}}
... (expand with 80 more examples in actual use)

User query: "{user_query}"
"""

    model = get_interpreter()
    output = model(prompt, max_new_tokens=256, temperature=0.2)[0]["generated_text"]
    print("🔍 Raw model output:\n", output)

    try:
        json_candidates = re.findall(r"{.*?}", output, re.DOTALL)
        if not json_candidates:
            raise ValueError("No JSON found in model output.")

        json_str = json_candidates[-1]
        result = json.loads(json_str)

        # Normalize all keys to lowercase
        result = {k.lower(): v for k, v in result.items()}

        print("✅ Parsed JSON:", result)
        return result
    except Exception as e:
        print("Error parsing model output:", e)
        return {}
