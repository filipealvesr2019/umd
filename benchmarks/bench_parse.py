"""Parse/render benchmark for large UMD documents.

Usage:
    python benchmarks/bench_parse.py            # print a table
    python benchmarks/bench_parse.py --save     # also write baseline.json

The generated document mixes Markdown blocks, a table and a chart so the
measurement covers the common hot paths.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from umd import parse, render_document

BASELINE_PATH = Path(__file__).resolve().parent / "baseline.json"
SIZES = (100, 500, 1000, 2000)


def build_document(blocks: int) -> str:
    parts = ["# Benchmark Document"]
    for i in range(blocks):
        parts.append(f"## Section {i}")
        parts.append(f"Paragraph number {i} with **bold**, *italic* and `code`.")
        parts.append("- item one\n- item two\n- item three")
        if i % 50 == 0:
            parts.append("[TABLE title=\"Metrics\"]\nName | Value\nLatency | 12.5\n[/TABLE]")
        if i % 100 == 0:
            parts.append(
                '[CHART title="Scores" type="bar"]\n'
                "Alpha | 88.5\nBeta | 92.4\n[/CHART]"
            )
    return "\n\n".join(parts) + "\n"


def measure(text: str, rounds: int = 3) -> dict:
    timings = []
    for _ in range(rounds):
        start = time.perf_counter()
        result = parse(text)
        elapsed = (time.perf_counter() - start) * 1000
        timings.append(elapsed)

    start = time.perf_counter()
    render_document(text)
    render_ms = (time.perf_counter() - start) * 1000

    return {
        "lines": text.count("\n"),
        "chars": len(text),
        "parse_ms_best": round(min(timings), 2),
        "parse_ms_avg": round(sum(timings) / len(timings), 2),
        "render_ms": round(render_ms, 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark the UMD parser")
    parser.add_argument("--save", action="store_true", help="write baseline.json")
    args = parser.parse_args()

    results = {}
    print(f"{'lines':>8} {'chars':>9} {'parse best':>12} {'parse avg':>11} {'render':>9}")
    for blocks in SIZES:
        text = build_document(blocks)
        row = measure(text)
        results[str(blocks)] = row
        print(
            f"{row['lines']:>8} {row['chars']:>9} "
            f"{row['parse_ms_best']:>10} ms {row['parse_ms_avg']:>9} ms {row['render_ms']:>7} ms"
        )

    if args.save:
        BASELINE_PATH.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        print(f"\nBaseline written to {BASELINE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
