import os
import json
import google.generativeai as genai


class GeminiClient:
    def __init__(self, model: str = "gemini-2.0-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def extract(self, system_prompt: str, user_prompt: str, schema: dict) -> dict:
        """
        Gemini does NOT natively enforce JSON schema.
        So we enforce it via prompt + strict parsing.
        """

        full_prompt = f"""
{system_prompt}

You MUST output valid JSON only.
The JSON MUST strictly follow this schema:
{json.dumps(schema, indent=2)}

User input:
{user_prompt}
"""

        response = self.model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0,
                "response_mime_type": "application/json"
            }
        )

        text = response.text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise RuntimeError(
                f"Gemini returned invalid JSON:\n{text}"
            )
