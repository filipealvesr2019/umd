"""Tema visual padrão do renderizador HTML (CSS puro, sem dependências)."""

CSS = """
:root {
  --umd-bg: #f4f6f9;
  --umd-surface: #ffffff;
  --umd-text: #171a21;
  --umd-muted: #5b6472;
  --umd-border: #e2e6ec;
  --umd-accent: #2563eb;
  --umd-radius: 12px;
  --tone: #4a5568;
  --tone-bg: #f4f6f9;
  --tone-border: #e2e6ec;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  padding: 40px 20px 64px;
  background: var(--umd-bg);
  color: var(--umd-text);
  font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  line-height: 1.62;
  -webkit-font-smoothing: antialiased;
}

.umd-document {
  max-width: 880px;
  margin: 0 auto;
  padding: 48px 52px 56px;
  background: var(--umd-surface);
  border: 1px solid var(--umd-border);
  border-radius: 16px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, .04), 0 12px 32px rgba(16, 24, 40, .06);
}

h1, h2, h3, h4, h5, h6 {
  margin: 1.5em 0 .55em;
  line-height: 1.25;
  letter-spacing: -.015em;
}

h1:first-child { margin-top: 0; }
h1 { font-size: 2.05rem; }
h2 { font-size: 1.3rem; padding-bottom: .3em; border-bottom: 1px solid var(--umd-border); }
h3 { font-size: 1.08rem; }

p { margin: .85em 0; }
p:first-child { margin-top: 0; }

a { color: var(--umd-accent); text-decoration: none; }
a:hover { text-decoration: underline; }

code {
  background: #eef1f6;
  padding: .15em .4em;
  border-radius: 6px;
  font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
  font-size: .88em;
}

pre {
  background: #14181f;
  color: #e6edf3;
  padding: 16px 18px;
  border-radius: 10px;
  overflow: auto;
  margin: 1.1em 0;
  font-size: .88rem;
}

pre code { background: none; padding: 0; color: inherit; }

blockquote {
  margin: 1.1em 0;
  padding: .15em 1.1em;
  border-left: 3px solid var(--umd-border);
  color: var(--umd-muted);
}

ul, ol { margin: .8em 0; padding-left: 1.4em; }
li { margin: .3em 0; }

hr { border: 0; border-top: 1px solid var(--umd-border); margin: 2em 0; }

/* ---------- tabela ---------- */

.umd-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.3em 0;
  font-variant-numeric: tabular-nums;
}

.umd-table caption {
  caption-side: top;
  text-align: left;
  padding: 0 0 10px;
  font-size: .76rem;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--umd-muted);
}

.umd-table th {
  text-align: left;
  padding: 10px 12px;
  font-size: .74rem;
  font-weight: 600;
  letter-spacing: .07em;
  text-transform: uppercase;
  color: var(--umd-muted);
  border-bottom: 1px solid var(--umd-border);
  white-space: nowrap;
}

.umd-table td {
  padding: 11px 12px;
  border-bottom: 1px solid var(--umd-border);
}

.umd-table tbody tr:last-child td { border-bottom: 0; }
.umd-table.striped tbody tr:nth-child(even) { background: #fafbfd; }
.umd-table.dense th, .umd-table.dense td { padding: 6px 10px; }

/* ---------- cartoes e colunas ---------- */

.umd-card {
  border: 1px solid var(--umd-border);
  border-top: 3px solid var(--tone);
  border-radius: var(--umd-radius);
  padding: 18px 20px 20px;
  background: var(--umd-surface);
}

.umd-card-title {
  margin: 0 0 .5em;
  font-size: .74rem;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--tone);
}

.umd-card > :last-child { margin-bottom: 0; }

.umd-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  margin: 1.3em 0;
}

/* ---------- callout ---------- */

.umd-callout {
  margin: 1.3em 0;
  padding: 14px 18px;
  border: 1px solid var(--tone-border);
  border-left: 4px solid var(--tone);
  border-radius: var(--umd-radius);
  background: var(--tone-bg);
}

.umd-callout-title {
  margin: 0 0 .3em;
  font-size: .78rem;
  font-weight: 700;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--tone);
}

.umd-callout > :last-child { margin-bottom: 0; }

/* ---------- imagem ---------- */

.umd-figure { margin: 1.3em 0; }
.umd-figure img { max-width: 100%; border-radius: 10px; display: block; }
.umd-figure figcaption {
  margin-top: .5em;
  font-size: .82rem;
  color: var(--umd-muted);
}

/* ---------- componente desconhecido ---------- */

/* ---------- chart, pipeline, progress ---------- */

.umd-chart {
  margin: 1.4em 0;
  padding: 16px 20px;
  background: var(--umd-surface);
  border: 1px solid var(--umd-border);
  border-radius: var(--umd-radius);
}
.umd-chart-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 12px;
}
.umd-chart-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 8px 0;
}
.umd-chart-label {
  width: 140px;
  font-size: 0.88rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.umd-chart-track {
  flex: 1;
  height: 10px;
  background: rgba(128, 128, 128, 0.15);
  border-radius: 999px;
  overflow: hidden;
}
.umd-chart-bar {
  height: 100%;
  background: linear-gradient(90deg, #38bdf8, #818cf8);
  border-radius: 999px;
}
.umd-chart-val {
  width: 50px;
  text-align: right;
  font-size: 0.88rem;
  font-weight: 600;
}

/* ---------- pie / donut ---------- */
.umd-pie-wrap {
  display: flex;
  align-items: center;
  gap: 28px;
  margin-top: 12px;
}
.umd-pie-visual {
  width: 130px;
  height: 130px;
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.umd-pie-hole {
  width: 65px;
  height: 65px;
  border-radius: 50%;
  background: var(--umd-surface);
}
.umd-pie-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}
.umd-pie-legend-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.88rem;
}
.umd-pie-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.umd-pie-legend-lbl {
  flex: 1;
}
.umd-pie-legend-val {
  font-weight: 600;
  color: var(--umd-muted);
}

/* ---------- column chart ---------- */
.umd-columns-flow {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  height: 160px;
  padding-top: 20px;
}
.umd-column-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}
.umd-column-val {
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 6px;
}
.umd-column-track {
  flex: 1;
  width: 24px;
  background: rgba(128, 128, 128, 0.1);
  border-radius: 6px 6px 0 0;
  display: flex;
  align-items: flex-end;
}
.umd-column-fill {
  width: 100%;
  border-radius: 6px 6px 0 0;
  transition: height 0.3s ease;
}
.umd-column-lbl {
  font-size: 0.8rem;
  margin-top: 8px;
  white-space: nowrap;
  color: var(--umd-muted);
}

/* ---------- line chart ---------- */
.umd-line-svg {
  width: 100%;
  height: 140px;
  overflow: visible;
}
.umd-line-x-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  color: var(--umd-muted);
  margin-top: 6px;
}

.umd-pipeline {
  margin: 1.4em 0;
  padding: 16px 20px;
  background: var(--umd-surface);
  border: 1px solid var(--umd-border);
  border-radius: var(--umd-radius);
}
.umd-pipeline-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 12px;
}
.umd-pipeline-flow {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
.umd-pipeline-node {
  padding: 6px 14px;
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 500;
}
.umd-pipeline-arrow {
  color: var(--umd-muted);
  font-size: 1.1rem;
}

.umd-progress-card {
  margin: 1.4em 0;
  padding: 14px 18px;
  background: var(--umd-surface);
  border: 1px solid var(--umd-border);
  border-radius: var(--umd-radius);
}
.umd-progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.umd-progress-label {
  font-size: 0.9rem;
  font-weight: 500;
}
.umd-progress-badge {
  font-size: 0.85rem;
  font-weight: 600;
  color: #38bdf8;
}
.umd-progress-track {
  height: 8px;
  background: rgba(128, 128, 128, 0.15);
  border-radius: 999px;
  overflow: hidden;
}
.umd-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #38bdf8, #818cf8);
  border-radius: 999px;
}

.umd-fallback {
  margin: 1.2em 0;
  padding: 14px 16px;
  border: 1px dashed var(--umd-border);
  border-radius: var(--umd-radius);
}

.umd-fallback-name {
  display: inline-block;
  margin-bottom: .5em;
  font-family: ui-monospace, Consolas, monospace;
  font-size: .74rem;
  color: var(--umd-muted);
}

/* ---------- tons ---------- */

.tone-neutral { --tone: #4a5568; --tone-bg: #f6f7f9; --tone-border: #e2e6ec; }
.tone-success { --tone: #0f7a5a; --tone-bg: #effaf5; --tone-border: #b9e6d3; }
.tone-warning { --tone: #a9600a; --tone-bg: #fff8ec; --tone-border: #f0d6a8; }
.tone-danger  { --tone: #b02a34; --tone-bg: #fdf2f3; --tone-border: #f2c4c7; }
.tone-info    { --tone: #1d5fbf; --tone-bg: #f1f6fe; --tone-border: #c3d7f5; }

@media (max-width: 640px) {
  body { padding: 16px 10px 32px; }
  .umd-document { padding: 28px 22px 32px; border-radius: 12px; }
  .umd-table { display: block; overflow-x: auto; white-space: nowrap; }
}
"""
