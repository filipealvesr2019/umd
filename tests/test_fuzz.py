"""Property-based / fuzz tests for the parser and renderer.

The parser must never crash on arbitrary input: malformed documents are
reported through diagnostics, not exceptions.
"""

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from umd import Document, parse, render_document
from umd.core.validator import validate

# Printable text plus the characters that are meaningful to the UMD grammar.
UMD_ALPHABET = st.characters(
    blacklist_categories=("Cs",),
    blacklist_characters="\x00",
)
TEXT = st.text(alphabet=UMD_ALPHABET, max_size=200)

FUZZ_SETTINGS = settings(
    max_examples=60,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


@FUZZ_SETTINGS
@given(TEXT)
def test_parse_never_raises(text):
    result = parse(text)
    assert result is not None
    assert result.root is not None
    assert result.root.type == "document"


@FUZZ_SETTINGS
@given(TEXT)
def test_validate_never_raises(text):
    result = parse(text)
    diagnostics = validate(result.root)
    assert isinstance(diagnostics, list)


@FUZZ_SETTINGS
@given(TEXT)
def test_render_never_raises(text):
    html = render_document(text)
    assert isinstance(html, str)
    assert "<html" in html.lower()


@FUZZ_SETTINGS
@given(TEXT)
def test_document_wrapper_never_raises(text):
    doc = Document(text)
    assert isinstance(doc.valid, bool)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    assert doc.source() == normalized


@FUZZ_SETTINGS
@given(TEXT)
def test_parse_preserves_source_text(text):
    result = parse(text)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    assert result.text == normalized


@FUZZ_SETTINGS
@given(st.lists(st.text(alphabet=UMD_ALPHABET, max_size=40), max_size=5))
def test_paragraph_count_is_stable(paragraphs):
    source = "\n\n".join(
        line.replace("\\", "\\\\").replace("\n", " ") for line in paragraphs
    )
    first = parse(source)
    second = parse(first.text)
    assert len(first.root.children) == len(second.root.children)
    assert first.text == second.text
