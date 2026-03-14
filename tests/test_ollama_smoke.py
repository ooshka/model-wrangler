import unittest

from scripts.ollama.smoke import (
    ensure_model_present,
    model_name_variants,
    parse_planner_json_content,
    validate_planner_payload,
)


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


class ValidatePlannerPayloadTests(unittest.TestCase):
    def test_rejects_missing_rationale(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "Planner JSON response missing 'rationale'.",
        ):
            validate_planner_payload({"actions": []})

    def test_rejects_empty_actions(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "Planner JSON response 'actions' must not be empty.",
        ):
            validate_planner_payload({"rationale": "Because", "actions": []})

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


if __name__ == "__main__":
    unittest.main()
