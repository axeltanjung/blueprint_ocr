import os
import requests
import json

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.endpoint = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o-mini"  # stabil & murah

        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

    def extract(self, system_prompt: str, user_prompt: str, schema: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": schema
            },
            "temperature": 0
        }

        resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)
