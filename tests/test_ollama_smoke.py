import unittest
from pathlib import Path

from scripts.ollama.smoke import (
    classify_draft_failure,
    classify_planner_failure,
    parse_draft_patch_content,
    ensure_model_present,
    model_name_variants,
    parse_planner_json_content,
    run_planner_parity_fixture,
    validate_draft_patch,
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


class ParseDraftPatchContentTests(unittest.TestCase):
    def test_accepts_unified_diff_text(self) -> None:
        patch = """--- a/notes/today.md
+++ b/notes/today.md
@@ -1 +1,2 @@
 alpha
+beta
"""
        self.assertEqual(parse_draft_patch_content(patch), patch.strip())

    def test_extracts_patch_from_json_object(self) -> None:
        content = '{"patch":"--- a/notes/today.md\\n+++ b/notes/today.md\\n@@ -1 +1,2 @@\\n alpha\\n+beta\\n"}'
        self.assertIn("--- a/notes/today.md", parse_draft_patch_content(content))

    def test_rejects_missing_patch_field(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "missing non-empty 'patch' string",
        ):
            parse_draft_patch_content("{}")


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


class ValidateDraftPatchTests(unittest.TestCase):
    def test_accepts_single_file_markdown_diff(self) -> None:
        result = validate_draft_patch(
            """--- a/notes/today.md
+++ b/notes/today.md
@@ -1 +1,2 @@
 alpha
+beta
"""
        )
        self.assertEqual(
            result,
            {
                "path": "notes/today.md",
                "hunk_count": 1,
                "line_count": 5,
                "change_line_count": 1,
            },
        )

    def test_rejects_non_markdown_target(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "markdown file",
        ):
            validate_draft_patch(
                """--- a/notes/today.txt
+++ b/notes/today.txt
@@ -1 +1,2 @@
 alpha
+beta
"""
            )

    def test_rejects_multi_hunk_patch(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "exactly one diff hunk",
        ):
            validate_draft_patch(
                """--- a/notes/today.md
+++ b/notes/today.md
@@ -1 +1,2 @@
 alpha
+beta
@@ -4 +5,2 @@
 gamma
+delta
"""
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
            classify_draft_failure("Draft patch response missing non-empty 'patch' string."),
            {
                "category": "malformed_draft_payload",
                "boundary": "provider_output",
                "owner": "local_llm",
            },
        )

    def test_classifies_invalid_diff_shape_failure(self) -> None:
        self.assertEqual(
            classify_draft_failure("Draft patch must contain exactly one diff hunk."),
            {
                "category": "invalid_diff_shape",
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


if __name__ == "__main__":
    unittest.main()
