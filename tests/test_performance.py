"""Performance guardrails for the parser.

Thresholds are deliberately generous (they only catch pathological
regressions in CI, not micro-optimizations). Baseline numbers live in
``benchmarks/baseline.json`` and can be refreshed with
``python benchmarks/bench_parse.py --save``.
"""

import time

from umd import parse

SMALL_DOC = "# Title\n\nParagraph with **bold** and `code`.\n" * 100
LARGE_DOC = SMALL_DOC * 20


def _timed_parse(text: str) -> float:
    start = time.perf_counter()
    parse(text)
    return (time.perf_counter() - start) * 1000


def test_parse_small_document_under_budget():
    elapsed = _timed_parse(SMALL_DOC)
    assert elapsed < 1000, f"parsing a small document took {elapsed:.1f} ms"


def test_parse_large_document_under_budget():
    elapsed = _timed_parse(LARGE_DOC)
    assert elapsed < 5000, f"parsing a large document took {elapsed:.1f} ms"


def test_parse_does_not_scale_quadratically():
    small = _timed_parse(SMALL_DOC)
    large = _timed_parse(LARGE_DOC)
    assert large < small * 60, f"large/small ratio is {large / max(small, 0.01):.1f}x"
