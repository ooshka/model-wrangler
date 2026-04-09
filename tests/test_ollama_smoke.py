import unittest
from pathlib import Path

from scripts.ollama.smoke import (
    classify_draft_failure,
    classify_planner_failure,
    ensure_model_present,
    model_name_variants,
    normalize_note_content,
    parse_edit_intent_content,
    parse_planner_json_content,
    run_planner_parity_fixture,
    run_workflow_failure_fixture,
    validate_edit_intent,
    validate_planner_payload,
)


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class ModelNameVariantsTests(unittest.TestCase):
    def test_unversioned_name_accepts_latest_alias(self) -> None:
        self.assertEqual(
            model_name_variants("all-minilm"),
            {"all-minilm", "all-minilm:latest"},
        )

    def test_latest_tag_accepts_unversioned_alias(self) -> None:
        self.assertEqual(
            model_name_variants("all-minilm:latest"),
            {"all-minilm", "all-minilm:latest"},
        )


class EnsureModelPresentTests(unittest.TestCase):
    def test_accepts_latest_installed_for_unversioned_baseline(self) -> None:
        tags_payload = {
            "models": [
                {"model": "all-minilm:latest"},
                {"model": "qwen3:8b"},
            ]
        }

        ensure_model_present(tags_payload, "all-minilm")


class ParsePlannerJsonContentTests(unittest.TestCase):
    def test_rejects_non_json_content(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "Planner JSON response was not valid JSON.",
        ):
            parse_planner_json_content("not json")

    def test_rejects_non_object_payload(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "Planner JSON response must be a JSON object.",
        ):
            parse_planner_json_content('["array"]')

    def test_accepts_object_payload(self) -> None:
        self.assertEqual(
            parse_planner_json_content('{"rationale":"ok","actions":[]}'),
            {"rationale": "ok", "actions": []},
        )


class ParseEditIntentContentTests(unittest.TestCase):
    def test_rejects_non_json_content(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "Draft response was not valid JSON.",
        ):
            parse_edit_intent_content("not json")

    def test_rejects_non_object_payload(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "Draft response must be a JSON object.",
        ):
            parse_edit_intent_content('["array"]')

    def test_accepts_object_payload(self) -> None:
        self.assertEqual(
            parse_edit_intent_content('{"edit_intent":{"path":"notes/today.md","operation":"replace_content","content":"ok"}}'),
            {
                "edit_intent": {
                    "path": "notes/today.md",
                    "operation": "replace_content",
                    "content": "ok",
                }
            },
        )


class ValidatePlannerPayloadTests(unittest.TestCase):
    def test_rejects_empty_actions(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "Planner JSON response 'actions' must not be empty.",
        ):
            validate_planner_payload({"rationale": "Because", "actions": []})

    def test_accepts_missing_rationale(self) -> None:
        self.assertEqual(
            validate_planner_payload(
                {
                    "actions": [
                        {"action": "notes.read", "reason": "inspect", "params": {"path": "notes/today.md"}}
                    ]
                }
            )["rationale"],
            None,
        )

    def test_accepts_blank_rationale_by_normalizing_to_none(self) -> None:
        self.assertEqual(
            validate_planner_payload(
                {
                    "rationale": "   ",
                    "actions": [
                        {"action": "notes.read", "params": {"path": "notes/today.md"}}
                    ],
                }
            )["rationale"],
            None,
        )

    def test_accepts_blank_reason_and_missing_params_by_normalizing_them(self) -> None:
        self.assertEqual(
            validate_planner_payload(
                {
                    "rationale": "Because",
                    "actions": [
                        {
                            "action": "notes.read",
                            "reason": "   ",
                        }
                    ],
                }
            ),
            {
                "rationale": "Because",
                "actions": [
                    {
                        "action": "notes.read",
                        "reason": None,
                        "params": {},
                    }
                ],
            },
        )

    def test_rejects_invalid_action_params(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "must include object 'params'",
        ):
            validate_planner_payload(
                {
                    "rationale": "Because",
                    "actions": [{"action": "notes.read", "reason": "inspect", "params": []}],
                }
            )

    def test_normalizes_valid_payload(self) -> None:
        self.assertEqual(
            validate_planner_payload(
                {
                    "rationale": " Need context ",
                    "actions": [
                        {
                            "action": "notes.read",
                            "reason": " inspect current note ",
                            "params": {"path": "notes/today.md"},
                        }
                    ],
                }
            ),
            {
                "rationale": "Need context",
                "actions": [
                    {
                        "action": "notes.read",
                        "reason": "inspect current note",
                        "params": {"path": "notes/today.md"},
                    }
                ],
            },
        )


