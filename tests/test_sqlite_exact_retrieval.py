import json
import tempfile
import unittest
from pathlib import Path

from scripts.retrieval.sqlite_exact import (
    ChunkRecord,
    SQLiteExactIndex,
    run_benchmark,
    run_retrieval_parity_fixture,
    run_rerank_evaluation,
)


class SQLiteExactIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "retrieval.sqlite3"
        self.index = SQLiteExactIndex(self.db_path)
        self.index.upsert_chunks(
            [
                ChunkRecord(
                    path="notes/alpha.md",
                    chunk_index=0,
                    content="alpha beta gamma",
                    embedding=(1.0, 0.0, 0.0),
                ),
                ChunkRecord(
                    path="notes/alpha.md",
                    chunk_index=1,
                    content="delta epsilon zeta",
                    embedding=(0.8, 0.2, 0.0),
                ),
                ChunkRecord(
                    path="notes/beta.md",
                    chunk_index=0,
                    content="theta iota kappa",
                    embedding=(0.0, 1.0, 0.0),
                ),
            ]
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_returns_ranked_contract_shape(self) -> None:
        results = self.index.query(
            (1.0, 0.0, 0.0),
            limit=2,
            query_text="alpha summary",
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["path"], "notes/alpha.md")
        self.assertEqual(results[0]["chunk_index"], 0)
        self.assertEqual(results[0]["content"], "alpha beta gamma")
        self.assertGreater(results[0]["score"], results[1]["score"])
        self.assertEqual(results[0]["snippet_offset"], {"start": 0, "end": 5})

    def test_ties_break_deterministically_by_path_then_chunk_index(self) -> None:
        self.index.upsert_chunks(
            [
                ChunkRecord(
                    path="notes/a.md",
                    chunk_index=2,
                    content="same score one",
                    embedding=(0.5, 0.5, 0.0),
                ),
                ChunkRecord(
                    path="notes/a.md",
                    chunk_index=1,
                    content="same score zero",
                    embedding=(0.5, 0.5, 0.0),
                ),
            ]
        )

        results = self.index.query((0.5, 0.5, 0.0), limit=3)

        tied = [
            (item["path"], item["chunk_index"])
            for item in results
            if item["path"] == "notes/a.md"
        ]
        self.assertEqual(tied, [("notes/a.md", 1), ("notes/a.md", 2)])

    def test_path_prefix_filters_before_ranking(self) -> None:
        results = self.index.query(
            (0.0, 1.0, 0.0),
            limit=5,
            path_prefix="notes/b",
        )

        self.assertEqual(
            results,
            [
                {
                    "path": "notes/beta.md",
                    "chunk_index": 0,
                    "content": "theta iota kappa",
                    "score": 1.0,
                    "snippet_offset": None,
                }
            ],
        )

    def test_irrelevant_or_zero_score_chunks_are_dropped(self) -> None:
        results = self.index.query((0.0, 0.0, 1.0), limit=5)
        self.assertEqual(results, [])

    def test_rejects_mixed_dimensions_in_one_write(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "same embedding dimensions",
        ):
            self.index.upsert_chunks(
                [
                    ChunkRecord(
                        path="notes/mixed.md",
                        chunk_index=0,
                        content="alpha",
                        embedding=(1.0, 0.0),
                    ),
                    ChunkRecord(
                        path="notes/mixed.md",
                        chunk_index=1,
                        content="beta",
                        embedding=(1.0, 0.0, 0.0),
                    ),
                ]
            )

    def test_rejects_write_with_artifact_dimension_mismatch(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "do not match this retrieval artifact",
        ):
            self.index.upsert_chunks(
                [
                    ChunkRecord(
                        path="notes/other.md",
                        chunk_index=0,
                        content="alpha",
                        embedding=(1.0, 0.0),
                    )
                ]
            )

    def test_rejects_query_with_artifact_dimension_mismatch(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Query embedding dimensions do not match",
        ):
            self.index.query((1.0, 0.0), limit=2)


class RunBenchmarkTests(unittest.TestCase):
    def test_reports_build_and_query_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            db_path = Path(tempdir) / "benchmark.sqlite3"
            result = run_benchmark(
                db_path,
                [
                    ChunkRecord(
                        path="notes/alpha.md",
                        chunk_index=0,
                        content="alpha beta",
                        embedding=(1.0, 0.0),
                    )
                ],
                query_embedding=(1.0, 0.0),
                limit=1,
                query_text="alpha",
            )

        self.assertEqual(result["chunk_count"], 1)
        self.assertEqual(result["note_count"], 1)
        self.assertEqual(result["embedding_dimensions"], 2)
        self.assertGreater(result["artifact_bytes"], 0)
        self.assertEqual(result["inserted_count"], 1)
        self.assertEqual(result["limit"], 1)
        self.assertIn("build_seconds", result)
        self.assertIn("query_seconds", result)
        self.assertEqual(
            result["top_result"],
            {"path": "notes/alpha.md", "chunk_index": 0, "score": 1.0},
        )
        self.assertTrue(result["reset"])

    def test_resets_existing_artifact_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            db_path = Path(tempdir) / "benchmark.sqlite3"
            index = SQLiteExactIndex(db_path)
            index.upsert_chunks(
                [
                    ChunkRecord(
                        path="notes/stale.md",
                        chunk_index=0,
                        content="stale row",
                        embedding=(1.0, 0.0),
                    )
                ]
            )

            result = run_benchmark(
                db_path,
                [
                    ChunkRecord(
                        path="notes/fresh.md",
                        chunk_index=0,
                        content="fresh row",
                        embedding=(1.0, 0.0),
                    )
                ],
                query_embedding=(1.0, 0.0),
                limit=1,
                query_text="fresh",
            )

        self.assertEqual(result["chunk_count"], 1)
        self.assertEqual(result["note_count"], 1)
        self.assertEqual(
            result["top_result"],
            {"path": "notes/fresh.md", "chunk_index": 0, "score": 1.0},
        )

    def test_can_reuse_artifact_when_reset_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            db_path = Path(tempdir) / "benchmark.sqlite3"
            first = run_benchmark(
                db_path,
                [
                    ChunkRecord(
                        path="notes/alpha.md",
                        chunk_index=0,
                        content="alpha",
                        embedding=(1.0, 0.0),
                    )
                ],
                query_embedding=(1.0, 0.0),
                limit=1,
                reset=True,
            )
            second = run_benchmark(
                db_path,
                [
                    ChunkRecord(
                        path="notes/beta.md",
                        chunk_index=0,
                        content="beta",
                        embedding=(1.0, 0.0),
                    )
                ],
                query_embedding=(1.0, 0.0),
                limit=2,
                reset=False,
            )

        self.assertEqual(first["chunk_count"], 1)
        self.assertEqual(first["note_count"], 1)
        self.assertEqual(second["chunk_count"], 2)
        self.assertEqual(second["note_count"], 2)
        self.assertEqual(second["embedding_dimensions"], 2)
        self.assertGreater(second["artifact_bytes"], 0)
        self.assertFalse(second["reset"])


class RunRerankEvaluationTests(unittest.TestCase):
    def test_reports_reranked_ordering_and_latency(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            db_path = Path(tempdir) / "rerank.sqlite3"
            result = run_rerank_evaluation(
                db_path,
                [
                    ChunkRecord(
                        path="notes/summary.md",
                        chunk_index=0,
                        content="Weekly planning recap with action items and owner notes.",
                        embedding=(1.0, 0.0, 0.0),
                    ),
                    ChunkRecord(
                        path="notes/today.md",
                        chunk_index=0,
                        content="Alpha budget decisions and alpha budget follow-up tasks.",
                        embedding=(0.92, 0.08, 0.0),
                    ),
                ],
                query_embedding=(1.0, 0.0, 0.0),
                limit=2,
                query_text="alpha budget",
            )

        self.assertEqual(result["mode"], "rerank_evaluation")
        self.assertEqual(result["chunk_count"], 2)
        self.assertEqual(result["note_count"], 2)
        self.assertTrue(result["changed_top_result"])
        self.assertTrue(result["changed_ranking"])
        self.assertEqual(result["baseline_results"][0]["path"], "notes/summary.md")
        self.assertEqual(result["reranked_results"][0]["path"], "notes/today.md")
        self.assertEqual(result["reranked_results"][0]["matched_term_count"], 2)
        self.assertIn("baseline_query_seconds", result)
        self.assertIn("rerank_seconds", result)

    def test_does_not_change_default_benchmark_output_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            db_path = Path(tempdir) / "benchmark.sqlite3"
            result = run_benchmark(
                db_path,
                [
                    ChunkRecord(
                        path="notes/alpha.md",
                        chunk_index=0,
                        content="alpha beta",
                        embedding=(1.0, 0.0),
                    )
                ],
                query_embedding=(1.0, 0.0),
                limit=1,
                query_text="alpha",
            )

        self.assertNotIn("mode", result)
        self.assertNotIn("baseline_results", result)
        self.assertNotIn("reranked_results", result)


class FixtureCompatibilityTests(unittest.TestCase):
    def test_example_fixture_payload_is_json_serializable(self) -> None:
        payload = {
            "chunks": [
                {
                    "path": "notes/sample.md",
                    "chunk_index": 0,
                    "content": "alpha beta",
                    "embedding": [1.0, 0.0],
                }
            ],
            "query_embedding": [1.0, 0.0],
            "query_text": "alpha",
            "limit": 1,
        }

        serialized = json.dumps(payload)
        self.assertIn("query_embedding", serialized)

    def test_retrieval_parity_fixture_reports_expected_summary(self) -> None:
        fixture_payload = {
            "chunks": [
                {
                    "path": "notes/summary.md",
                    "chunk_index": 0,
                    "content": "Weekly planning recap with action items and owner notes.",
                    "embedding": [1.0, 0.0, 0.0],
                },
                {
                    "path": "notes/today.md",
                    "chunk_index": 0,
                    "content": "Alpha budget decisions and alpha budget follow-up tasks for today.",
                    "embedding": [0.92, 0.08, 0.0],
                },
            ],
            "query_embedding": [1.0, 0.0, 0.0],
            "query_text": "alpha budget",
            "limit": 2,
            "expected": {
                "changed_top_result": True,
                "changed_ranking": True,
                "baseline_results": [
                    {
                        "path": "notes/summary.md",
                        "chunk_index": 0,
                        "score": 1.0,
                        "matched_term_count": 0,
                    },
                    {
                        "path": "notes/today.md",
                        "chunk_index": 0,
                        "score": 0.996241,
                        "matched_term_count": 2,
                    },
                ],
                "reranked_results": [
                    {
                        "path": "notes/today.md",
                        "chunk_index": 0,
                        "score": 0.996241,
                        "matched_term_count": 2,
                    },
                    {
                        "path": "notes/summary.md",
                        "chunk_index": 0,
                        "score": 1.0,
                        "matched_term_count": 0,
                    },
                ],
            },
        }

        with tempfile.TemporaryDirectory() as tempdir:
            fixture_path = Path(tempdir) / "retrieval_parity.json"
            fixture_path.write_text(json.dumps(fixture_payload), encoding="utf-8")
            result = run_retrieval_parity_fixture(
                Path(tempdir) / "parity.sqlite3",
                fixture_path,
            )

        self.assertEqual(result["mode"], "retrieval_parity_fixture")
        self.assertEqual(result["status"], "parity-fixture-passed")
        self.assertTrue(result["changed_top_result"])

    def test_retrieval_parity_fixture_raises_on_expected_mismatch(self) -> None:
        fixture_payload = {
            "chunks": [
                {
                    "path": "notes/sample.md",
                    "chunk_index": 0,
                    "content": "alpha beta",
                    "embedding": [1.0, 0.0],
                }
            ],
            "query_embedding": [1.0, 0.0],
            "query_text": "alpha",
            "limit": 1,
            "expected": {
                "changed_top_result": False,
                "changed_ranking": False,
                "baseline_results": [
                    {
                        "path": "notes/sample.md",
                        "chunk_index": 0,
                        "score": 0.5,
                        "matched_term_count": 1,
                    }
                ],
                "reranked_results": [
                    {
                        "path": "notes/sample.md",
                        "chunk_index": 0,
                        "score": 0.5,
                        "matched_term_count": 1,
                    }
                ],
            },
        }

        with tempfile.TemporaryDirectory() as tempdir:
            fixture_path = Path(tempdir) / "retrieval_parity_bad.json"
            fixture_path.write_text(json.dumps(fixture_payload), encoding="utf-8")
            with self.assertRaisesRegex(
                RuntimeError,
                "baseline_results did not match expected output",
            ):
                run_retrieval_parity_fixture(
                    Path(tempdir) / "parity.sqlite3",
                    fixture_path,
                )


if __name__ == "__main__":
    unittest.main()
