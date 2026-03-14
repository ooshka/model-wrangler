import unittest

from scripts.ollama.smoke import ensure_model_present, model_name_variants


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


if __name__ == "__main__":
    unittest.main()
