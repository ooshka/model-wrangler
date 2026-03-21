#!/usr/bin/env python3
"""Validate local retrieval and planner parity fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.ollama.smoke import run_planner_parity_fixture
from scripts.retrieval.sqlite_exact import run_retrieval_parity_fixture


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RETRIEVAL_FIXTURE = ROOT / "agent_docs" / "testing" / "local_retrieval_parity_fixture.json"
DEFAULT_PLANNER_FIXTURE = ROOT / "agent_docs" / "testing" / "planner_json_parity_fixture.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate the local provider parity fixture pack.",
    )
    parser.add_argument(
        "--db-path",
        default="/tmp/local_llm_parity.sqlite3",
        help="SQLite database path used for retrieval parity validation.",
    )
    parser.add_argument(
        "--retrieval-fixture",
        default=str(DEFAULT_RETRIEVAL_FIXTURE),
        help="Path to the retrieval parity fixture JSON.",
    )
    parser.add_argument(
        "--planner-fixture",
        default=str(DEFAULT_PLANNER_FIXTURE),
        help="Path to the planner parity fixture JSON.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        retrieval = run_retrieval_parity_fixture(args.db_path, args.retrieval_fixture)
        planner = run_planner_parity_fixture(args.planner_fixture)
    except (RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "parity-fixtures-passed",
                "retrieval": retrieval,
                "planner": planner,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