class NormalizeNoteContentTests(unittest.TestCase):
    def test_adds_trailing_newline_when_missing(self) -> None:
        self.assertEqual(normalize_note_content("alpha"), "alpha\n")

    def test_normalizes_windows_newlines(self) -> None:
        self.assertEqual(normalize_note_content("alpha\r\nbeta"), "alpha\nbeta\n")


class ValidateEditIntentTests(unittest.TestCase):
    def test_accepts_replace_content_markdown_intent(self) -> None:
        result = validate_edit_intent(
            {
                "edit_intent": {
                    "path": "notes/today.md",
                    "operation": "replace_content",
                    "content": "# Today\n\n- Done",
                }
            },
            expected_path="notes/today.md",
        )
        self.assertEqual(
            result,
            {
                "path": "notes/today.md",
                "operation": "replace_content",
                "content": "# Today\n\n- Done\n",
            },
        )

    def test_rejects_missing_edit_intent_object(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "missing edit_intent object",
        ):
            validate_edit_intent({})

    def test_rejects_non_markdown_target(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "markdown file",
        ):
            validate_edit_intent(
                {
                    "edit_intent": {
                        "path": "notes/today.txt",
                        "operation": "replace_content",
                        "content": "alpha",
                    }
                }
            )

    def test_rejects_path_mismatch(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "must match the requested path",
        ):
            validate_edit_intent(
                {
                    "edit_intent": {
                        "path": "notes/other.md",
                        "operation": "replace_content",
                        "content": "alpha",
                    }
                },
                expected_path="notes/today.md",
            )

    def test_rejects_unsupported_operation(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "operation is unsupported",
        ):
            validate_edit_intent(
                {
                    "edit_intent": {
                        "path": "notes/today.md",
                        "operation": "append_content",
                        "content": "alpha",
                    }
                }
            )


class PlannerFailureClassificationTests(unittest.TestCase):
    def test_classifies_runtime_unavailable_failure(self) -> None:
        self.assertEqual(
            classify_planner_failure(
                "Unable to reach http://127.0.0.1:11434/v1/chat/completions: [Errno 111] Connection refused"
            ),
            {
                "category": "runtime_unavailable",
                "boundary": "provider_runtime",
                "owner": "local_llm",
            },
        )

    def test_classifies_malformed_payload_failure(self) -> None:
        self.assertEqual(
            classify_planner_failure("Planner JSON response was not valid JSON."),
            {
                "category": "malformed_planner_payload",
                "boundary": "provider_output",
                "owner": "local_llm",
            },
        )


class DraftFailureClassificationTests(unittest.TestCase):
    def test_classifies_runtime_unavailable_failure(self) -> None:
        self.assertEqual(
            classify_draft_failure(
                "Unable to reach http://127.0.0.1:11434/v1/chat/completions: [Errno 111] Connection refused"
            ),
            {
                "category": "runtime_unavailable",
                "boundary": "provider_runtime",
                "owner": "local_llm",
            },
        )

    def test_classifies_malformed_payload_failure(self) -> None:
        self.assertEqual(
            classify_draft_failure("Draft response missing edit_intent object."),
            {
                "category": "malformed_draft_payload",
                "boundary": "provider_output",
                "owner": "local_llm",
            },
        )

    def test_classifies_invalid_edit_intent_shape_failure(self) -> None:
        self.assertEqual(
            classify_draft_failure("Edit intent path must target a markdown file."),
            {
                "category": "invalid_edit_intent_shape",
                "boundary": "provider_output",
                "owner": "local_llm",
            },
        )


