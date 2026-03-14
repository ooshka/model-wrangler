#!/usr/bin/env python3
"""Minimal Ollama smoke path for the Windows-hosted + WSL2 workflow."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_ENV = ROOT / "config" / "ollama.env.example"
LOCAL_ENV = ROOT / "config" / "ollama.env"


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def load_config() -> dict[str, str]:
    config = {
        "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
        "OLLAMA_OPENAI_BASE_URL": "http://127.0.0.1:11434/v1",
        "OLLAMA_CHAT_MODEL": "qwen3:8b",
        "OLLAMA_EMBED_MODEL": "all-minilm",
        "OLLAMA_API_KEY": "ollama",
    }

    for candidate in (EXAMPLE_ENV, LOCAL_ENV):
        config.update(parse_env_file(candidate))

    for key in config:
        config[key] = os.environ.get(key, config[key])

    return config


def request_json(
    url: str,
    payload: dict | None = None,
    *,
    timeout: int = 60,
    headers: dict[str, str] | None = None,
) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    merged_headers = {"Accept": "application/json"}
    if body is not None:
        merged_headers["Content-Type"] = "application/json"
    if headers:
        merged_headers.update(headers)

    request = urllib.request.Request(url, data=body, headers=merged_headers)

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            raw = response.read().decode(charset)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Unable to reach {url}: {exc.reason}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Non-JSON response from {url}: {raw[:400]}") from exc


def check_runtime(config: dict[str, str]) -> dict:
    return request_json(f"{config['OLLAMA_BASE_URL'].rstrip('/')}/api/tags", timeout=10)


def model_name_variants(model_name: str) -> set[str]:
    variants = {model_name}
    if ":" in model_name:
        base, tag = model_name.rsplit(":", 1)
        if tag == "latest":
            variants.add(base)
    else:
        variants.add(f"{model_name}:latest")
    return variants


def ensure_model_present(tags_payload: dict, model_name: str) -> None:
    installed = {
        model.get("model")
        for model in tags_payload.get("models", [])
        if isinstance(model, dict)
    }
    expected_names = model_name_variants(model_name)
    if installed & expected_names:
        return

    raise RuntimeError(
        f"Model '{model_name}' is not installed in Ollama. "
        "Pull it on Windows with 'ollama pull "
        f"{model_name}'."
    )


def run_embeddings_smoke(config: dict[str, str]) -> dict:
    payload = {
        "model": config["OLLAMA_EMBED_MODEL"],
        "input": "Summarize the local_llm repo purpose in a short embedding-friendly sentence.",
    }
    response = request_json(
        f"{config['OLLAMA_OPENAI_BASE_URL'].rstrip('/')}/embeddings",
        payload,
        headers={"Authorization": f"Bearer {config['OLLAMA_API_KEY']}"},
    )

    data = response.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError(f"Embeddings response missing data array: {response}")

    vector = data[0].get("embedding")
    if not isinstance(vector, list) or not vector:
        raise RuntimeError(f"Embeddings response missing vector payload: {response}")

    return {
        "model": response.get("model", config["OLLAMA_EMBED_MODEL"]),
        "dimensions": len(vector),
    }


def run_chat_smoke(config: dict[str, str]) -> dict:
    payload = {
        "model": config["OLLAMA_CHAT_MODEL"],
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a local planning assistant. "
                    "Respond briefly and concretely."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Give two short next steps for standing up a local retrieval "
                    "prototype."
                ),
            },
        ],
    }
    response = request_json(
        f"{config['OLLAMA_OPENAI_BASE_URL'].rstrip('/')}/chat/completions",
        payload,
        headers={"Authorization": f"Bearer {config['OLLAMA_API_KEY']}"},
    )

    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError(f"Chat response missing choices: {response}")

    message = choices[0].get("message", {})
    content = message.get("content", "")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(f"Chat response missing message content: {response}")

    return {
        "model": response.get("model", config["OLLAMA_CHAT_MODEL"]),
        "preview": content.strip().replace("\n", " ")[:160],
    }


def parse_planner_json_content(content: str) -> dict:
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Planner JSON response missing message content.")

    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Planner JSON response was not valid JSON."
        ) from exc

    if not isinstance(payload, dict):
        raise RuntimeError("Planner JSON response must be a JSON object.")

    return payload


def validate_planner_payload(payload: dict) -> dict:
    if "actions" not in payload:
        raise RuntimeError("Planner JSON response missing 'actions'.")

    rationale = payload.get("rationale")
    if rationale is not None and not isinstance(rationale, str):
        raise RuntimeError("Planner JSON response 'rationale' must be a string when present.")

    actions = payload["actions"]
    if not isinstance(actions, list):
        raise RuntimeError("Planner JSON response 'actions' must be an array.")
    if not actions:
        raise RuntimeError("Planner JSON response 'actions' must not be empty.")

    normalized_actions: list[dict] = []
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            raise RuntimeError(
                f"Planner JSON action at index {index} must be an object."
            )

        name = action.get("action")
        if not isinstance(name, str) or not name.strip():
            raise RuntimeError(
                f"Planner JSON action at index {index} is missing a non-empty 'action' string."
            )

        reason = action.get("reason")
        if reason is not None and not isinstance(reason, str):
            raise RuntimeError(
                f"Planner JSON action at index {index} has an invalid 'reason'."
            )

        params = action.get("params")
        if params is not None and not isinstance(params, dict):
            raise RuntimeError(
                f"Planner JSON action at index {index} must include object 'params'."
            )

        normalized_actions.append(
            {
                "action": name.strip(),
                "reason": None if reason is None or not reason.strip() else reason.strip(),
                "params": params or {},
            }
        )

    return {
        "rationale": None if rationale is None or not rationale.strip() else rationale.strip(),
        "actions": normalized_actions,
    }


def run_planner_json_smoke(config: dict[str, str]) -> dict:
    prompt_payload = {
        "intent": "Prepare the next local_llm planner validation step.",
        "context": {
            "project": "local_llm",
            "constraints": [
                "work only inside local_llm",
                "preserve current Ollama baseline",
                "keep the slice small and testable",
            ],
        },
    }
    payload = {
        "model": config["OLLAMA_CHAT_MODEL"],
        "stream": False,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return only JSON with keys rationale and actions. "
                    "Actions must be an array of objects with action, reason, and params."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(prompt_payload),
            },
        ],
    }
    response = request_json(
        f"{config['OLLAMA_OPENAI_BASE_URL'].rstrip('/')}/chat/completions",
        payload,
        headers={"Authorization": f"Bearer {config['OLLAMA_API_KEY']}"},
    )

    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError(f"Planner JSON response missing choices: {response}")

    message = choices[0].get("message", {})
    content = message.get("content", "")
    parsed = parse_planner_json_content(content)
    validated = validate_planner_payload(parsed)
    first_action = validated["actions"][0]["action"]

    return {
        "model": response.get("model", config["OLLAMA_CHAT_MODEL"]),
        "rationale_preview": validated["rationale"].replace("\n", " ")[:160],
        "action_count": len(validated["actions"]),
        "first_action": first_action,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the local Ollama smoke path from WSL2.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only verify runtime reachability and required models.",
    )
    parser.add_argument(
        "--print-config",
        action="store_true",
        help="Print the effective non-secret config and exit.",
    )
    parser.add_argument(
        "--planner-json-only",
        action="store_true",
        help="Run only the strict planner JSON smoke path.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config()

    if args.print_config:
        printable = {
            "OLLAMA_BASE_URL": config["OLLAMA_BASE_URL"],
            "OLLAMA_OPENAI_BASE_URL": config["OLLAMA_OPENAI_BASE_URL"],
            "OLLAMA_CHAT_MODEL": config["OLLAMA_CHAT_MODEL"],
            "OLLAMA_EMBED_MODEL": config["OLLAMA_EMBED_MODEL"],
            "LOCAL_ENV_PRESENT": str(LOCAL_ENV.exists()).lower(),
        }
        print(json.dumps(printable, indent=2, sort_keys=True))
        return 0

    try:
        tags_payload = check_runtime(config)
        ensure_model_present(tags_payload, config["OLLAMA_CHAT_MODEL"])
        ensure_model_present(tags_payload, config["OLLAMA_EMBED_MODEL"])

        result = {
            "runtime": {
                "base_url": config["OLLAMA_BASE_URL"],
                "chat_model": config["OLLAMA_CHAT_MODEL"],
                "embed_model": config["OLLAMA_EMBED_MODEL"],
            }
        }

        if args.check_only:
            result["status"] = "runtime-ready"
        elif args.planner_json_only:
            result["planner_json"] = run_planner_json_smoke(config)
            result["status"] = "planner-json-passed"
        else:
            result["embeddings"] = run_embeddings_smoke(config)
            result["chat"] = run_chat_smoke(config)
            result["planner_json"] = run_planner_json_smoke(config)
            result["status"] = "smoke-passed"
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
