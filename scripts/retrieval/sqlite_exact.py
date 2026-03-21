#!/usr/bin/env python3
"""SQLite-backed exact retrieval baseline for local_llm."""

from __future__ import annotations

import argparse
import json
import math
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ChunkRecord:
    path: str
    chunk_index: int
    content: str
    embedding: tuple[float, ...]


def _normalize_embedding(values: Sequence[float]) -> tuple[float, ...]:
    if not values:
        raise ValueError("Embedding must not be empty.")

    normalized: list[float] = []
    for value in values:
        if not isinstance(value, (int, float)):
            raise ValueError("Embedding values must be numeric.")
        normalized.append(float(value))
    return tuple(normalized)


def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding dimensions must match.")

    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0

    dot = sum(left_value * right_value for left_value, right_value in zip(left, right))
    return dot / (left_norm * right_norm)


def _serialize_embedding(embedding: Sequence[float]) -> str:
    return json.dumps(_normalize_embedding(embedding), separators=(",", ":"))


def _deserialize_embedding(payload: str) -> tuple[float, ...]:
    raw = json.loads(payload)
    if not isinstance(raw, list):
        raise ValueError("Stored embedding payload must decode to a list.")
    return _normalize_embedding(raw)


def _derive_snippet_offset(content: str, query_text: str | None) -> dict[str, int] | None:
    if not query_text:
        return None

    lowered_content = content.lower()
    for token in query_text.lower().split():
        if len(token) < 3:
            continue
        start = lowered_content.find(token)
        if start != -1:
            return {"start": start, "end": start + len(token)}
    return None


class SQLiteExactIndex:
    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    path TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding_json TEXT NOT NULL,
                    embedding_dimensions INTEGER NOT NULL,
                    PRIMARY KEY (path, chunk_index)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chunks_path
                ON chunks (path)
                """
            )

    def upsert_chunks(self, chunks: Iterable[ChunkRecord]) -> int:
        rows: list[tuple[str, int, str, str, int]] = []
        for chunk in chunks:
            embedding = _normalize_embedding(chunk.embedding)
            rows.append(
                (
                    chunk.path,
                    chunk.chunk_index,
                    chunk.content,
                    _serialize_embedding(embedding),
                    len(embedding),
                )
            )

        if not rows:
            return 0

        self.initialize()
        with sqlite3.connect(self.db_path) as connection:
            connection.executemany(
                """
                INSERT INTO chunks (
                    path,
                    chunk_index,
                    content,
                    embedding_json,
                    embedding_dimensions
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(path, chunk_index) DO UPDATE SET
                    content = excluded.content,
                    embedding_json = excluded.embedding_json,
                    embedding_dimensions = excluded.embedding_dimensions
                """,
                rows,
            )
            return len(rows)

    def query(
        self,
        query_embedding: Sequence[float],
        *,
        limit: int,
        query_text: str | None = None,
        path_prefix: str | None = None,
        min_score: float = 0.0,
    ) -> list[dict]:
        if limit <= 0:
            raise ValueError("limit must be positive.")

        normalized_query = _normalize_embedding(query_embedding)
        results: list[tuple[float, str, int, str]] = []
        self.initialize()

        sql = (
            "SELECT path, chunk_index, content, embedding_json FROM chunks"
            " WHERE (? IS NULL OR path LIKE ?)"
        )
        params = (path_prefix, None if path_prefix is None else f"{path_prefix}%")

        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(sql, params).fetchall()

        for path, chunk_index, content, embedding_json in rows:
            embedding = _deserialize_embedding(embedding_json)
            score = _cosine_similarity(normalized_query, embedding)
            if score <= min_score:
                continue
            results.append((score, path, int(chunk_index), content))

        results.sort(key=lambda item: (-item[0], item[1], item[2]))
        ranked = []
        for score, path, chunk_index, content in results[:limit]:
            ranked.append(
                {
                    "path": path,
                    "chunk_index": chunk_index,
                    "content": content,
                    "score": score,
                    "snippet_offset": _derive_snippet_offset(content, query_text),
                }
            )
        return ranked

    def count_chunks(self) -> int:
        self.initialize()
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute("SELECT COUNT(*) FROM chunks").fetchone()
        return 0 if row is None else int(row[0])


def run_benchmark(
    db_path: Path | str,
    chunks: Sequence[ChunkRecord],
    query_embedding: Sequence[float],
    *,
    limit: int,
    query_text: str | None = None,
) -> dict:
    index = SQLiteExactIndex(db_path)

    started_at = time.perf_counter()
    inserted = index.upsert_chunks(chunks)
    build_seconds = time.perf_counter() - started_at

    started_at = time.perf_counter()
    results = index.query(
        query_embedding,
        limit=limit,
        query_text=query_text,
    )
    query_seconds = time.perf_counter() - started_at

    return {
        "database_path": str(Path(db_path)),
        "chunk_count": index.count_chunks(),
        "inserted_count": inserted,
        "limit": limit,
        "build_seconds": round(build_seconds, 6),
        "query_seconds": round(query_seconds, 6),
        "top_result": None if not results else {
            "path": results[0]["path"],
            "chunk_index": results[0]["chunk_index"],
            "score": round(results[0]["score"], 6),
        },
    }


def _load_fixture(path: Path) -> tuple[list[ChunkRecord], tuple[float, ...], int, str | None]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture must be a JSON object.")

    raw_chunks = payload.get("chunks")
    if not isinstance(raw_chunks, list) or not raw_chunks:
        raise ValueError("Fixture must include a non-empty 'chunks' array.")

    chunks = []
    for item in raw_chunks:
        if not isinstance(item, dict):
            raise ValueError("Each fixture chunk must be an object.")
        chunks.append(
            ChunkRecord(
                path=item["path"],
                chunk_index=int(item["chunk_index"]),
                content=item["content"],
                embedding=_normalize_embedding(item["embedding"]),
            )
        )

    limit = int(payload.get("limit", 5))
    query_text = payload.get("query_text")
    if query_text is not None and not isinstance(query_text, str):
        raise ValueError("'query_text' must be a string when present.")

    return chunks, _normalize_embedding(payload["query_embedding"]), limit, query_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark the SQLite exact retrieval baseline.",
    )
    parser.add_argument(
        "--db-path",
        required=True,
        help="SQLite database path for the retrieval artifact.",
    )
    parser.add_argument(
        "--fixture",
        required=True,
        help="JSON fixture with chunks and query_embedding.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    chunks, query_embedding, limit, query_text = _load_fixture(Path(args.fixture))
    result = run_benchmark(
        args.db_path,
        chunks,
        query_embedding,
        limit=limit,
        query_text=query_text,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
