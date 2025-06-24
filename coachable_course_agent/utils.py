import json
import re

def extract_json_block(text: str) -> dict:
    try:
        # Try raw parse
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: extract JSON array or object from LLM text
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise
