import os
import json
import requests
import time
import random
import re


class OpenRouterClient:
    def __init__(
        self,
        model: str = "mistralai/mistral-small-3.1-24b-instruct:free"
    ):
        self.api_key = os.getenv("OPEN_ROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPEN_ROUTER_API_KEY not set")

        self.model = model
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def _extract_json(self, text: str) -> dict:
        """
        Robust JSON extraction:
        - Removes ```json fences
        - Removes ``` fences
        - Fails hard if JSON invalid
        """
        text = text.strip()

        # Remove markdown code fences
        if text.startswith("```"):
            text = re.sub(r"^```(json)?", "", text, flags=re.IGNORECASE).strip()
            text = re.sub(r"```$", "", text).strip()

        return json.loads(text)

    def extract(self, system_prompt: str, user_prompt: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "blueprint-ocr-demo"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0
        }

        for attempt in range(3):
            resp = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )

            if resp.status_code in (429, 502, 503):
                sleep = (2 ** attempt) + random.uniform(0, 1)
                print(f"OpenRouter retry in {sleep:.1f}s...")
                time.sleep(sleep)
                continue

            if resp.status_code == 404:
                raise RuntimeError(
                    f"OpenRouter 404. Check model availability.\n{resp.text}"
                )

            resp.raise_for_status()

            raw_text = resp.json()["choices"][0]["message"]["content"]

            try:
                return self._extract_json(raw_text)
            except Exception:
                raise RuntimeError(
                    f"Model returned non-JSON output:\n{raw_text}"
                )

        raise RuntimeError("OpenRouter request failed after retries.")
