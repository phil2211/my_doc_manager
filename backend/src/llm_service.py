import json
from litellm import completion

def extract_metadata_via_llm(text: str, few_shot_examples: list = None) -> dict:
    # In a real implementation, few_shot_examples would be injected into the prompt
    response = completion(
        model="gpt-4o-mini", # Configurable
        messages=[{"role": "user", "content": f"Extract JSON with date, sender, category from: {text}"}],
        response_format={ "type": "json_object" }
    )
    content = response.choices[0].message.content
    return json.loads(content)