from __future__ import annotations

import json
from typing import Any
from urllib.parse import urljoin

import requests

SYSTEM_PROMPT = """You are a strict but supportive coding tutor inside a guided practice platform.
Do not reveal a complete solution unless the learner explicitly asks for the final solution.
Diagnose the learner's current misconception using the problem, code, failed tests, and guide notes.
Return valid JSON with exactly these keys:
- diagnosis: one concise sentence
- hint: the smallest useful next hint, one or two sentences
- question: one Socratic question that moves the learner forward
- concept: the main algorithmic concept involved
Do not use markdown fences."""


def _extract_json(text: str) -> dict[str, str]:
    text = text.strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("The model did not return valid JSON.")
        payload = json.loads(text[start : end + 1])

    required = ["diagnosis", "hint", "question", "concept"]
    return {key: str(payload.get(key, "")).strip() for key in required}


def _build_user_prompt(
    problem: dict[str, Any],
    code: str,
    result: dict[str, Any],
    guide_notes: dict[int, str],
    revealed_hint_level: int,
) -> str:
    failed = [item for item in result.get("results", []) if not item.get("passed")][:2]
    notes = [
        {"step": problem["guide"][index], "answer": note}
        for index, note in guide_notes.items()
        if note.strip() and index < len(problem["guide"])
    ]
    context = {
        "problem": {
            "title": problem["title"],
            "description": problem["description"],
            "tags": problem["tags"],
            "constraints": problem["constraints"],
        },
        "learner_code": code,
        "judge_status": result.get("status"),
        "passed": result.get("passed"),
        "total": result.get("total"),
        "failed_tests": failed,
        "guide_notes": notes,
        "existing_hint_level": revealed_hint_level,
    }
    return "Analyze this learner attempt and return the requested JSON:\n" + json.dumps(context, default=str)


def get_llm_feedback(
    settings: dict[str, str],
    problem: dict[str, Any],
    code: str,
    result: dict[str, Any],
    guide_notes: dict[int, str],
    revealed_hint_level: int,
) -> dict[str, str]:
    provider = settings.get("provider", "Off")
    endpoint = settings.get("endpoint", "").strip()
    model = settings.get("model", "").strip()
    api_key = settings.get("api_key", "").strip()

    if provider == "Off":
        raise ValueError("LLM feedback is disabled.")
    if not endpoint or not model:
        raise ValueError("Provide both an endpoint and model name.")

    user_prompt = _build_user_prompt(problem, code, result, guide_notes, revealed_hint_level)

    if provider == "Ollama":
        url = endpoint.rstrip("/") + "/api/chat"
        response = requests.post(
            url,
            json={
                "model": model,
                "stream": False,
                "format": "json",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "options": {"temperature": 0.2},
            },
            timeout=45,
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        return _extract_json(content)

    # Generic OpenAI-compatible endpoint.
    base = endpoint.rstrip("/") + "/"
    url = urljoin(base, "v1/chat/completions")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    response = requests.post(
        url,
        headers=headers,
        json={
            "model": model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=45,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return _extract_json(content)
