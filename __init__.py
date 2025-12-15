import os, json, requests
from typing import Any

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"                                         

                                                                   
DEFAULT_MODEL = "deepseek/deepseek-chat:free"                                         

JSON_EXAMPLE = {
  "schema_version": "1.0",
  "language": "ru",
  "user_query": {"symptoms_text": "строка"},
  "triage": {"urgency": "self_care", "red_flags": [], "when_to_seek_help": "строка"},
  "recommendations": [],
  "planner": {"calendar_events": [], "diary_items": [], "notes": []},
  "ui_hints": {"summary": "строка", "disclaimer_short": "строка"}
}

class OpenRouterDeepSeekClient:
    def __init__(self, api_key: str | None = None, app_title: str = "Micro Doser"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("Нет OPENROUTER_API_KEY в env.")
        self.app_title = app_title

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": self.app_title,
        }

    def get_json_plan(self, *, user_text: str, language: str = "ru", model: str = DEFAULT_MODEL) -> dict[str, Any]:
                                                                                                                              
        system = (
            "Верни ТОЛЬКО валидный json (без markdown и текста вокруг). "
            "Структура строго как в примере. Не ставь диагноз. "
            f"ПРИМЕР json: {json.dumps(JSON_EXAMPLE, ensure_ascii=False)}"
        )

        max_out = 1200              

        base_payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": f"language={language}. symptoms_text={user_text}"},
            ],
            "response_format": {"type": "json_object"},
        }

                                       
        payload = dict(base_payload)
        payload["max_tokens"] = max_out
        print("LLM DEBUG:", {"model": model, "max_tokens": payload.get("max_tokens")})

        r = requests.post(OPENROUTER_URL, headers=self._headers(), json=payload, timeout=60)

                                                                                                          
        if r.status_code == 402 and "requested up to 65536" in r.text:
            payload = dict(base_payload)
            payload["max_completion_tokens"] = max_out
            print("LLM DEBUG retry:", {"model": model, "max_completion_tokens": payload.get("max_completion_tokens")})
            r = requests.post(OPENROUTER_URL, headers=self._headers(), json=payload, timeout=60)

        r.raise_for_status()
