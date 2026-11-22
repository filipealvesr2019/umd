"""Tests for AI-agent features: Report builder (all editor elements & inline styles),
umd spec, install-skill, umd check --json, umd outline --json, and surgical edits.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from umd import Document, Report, bold, inline_code, italic, strike, styled, underline
from umd.agent_kit import (
    UMD_SPEC,
    add_table_row,
    append_chart_row,
    install_skill,
    set_metric,
)
from umd.cli import main as cli_main


def test_report_builder_all_elements_and_text_styles():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "relatorio_completo.umd"
        styled_line = (
            f"{bold('Bold')} {italic('Italic')} {underline('Under')} {strike('Old')} "
            f"{inline_code('code()')} "
            f"{styled('Highlight', color='#ef4444', size=18, font='mono', spacing='1px', bold=True)}"
        )
        r = (
            Report("Experimento 132", "Resumo automático")
            .h2("Texto e Formatação")
            .h3("Subseção 3")
            .h4("Subseção 4")
            .p(styled_line)
            .p("Parágrafo estilizado", color="#38bdf8", size="16px", font="serif")
            .quote("Citação importante")
            .divider()
            .bullets(["Item A", "Item B"])
            .numbers(["Primeiro", "Segundo"])
            .checklist([("Treino concluído", True), ("Avaliação OOD", False)])
            .toggle("Detalhes técnicos", "Conteúdo recolhido dentro do toggle.")
            .cards([
                ("TRAIN Exatas", "18/20", "90.0%"),
                ("HELD Exatas", "6/8", "75.0%"),
            ])
            .card("Card Solo", "42", "extra", tone="info")
            .bar_chart("Horizontal", [("A", 88.5), ("B", 92.4)])
            .column_chart("Vertical", [("2k", 14.2), ("8k", 22.8)])
            .pie_chart("Pizza", [("Code", 35), ("Papers", 25)])
            .line_chart("Linha", [("E1", [0.8, 0.9]), ("E2", [0.85, 0.92])], series=["Train", "Val"])
            .curved_chart("Curva", [("E1", [1.0, 0.7]), ("E2", [0.4, 0.3])], series=["Loss", "Val"])
            .comparison_chart(
                "Acurácia por Regime (%)",
                [("TRAIN", [82.0, 90.0]), ("HELD", [62.5, 75.0])],
                series=["Exp 131", "Exp 132"],
            )
            .pipeline(["Input", "Encoder", "Verifier", "Output"], title="Pipeline")
            .progress("Stage 2", 85, max_value=100)
            .table(["Seed", "Regime", "Score"], [["130", "HELD01", "84.6%"]])
            .code("[ESPERADO]\nUse TestCase com setUpTestData...", lang="text")
            .code("def f(x):\n    return x + 1", lang="python")
            .callout("Baixa intrusão em HELD.", tone="warning", title="Diagnóstico")
            .image("https://example.com/plot.png", alt="Plot", caption="Figura 1", width=640)
            .tasks([("Validar checkpoint", True)], title="Checklist")
        )
        r.save(out)

        text = out.read_text(encoding="utf-8")
        doc = Document(text)
        assert doc.valid, f"Unexpected diagnostics: {doc.diagnostics}"
        assert 'type="bar"' in text
        assert 'type="column"' in text
        assert 'type="pie"' in text
        assert 'type="line"' in text
        assert 'type="curved"' in text
        assert 'type="comparison"' in text
        assert "<details>\n<summary>Detalhes técnicos</summary>" in text
        assert "font-size:18px" in text
        assert "color:#ef4444" in text
        assert "<u>Under</u>" in text
        assert "~~Old~~" in text
        assert "[IMAGE " in text
        assert "[TASKS " in text


def test_cli_check_json_catches_chart_and_unclosed_errors(capsys):
    with tempfile.TemporaryDirectory() as td:
        bad = Path(td) / "broken.umd"
        bad.write_text(
            '[CHART title="Bad" type="bar"]\nModel A | not_a_number\n[/CHART]\n',
            encoding="utf-8",
        )
        code = cli_main(["check", str(bad), "--json"])
        assert code == 1
        payload = json.loads(capsys.readouterr().out)
        assert payload["valid"] is False
        assert payload["error_count"] >= 1
        codes = {d["code"] for d in payload["diagnostics"]}
        assert "E_CHART_NON_NUMERIC" in codes
        assert all(d.get("hint") for d in payload["diagnostics"])


def test_cli_spec_and_install_skill(capsys):
    assert cli_main(["spec"]) == 0
    out = capsys.readouterr().out
    assert "[CHART" in out and "from umd.builder import Report" in out
    assert len(UMD_SPEC) > 200

    with tempfile.TemporaryDirectory() as td:
        skill_dir = Path(td) / "custom_skill"
        written = install_skill(skill_dir)
        assert len(written) == 1
        assert (skill_dir / "SKILL.md").exists()
        content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        assert content.startswith("---\nname: umd\n")


def test_outline_and_surgical_edits(capsys):
    with tempfile.TemporaryDirectory() as td:
        doc_path = Path(td) / "exp.umd"
        (
            Report("Exp 132")
            .cards([("TRAIN", "18/20"), ("HELD", "6/8")])
            .progress("Epoch", 40, max_value=100)
            .bar_chart("Scores", [("Exp 131", 80.5)])
            .table(["Seed", "Score"], [["130", "84.6%"]])
            .save(doc_path)
        )

        # 1. Outline JSON
        assert cli_main(["outline", str(doc_path), "--json"]) == 0
        outline = json.loads(capsys.readouterr().out)
        kinds = [item["kind"] for item in outline["items"]]
        assert "h1" in kinds
        assert "card" in kinds
        assert "progress" in kinds
        assert "chart" in kinds
        assert "table" in kinds

        # 2. Surgical add-row on Markdown table
        ok, msg, _ = add_table_row(doc_path, 1, ["131|88.2%"], write=True)
        assert ok, msg
        assert "| 131 | 88.2% |" in doc_path.read_text(encoding="utf-8")

        # 3. Surgical set-metric on CARD and PROGRESS
        ok, msg, _ = set_metric(doc_path, "HELD", "7/8", subtitle="87.5%", write=True)
        assert ok, msg
        assert "7/8\n87.5%" in doc_path.read_text(encoding="utf-8")

        ok, msg, _ = set_metric(doc_path, "Epoch", "100", write=True)
        assert ok, msg
        assert 'value="100"' in doc_path.read_text(encoding="utf-8")

        # 4. Surgical append-chart
        ok, msg, _ = append_chart_row(doc_path, "Scores", ["Exp 132|91.2"], write=True)
        assert ok, msg
        final_text = doc_path.read_text(encoding="utf-8")
        assert "Exp 132 | 91.2" in final_text

        # 5. Resulting file is still 100% valid
        assert Document(final_text).valid
