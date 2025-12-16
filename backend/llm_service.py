import json
import os
import re
from typing import Any, Dict, List

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-chat:free"


def _json_schema() -> Dict[str, Any]:
    return {
        "name": "medicine_plan",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["ui_hints", "recommendations", "planner", "disclaimer"],
            "properties": {
                "ui_hints": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["summary", "severity", "need_doctor", "emergency"],
                    "properties": {
                        "summary": {"type": "string"},
                        "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                        "need_doctor": {"type": "boolean"},
                        "emergency": {"type": "boolean"},
                    },
                },
                "recommendations": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["name", "dose", "how_to_take", "course", "warnings", "contraindications", "interactions"],
                        "properties": {
                            "name": {"type": "string"},
                            "dose": {"type": "string"},
                            "how_to_take": {"type": "string"},
                            "course": {"type": "string"},
                            "warnings": {"type": "array", "items": {"type": "string"}},
                            "contraindications": {"type": "array", "items": {"type": "string"}},
                            "interactions": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "planner": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["calendar_events", "diary_entry", "notes"],
                    "properties": {
                        "start_date": {"type": "string"},
                        "calendar_events": {
                            "type": "array",
                        "minItems": 1,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "required": ["title", "datetime", "duration_min", "note"],
                                "properties": {
                                    "title": {"type": "string"},
                                    "datetime": {
                                        "type": "string",
                                        "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?$",
                                    },
                                    "duration_min": {"type": "number"},
                                    "note": {"type": "string"},
                                },
                            },
                        },
                        "diary_entry": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["title", "body"],
                            "properties": {
                                "title": {"type": "string"},
                                "body": {"type": "string"},
                            },
                        },
                        "notes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "required": ["title", "body"],
                                "properties": {
                                    "title": {"type": "string"},
                                    "body": {"type": "string"},
                                },
                            },
                        },
                    },
                },
                "disclaimer": {"type": "string"},
            },
        },
    }


def _build_system_prompt(language: str) -> str:
    lang = (language or "ru").lower()
    if lang.startswith("en"):
        return (
            "You are a medical information assistant. "
            "You are NOT a doctor and you must not give definitive diagnoses. "
            "If symptoms may indicate an emergency, set ui_hints.emergency=true and advise urgent medical help. "
            "Return ONLY one valid JSON object. No markdown. No commentary.\n\n"
            "JSON schema (must match):\n"
            "{\n"
            '  "ui_hints": {"summary": string, "severity": "low|medium|high", "need_doctor": boolean, "emergency": boolean},\n'
            '  "recommendations": [{"name": string, "dose": string, "how_to_take": string, "course": string, '
            '"warnings": [string], "contraindications": [string], "interactions": [string]}],\n'
            '  "planner": {\n'
            '     "calendar_events": [{"title": string, "datetime": "YYYY-MM-DDTHH:MM", "duration_min": number, "note": string}],\n'
            '     "diary_entry": {"title": string, "body": string},\n'
            '     "notes": [{"title": string, "body": string}]\n'
            "  },\n"
            '  "disclaimer": string\n'
            "}\n"
        )

    return (
        "Ты медицинский информационный ассистент. "
        "Ты НЕ врач и не ставишь диагноз. "
        "Если симптомы могут быть опасными, выстави ui_hints.emergency=true и рекомендуй срочно обратиться за медицинской помощью. "
        "Верни ТОЛЬКО один валидный JSON-объект. Без markdown. Без текста вне JSON.\n\n"
        "Схема JSON (строго соблюдать):\n и перед названием лекарства не пиши '1)'"
        "{\n"
        '  "ui_hints": {"summary": string, "severity": "low|medium|high", "need_doctor": boolean, "emergency": boolean},\n'
        '  "recommendations": [{"name": string, "dose": string, "how_to_take": string, "course": string, '
        '"warnings": [string], "contraindications": [string], "interactions": [string]}],\n'
        '  "planner": {\n'
        '     "calendar_events": [{"title": string, "datetime": "YYYY-MM-DDTHH:MM", "duration_min": number, "note": string}],\n'
        '     "diary_entry": {"title": string, "body": string},\n'
        '     "notes": [{"title": string, "body": string}]\n'
        "  },\n"
        '  "disclaimer": string\n'
        "}\n"
    )


def _extract_json(text: str) -> Dict[str, Any]:
    text = (text or "").strip()

                             
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

                                     
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        obj = json.loads(candidate)
        if isinstance(obj, dict):
            return obj

    raise ValueError("LLM вернул не-JSON или неожиданный формат.")


def ask_openrouter_json(
    *,
    api_key: str | None,
    model: str,
    language: str,
    user_text: str,
    max_tokens: int = 1200,
    timeout_s: int = 60,
) -> Dict[str, Any]:
    api_key = (api_key or "").strip() or os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OpenRouter API key отсутствует.")

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": _build_system_prompt(language)},
        {"role": "user", "content": f"Симптомы пользователя:\n{user_text}\n"},
    ]

    max_out = max_tokens
    try:
        max_out = int(max_out)
    except Exception:
        max_out = 1200
                  
    max_out = max(128, min(max_out, 2000))

    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": max_out,
                                                            
        "structured_outputs": True,
        "response_format": {"type": "json_schema", "json_schema": _json_schema()},
        "plugins": [{"id": "response-healing"}],
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout_s)
    if resp.status_code != 200:
                                                                                             
                                                                               
        if resp.status_code == 402 and ("requested up to 65536" in resp.text or "requested up to 32768" in resp.text):
            payload.pop("max_tokens", None)
            payload["max_completion_tokens"] = max_out
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout_s)

        if resp.status_code != 200:
            raise RuntimeError(f"OpenRouter error {resp.status_code}: {resp.text[:400]}")

    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        raise RuntimeError(f"Неожиданный формат ответа OpenRouter: {data}")

    try:
        return _extract_json(content)
    except Exception as e:
                                                                                       
        snippet = (content or "").strip().replace("\n", " ")
        snippet = snippet[:400]
        raise RuntimeError(f"Ошибка LLM: {e}. Ответ (первые 400 символов): {snippet}")

