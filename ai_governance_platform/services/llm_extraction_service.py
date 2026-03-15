"""
LLMExtractionService
Provider-agnostic LLM extraction for document text -> structured fields.

Supported providers via environment variables:
- openai (default): OpenAI-compatible Chat Completions endpoint
- ollama: local Ollama OpenAI-compatible endpoint

Environment variables:
- AI_EXTRACTION_MODE=rules|llm|hybrid (default: rules)
- LLM_PROVIDER=openai|ollama (default: openai)
- LLM_MODEL (defaults vary by provider)
- OPENAI_API_KEY (required for openai provider)
- OPENAI_BASE_URL (default: https://api.openai.com/v1)
- OLLAMA_BASE_URL (default: http://localhost:11434/v1)
"""

import json
import os
import re
from typing import Any, Dict, Optional

import requests


DOC_TYPES = [
    "Loan Application",
    "Disclosure",
    "Credit Report",
    "Appraisal Report",
    "Income Verification",
    "Bank Statement",
    "Tax Return",
    "Closing Documents",
    "Unknown",
]


class LLMExtractionService:
    @staticmethod
    def extraction_mode() -> str:
        return str(os.getenv("AI_EXTRACTION_MODE", "rules")).strip().lower()

    @classmethod
    def is_enabled(cls) -> bool:
        return cls.extraction_mode() in {"llm", "hybrid"}

    @staticmethod
    def _provider() -> str:
        return str(os.getenv("LLM_PROVIDER", "openai")).strip().lower()

    @classmethod
    def _provider_config(cls) -> Dict[str, Any]:
        provider = cls._provider()
        if provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            model = os.getenv("LLM_MODEL", "llama3.2")
            api_key = os.getenv("OPENAI_API_KEY", "ollama")
        else:
            provider = "openai"
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            model = os.getenv("LLM_MODEL", "gpt-4o-mini")
            api_key = os.getenv("OPENAI_API_KEY", "")

        return {
            "provider": provider,
            "base_url": base_url.rstrip("/"),
            "model": model,
            "api_key": api_key,
        }

    @staticmethod
    def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        stripped = text.strip()
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

        match = re.search(r"\{[\s\S]*\}", stripped)
        if not match:
            return None
        candidate = match.group(0)
        try:
            parsed = json.loads(candidate)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None

    @classmethod
    def extract_fields(cls, text: str, detected_doc_type: str = "Unknown") -> Dict[str, Any]:
        cfg = cls._provider_config()

        if cfg["provider"] == "openai" and not cfg["api_key"]:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

        system_prompt = (
            "You extract mortgage-loan document fields into strict JSON. "
            "Only return valid JSON with keys: doc_type (string), fields (object). "
            "Use snake_case for all field keys. "
            "If uncertain, leave field value as empty string. "
            "Do not invent values."
        )

        user_prompt = (
            "Extract structured fields from this document text.\n"
            f"Detected doc type (heuristic): {detected_doc_type}\n"
            f"Allowed doc_type values: {', '.join(DOC_TYPES)}\n"
            "Output JSON schema:\n"
            "{\n"
            "  \"doc_type\": \"...\",\n"
            "  \"fields\": {\"field_name\": \"value\", ...}\n"
            "}\n\n"
            "Document text:\n"
            f"{text}"
        )

        payload = {
            "model": cfg["model"],
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        headers = {"Content-Type": "application/json"}
        if cfg["api_key"]:
            headers["Authorization"] = f"Bearer {cfg['api_key']}"

        response = requests.post(
            f"{cfg['base_url']}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        parsed = cls._extract_json_object(content)
        if not parsed:
            raise ValueError("LLM did not return valid JSON object")

        fields = parsed.get("fields", {})
        if not isinstance(fields, dict):
            raise ValueError("LLM JSON missing valid 'fields' object")

        doc_type = str(parsed.get("doc_type", "") or detected_doc_type).strip() or "Unknown"
        if doc_type not in DOC_TYPES:
            doc_type = detected_doc_type if detected_doc_type in DOC_TYPES else "Unknown"

        normalized_fields = {}
        for key, value in fields.items():
            normalized_key = re.sub(r"[^a-zA-Z0-9_]", "", str(key).strip().replace(" ", "_")).lower()
            normalized_fields[normalized_key] = "" if value is None else str(value).strip()

        return {
            "doc_type": doc_type,
            "fields": normalized_fields,
            "provider": cfg["provider"],
            "model": cfg["model"],
        }