class PlannerParityFixtureTests(unittest.TestCase):
    def test_reports_expected_summary(self) -> None:
        result = run_planner_parity_fixture(FIXTURES_DIR / "planner_json_parity_fixture.json")

        self.assertEqual(result["mode"], "planner_parity_fixture")
        self.assertEqual(result["status"], "parity-fixture-passed")
        self.assertEqual(result["first_action"], "notes.read")
        self.assertEqual(len(result["failure_expectations"]), 2)

    def test_raises_on_expected_mismatch(self) -> None:
        import json
        import tempfile
        from pathlib import Path

        fixture_payload = {
            "valid_payload": {
                "actions": [
                    {
                        "action": "notes.read",
                        "params": {"path": "notes/today.md"},
                    }
                ]
            },
            "expected": {
                "rationale": None,
                "action_count": 1,
                "first_action": "notes.write",
                "first_action_param_keys": ["path"],
            },
            "invalid_json_payload": "not json",
            "invalid_json_error": "Planner JSON response was not valid JSON.",
            "failure_expectations": [
                {
                    "name": "malformed_planner_payload",
                    "message": "Planner JSON response was not valid JSON.",
                    "expected_category": "malformed_planner_payload",
                    "expected_boundary": "provider_output",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tempdir:
            fixture_path = Path(tempdir) / "planner_parity_bad.json"
            fixture_path.write_text(json.dumps(fixture_payload), encoding="utf-8")
            with self.assertRaisesRegex(
                RuntimeError,
                "first_action did not match expected output",
            ):
                run_planner_parity_fixture(fixture_path)


class WorkflowFailureFixtureTests(unittest.TestCase):
    def test_reports_expected_summary(self) -> None:
        result = run_workflow_failure_fixture(FIXTURES_DIR / "workflow_failure_fixture.json")

        self.assertEqual(result["mode"], "workflow_failure_fixture")
        self.assertEqual(result["status"], "workflow-failure-fixture-passed")
        self.assertEqual(len(result["planner_failure_expectations"]), 2)
        self.assertEqual(len(result["draft_failure_expectations"]), 3)
        self.assertEqual(
            result["draft_failure_expectations"][0],
            {
                "name": "runtime_unavailable",
                "category": "runtime_unavailable",
                "boundary": "provider_runtime",
                "owner": "local_llm",
            },
        )

    def test_raises_on_expected_owner_mismatch(self) -> None:
        import json
        import tempfile
        from pathlib import Path

        fixture_payload = {
            "planner_failure_expectations": [
                {
                    "name": "runtime_unavailable",
                    "message": (
                        "Unable to reach http://127.0.0.1:11434/v1/chat/completions: "
                        "[Errno 111] Connection refused"
                    ),
                    "expected_category": "runtime_unavailable",
                    "expected_boundary": "provider_runtime",
                    "expected_owner": "mirai",
                }
            ],
            "draft_failure_expectations": [
                {
                    "name": "invalid_edit_intent_shape",
                    "message": "Edit intent path must target a markdown file.",
                    "expected_category": "invalid_edit_intent_shape",
                    "expected_boundary": "provider_output",
                    "expected_owner": "local_llm",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tempdir:
            fixture_path = Path(tempdir) / "workflow_failure_bad.json"
            fixture_path.write_text(json.dumps(fixture_payload), encoding="utf-8")
            with self.assertRaisesRegex(
                RuntimeError,
                "planner_failure_expectations owner mismatch",
            ):
                run_workflow_failure_fixture(fixture_path)


if __name__ == "__main__":
    unittest.main()
