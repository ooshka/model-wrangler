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
EDIT_INTENT_REPLACE_CONTENT = "replace_content"


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


def parse_edit_intent_content(content: str) -> dict:
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Draft response missing message content.")

    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Draft response was not valid JSON.") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("Draft response must be a JSON object.")

    return payload


def normalize_note_content(content: str) -> str:
    normalized = content.replace("\r\n", "\n")
    if not normalized or normalized.endswith("\n"):
        return normalized
    return f"{normalized}\n"


def validate_edit_intent(payload: dict, *, expected_path: str | None = None) -> dict:
    edit_intent = payload.get("edit_intent")
    if not isinstance(edit_intent, dict):
        raise RuntimeError("Draft response missing edit_intent object.")

    path = edit_intent.get("path")
    if not isinstance(path, str) or not path.strip():
        raise RuntimeError("Edit intent path is required.")
    path = path.strip()
    if not path.endswith(".md"):
        raise RuntimeError("Edit intent path must target a markdown file.")
    if ".." in Path(path).parts:
        raise RuntimeError("Edit intent path must be repo-relative without traversal.")
    if expected_path is not None and path != expected_path:
        raise RuntimeError("Edit intent path must match the requested path.")

    operation = edit_intent.get("operation")
    if not isinstance(operation, str) or not operation.strip():
        raise RuntimeError("Edit intent operation is required.")
    operation = operation.strip()
    if operation != EDIT_INTENT_REPLACE_CONTENT:
        raise RuntimeError("Edit intent operation is unsupported.")

    content = edit_intent.get("content")
    if not isinstance(content, str):
        raise RuntimeError("Edit intent content must be a string.")

    return {
        "path": path,
        "operation": operation,
        "content": normalize_note_content(content),
    }


def classify_planner_failure(message: str) -> dict[str, str]:
    normalized = message.strip()
    if normalized.startswith("Unable to reach "):
        return {
            "category": "runtime_unavailable",
            "boundary": "provider_runtime",
            "owner": "local_llm",
        }
    if normalized.startswith("Planner JSON response"):
        return {
            "category": "malformed_planner_payload",
            "boundary": "provider_output",
            "owner": "local_llm",
        }
    return {
        "category": "unknown",
        "boundary": "unknown",
        "owner": "local_llm",
    }


def classify_draft_failure(message: str) -> dict[str, str]:
    normalized = message.strip()
    if normalized.startswith("Unable to reach "):
        return {
            "category": "runtime_unavailable",
            "boundary": "provider_runtime",
            "owner": "local_llm",
        }
    if normalized.startswith("Draft response"):
        return {
            "category": "malformed_draft_payload",
            "boundary": "provider_output",
            "owner": "local_llm",
        }
    if normalized.startswith("Edit intent "):
        return {
            "category": "invalid_edit_intent_shape",
            "boundary": "provider_output",
            "owner": "local_llm",
        }
    return {
        "category": "unknown",
        "boundary": "unknown",
        "owner": "local_llm",
    }


def validate_failure_expectations(
    raw_expectations: list,
    *,
    classifier,
    label: str,
) -> list[dict[str, str]]:
    if not isinstance(raw_expectations, list) or not raw_expectations:
        raise ValueError(f"Fixture must include a non-empty '{label}' array.")

    summaries = []
    for item in raw_expectations:
        if not isinstance(item, dict):
            raise ValueError(f"Each entry in '{label}' must be an object.")

        name = item.get("name")
        message = item.get("message")
        expected_category = item.get("expected_category")
        expected_boundary = item.get("expected_boundary")
        expected_owner = item.get("expected_owner")
        if not all(isinstance(value, str) and value for value in (
            name,
            message,
            expected_category,
            expected_boundary,
            expected_owner,
        )):
            raise ValueError(
                f"Each entry in '{label}' must include non-empty name, message, "
                "expected_category, expected_boundary, and expected_owner strings."
            )

        summary = classifier(message)
        if summary["category"] != expected_category:
            raise RuntimeError(
                f"{label} category mismatch for '{name}'."
            )
        if summary["boundary"] != expected_boundary:
            raise RuntimeError(
                f"{label} boundary mismatch for '{name}'."
            )
        if summary["owner"] != expected_owner:
            raise RuntimeError(
                f"{label} owner mismatch for '{name}'."
            )

        summaries.append({"name": name, **summary})

    return summaries


