from __future__ import annotations
import json
import os


class OpenAICompatibleProvider:
    """Minimal optional adapter for OpenAI-compatible chat-completions APIs."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 model: str | None = None, timeout: float = 90.0):
        self.base_url = (base_url or os.getenv("AI_CFD_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.api_key = api_key or os.getenv("AI_CFD_API_KEY")
        self.model = model or os.getenv("AI_CFD_MODEL")
        self.timeout = timeout
        if not self.api_key or not self.model:
            raise ValueError("Set AI_CFD_API_KEY and AI_CFD_MODEL before using the API provider.")

    def complete(self, *, system_prompt: str, user_prompt: str, role: str) -> str:
        try:
            import httpx
        except ImportError as exc:
            raise RuntimeError("Install the API extra: pip install -e '.[api]'") from exc

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        response = httpx.post(
            url, headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload, timeout=self.timeout
        )
        response.raise_for_status()
        body = response.json()
        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"Unexpected chat-completions response: {json.dumps(body)[:1000]}") from exc