def run_planner_parity_fixture(fixture_path: Path | str) -> dict:
    fixture_path = Path(fixture_path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture must be a JSON object.")

    valid_payload = payload.get("valid_payload")
    if not isinstance(valid_payload, dict):
        raise ValueError("Fixture must include a 'valid_payload' object.")

    expected = payload.get("expected")
    if not isinstance(expected, dict):
        raise ValueError("Fixture must include an 'expected' object.")

    parsed = parse_planner_json_content(json.dumps(valid_payload))
    validated = validate_planner_payload(parsed)

    expected_action_count = int(expected["action_count"])
    expected_first_action = expected["first_action"]
    expected_rationale = expected.get("rationale")
    expected_param_keys = expected.get("first_action_param_keys", [])
    if not isinstance(expected_param_keys, list):
        raise ValueError("'first_action_param_keys' must be an array when present.")

    actual_first_action = validated["actions"][0]
    if len(validated["actions"]) != expected_action_count:
        raise RuntimeError(
            "Planner parity fixture action_count did not match expected output."
        )
    if actual_first_action["action"] != expected_first_action:
        raise RuntimeError(
            "Planner parity fixture first_action did not match expected output."
        )
    if validated["rationale"] != expected_rationale:
        raise RuntimeError(
            "Planner parity fixture rationale did not match expected output."
        )
    if sorted(actual_first_action["params"].keys()) != sorted(expected_param_keys):
        raise RuntimeError(
            "Planner parity fixture first_action params did not match expected output."
        )

    raw_invalid_payload = payload.get("invalid_json_payload")
    if not isinstance(raw_invalid_payload, str):
        raise ValueError("Fixture must include an 'invalid_json_payload' string.")
    expected_invalid_json_error = payload.get("invalid_json_error")
    if not isinstance(expected_invalid_json_error, str):
        raise ValueError("Fixture must include an 'invalid_json_error' string.")
    try:
        parse_planner_json_content(raw_invalid_payload)
    except RuntimeError as exc:
        if str(exc) != expected_invalid_json_error:
            raise RuntimeError(
                "Planner parity fixture invalid_json_error did not match expected output."
            ) from exc
    else:
        raise RuntimeError("Planner parity fixture invalid_json_payload unexpectedly parsed.")

    failure_expectations = validate_failure_expectations(
        payload.get("failure_expectations"),
        classifier=classify_planner_failure,
        label="Planner parity fixture failure_expectations",
    )

    return {
        "mode": "planner_parity_fixture",
        "fixture_path": str(fixture_path),
        "status": "parity-fixture-passed",
        "rationale": validated["rationale"],
        "action_count": len(validated["actions"]),
        "first_action": actual_first_action["action"],
        "failure_expectations": failure_expectations,
    }


def run_workflow_failure_fixture(fixture_path: Path | str) -> dict:
    fixture_path = Path(fixture_path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture must be a JSON object.")

    planner_failures = validate_failure_expectations(
        payload.get("planner_failure_expectations"),
        classifier=classify_planner_failure,
        label="Workflow failure fixture planner_failure_expectations",
    )
    draft_failures = validate_failure_expectations(
        payload.get("draft_failure_expectations"),
        classifier=classify_draft_failure,
        label="Workflow failure fixture draft_failure_expectations",
    )

    return {
        "mode": "workflow_failure_fixture",
        "fixture_path": str(fixture_path),
        "status": "workflow-failure-fixture-passed",
        "planner_failure_expectations": planner_failures,
        "draft_failure_expectations": draft_failures,
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


def run_edit_intent_smoke(config: dict[str, str]) -> dict:
    target_path = "notes/local_llm_status.md"
    prompt_payload = {
        "instruction": "Add one bullet noting that local edit-intent smoke is active.",
        "path": target_path,
        "content": "# Local LLM Status\n\n- Planner smoke is active.\n",
        "constraints": [
            "return only json with an edit_intent object",
            "target the provided markdown path",
            "use operation replace_content",
            "return the full replacement note content",
        ],
    }
    payload = {
        "model": config["OLLAMA_CHAT_MODEL"],
        "stream": False,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return only JSON with top-level key edit_intent. "
                    "edit_intent must contain path, operation, and content. "
                    "Use operation replace_content and keep the path exactly as provided."
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
        raise RuntimeError(f"Draft response missing choices: {response}")

    message = choices[0].get("message", {})
    content = message.get("content", "")
    parsed = parse_edit_intent_content(content)
    validated = validate_edit_intent(parsed, expected_path=target_path)

    return {
        "model": response.get("model", config["OLLAMA_CHAT_MODEL"]),
        "path": validated["path"],
        "operation": validated["operation"],
        "content_length": len(validated["content"]),
        "content_preview": validated["content"].splitlines()[0] if validated["content"] else "",
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
    parser.add_argument(
        "--edit-intent-only",
        action="store_true",
        help="Run only the workflow edit_intent smoke path.",
    )
    parser.add_argument(
        "--workflow-failure-fixture-only",
        action="store_true",
        help="Run only the local workflow failure fixture check.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config()
    workflow_failure_fixture_path = ROOT / "tests" / "fixtures" / "workflow_failure_fixture.json"

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

    if args.workflow_failure_fixture_only:
        try:
            result = run_workflow_failure_fixture(workflow_failure_fixture_path)
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

        print(json.dumps(result, indent=2, sort_keys=True))
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
        elif args.edit_intent_only:
            result["edit_intent"] = run_edit_intent_smoke(config)
            result["status"] = "edit-intent-passed"
        else:
            result["embeddings"] = run_embeddings_smoke(config)
            result["chat"] = run_chat_smoke(config)
            result["planner_json"] = run_planner_json_smoke(config)
            result["edit_intent"] = run_edit_intent_smoke(config)
            result["status"] = "smoke-passed"
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
