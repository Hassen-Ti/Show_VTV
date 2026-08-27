#!/usr/bin/env python3
"""Viewer HTML — Philosophe réflexif × 10 questions, tous les outputs."""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.personas.reflection_lab import export_philosopher_json, run_philosopher_lab

OUT = ROOT / "docs" / "product"
HTML_PATH = OUT / "philosopher_reflection_lab.html"
JSON_PATH = OUT / "philosopher_reflection_traces.json"

HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>V.TV — Philosophe Réflexif</title>
  <style>
    :root {
      --bg: #060a12; --panel: #0d1420; --panel2: #121c2c;
      --line: #1e2a3c; --ink: #eef2f8; --dim: #8a94a8; --faint: #5c6678;
      --violet: #a78bfa; --mint: #34d399; --gold: #fbbf24; --blue: #60a5fa;
      --mono: "JetBrains Mono", Consolas, monospace;
      --sans: "Segoe UI", system-ui, sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; font-family: var(--sans);
      background: radial-gradient(ellipse 100% 60% at 50% -10%, #1a1040 0%, var(--bg) 50%);
      color: var(--ink); min-height: 100vh;
    }
    header {
      position: sticky; top: 0; z-index: 10;
      padding: 14px 20px; border-bottom: 1px solid var(--line);
      background: rgba(6,10,18,0.94); backdrop-filter: blur(8px);
    }
    header h1 { margin: 0; font-size: 1.05rem; letter-spacing: 0.1em; }
    .sub { color: var(--dim); font-size: 0.8rem; margin-top: 4px; }
    .shell { display: grid; grid-template-columns: 300px 1fr; min-height: calc(100vh - 70px); }
    aside { border-right: 1px solid var(--line); overflow-y: auto; background: rgba(13,20,32,0.8); }
    .q-item {
      padding: 12px 14px; border-bottom: 1px solid var(--line);
      cursor: pointer; transition: background 0.12s;
    }
    .q-item:hover, .q-item.on { background: rgba(167,139,250,0.1); }
    .q-item.on { border-left: 3px solid var(--violet); }
    .q-num { color: var(--violet); font-weight: 700; font-size: 0.75rem; }
    .q-preview { font-size: 0.82rem; line-height: 1.35; margin-top: 4px; color: var(--dim); }
    main { padding: 18px 22px 60px; overflow-y: auto; }
    .question-block {
      font-size: 1.15rem; line-height: 1.5; color: var(--gold);
      border-left: 4px solid var(--gold);
      padding: 12px 16px; margin-bottom: 20px;
      background: rgba(251,191,36,0.06); border-radius: 0 8px 8px 0;
    }
    .response-block {
      font-size: 1.05rem; line-height: 1.65;
      padding: 18px 20px; margin-bottom: 20px;
      background: var(--panel); border: 1px solid var(--line);
      border-radius: 10px; border-left: 4px solid var(--mint);
    }
    .response-label, .section-label {
      font-size: 0.65rem; letter-spacing: 0.14em; text-transform: uppercase;
      color: var(--faint); margin-bottom: 8px;
    }
    .monologue {
      font-style: italic; color: var(--violet);
      padding: 14px 16px; margin-bottom: 20px;
      background: rgba(167,139,250,0.08); border-radius: 8px;
      border: 1px solid rgba(167,139,250,0.25);
    }
    .outputs-grid {
      display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px;
    }
    @media (max-width: 900px) { .outputs-grid { grid-template-columns: 1fr; } .shell { grid-template-columns: 1fr; } aside { max-height: 180px; } }
    .out-card {
      background: var(--panel); border: 1px solid var(--line);
      border-radius: 8px; overflow: hidden;
    }
    .out-card h3 {
      margin: 0; padding: 8px 12px; font-size: 0.65rem;
      letter-spacing: 0.12em; text-transform: uppercase;
      color: var(--faint); border-bottom: 1px solid var(--line);
    }
    pre.json {
      margin: 0; padding: 12px; font-family: var(--mono); font-size: 0.72rem;
      line-height: 1.45; color: var(--dim); white-space: pre-wrap;
      word-break: break-word; max-height: 280px; overflow: auto;
    }
    .step {
      border: 1px solid var(--line); border-radius: 8px;
      margin-bottom: 10px; overflow: hidden; background: var(--panel);
    }
    .step-head {
      padding: 10px 14px; cursor: pointer; display: flex; gap: 10px; align-items: center;
      background: rgba(0,0,0,0.2); border-bottom: 1px solid transparent;
    }
    .step.open .step-head { border-bottom-color: var(--line); }
    .step-idx { font-family: var(--mono); font-size: 0.72rem; color: var(--mint); }
    .step-name { flex: 1; font-weight: 600; font-size: 0.86rem; }
    .step-body { display: none; }
    .step.open .step-body { display: grid; grid-template-columns: 1fr 1fr 1fr; }
    @media (max-width: 1100px) { .step.open .step-body { grid-template-columns: 1fr; } }
    .col { border-right: 1px solid var(--line); }
    .col:last-child { border-right: none; }
    .col h4 {
      margin: 0; padding: 7px 10px; font-size: 0.62rem;
      letter-spacing: 0.1em; text-transform: uppercase; color: var(--faint);
      border-bottom: 1px solid var(--line);
    }
    .col.in h4 { color: var(--blue); }
    .col.llm h4 { color: var(--violet); }
    .col.out h4 { color: var(--mint); }
    .llm-row { padding: 10px; border-bottom: 1px solid var(--line); }
    .llm-phase {
      font-size: 0.6rem; font-weight: 700; color: var(--violet);
      letter-spacing: 0.08em; text-transform: uppercase;
    }
    .llm-txt {
      font-family: var(--mono); font-size: 0.68rem; color: var(--dim);
      white-space: pre-wrap; margin-top: 4px; max-height: 120px; overflow: auto;
      background: rgba(0,0,0,0.2); padding: 6px; border-radius: 4px;
    }
    .resp-txt { color: var(--ink); }
    .meta { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
    .pill {
      font-size: 0.72rem; padding: 4px 10px; border-radius: 12px;
      border: 1px solid var(--line); color: var(--dim);
    }
  </style>
</head>
<body>
  <header>
    <h1>PHILOSOPHE RÉFLEXIF — LAB RÉFLEXION</h1>
    <div class="sub" id="sub">10 questions · architecture Reflexion · sans débat</div>
  </header>
  <div class="shell">
    <aside id="q-list"></aside>
    <main id="main"></main>
  </div>
  <script>
    const LAB = __LAB_JSON__;
    const qList = document.getElementById('q-list');
    const main = document.getElementById('main');
    let cur = 0;
    const openSteps = new Set([1]);

    function esc(s) {
      if (s == null) return '';
      return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }
    function j(obj) {
      if (!obj || !Object.keys(obj).length) return '—';
      return esc(JSON.stringify(obj, null, 2));
    }

    function llmBlock(calls) {
      if (!calls || !calls.length) return '<p style="padding:10px;color:var(--faint);font-size:0.8rem">—</p>';
      return calls.map((c,i) => `
        <div class="llm-row">
          <div class="llm-phase">${esc(c.phase)} #${i+1}</div>
          <div style="font-size:0.6rem;color:var(--faint);margin-top:4px">SYSTEM</div>
          <div class="llm-txt">${esc(c.system)}</div>
          <div style="font-size:0.6rem;color:var(--faint);margin-top:4px">USER</div>
          <div class="llm-txt">${esc(c.user)}</div>
          <div style="font-size:0.6rem;color:var(--faint);margin-top:4px">RESPONSE</div>
          <div class="llm-txt resp-txt">${esc(c.response)}</div>
        </div>
      `).join('');
    }

    function stepCard(s) {
      const open = openSteps.has(s.index);
      return `
        <div class="step ${open?'open':''}" id="s-${s.index}">
          <div class="step-head" onclick="tog(${s.index})">
            <span class="step-idx">#${s.index}</span>
            <span class="step-name">${esc(s.label)} <code style="color:var(--faint)">${esc(s.step)}</code></span>
            <span style="color:var(--faint);font-size:0.75rem">${(s.llm_calls||[]).length} LLM</span>
          </div>
          <div class="step-body">
            <div class="col in"><h4>Input state</h4><pre class="json">// turn\n${j(s.input_turn)}\n\n// mind\n${j(s.input_mind)}\n\n// show\n${j(s.input_show)}</pre></div>
            <div class="col llm"><h4>LLM I/O</h4>${llmBlock(s.llm_calls)}</div>
            <div class="col out"><h4>Output delta</h4><pre class="json">${j(s.output)}</pre></div>
          </div>
        </div>
      `;
    }

    window.tog = function(i) {
      openSteps.has(i) ? openSteps.delete(i) : openSteps.add(i);
      document.getElementById('s-'+i)?.classList.toggle('open');
    };

    function render(i) {
      const q = LAB.questions[i];
      main.innerHTML = `
        <div class="meta">
          <span class="pill">${esc(LAB.persona_name)}</span>
          <span class="pill">${esc(LAB.architecture_id)}</span>
          <span class="pill">${esc(LAB.cognitive_sequence)}</span>
          <span class="pill">${(q.pipeline||[]).length} étapes · ${(q.llm_calls||[]).length} LLM</span>
        </div>
        <div class="response-label">Question ${q.question_id}</div>
        <div class="question-block">${esc(q.question)}</div>
        <div class="response-label">Réponse finale (deliver)</div>
        <div class="response-block">${esc(q.final_response) || '<em style="color:var(--faint)">—</em>'}</div>
        <div class="response-label">Monologue intérieur</div>
        <div class="monologue">${esc(q.inner_monologue) || '—'}</div>
        <div class="section-label">Tous les outputs agrégés</div>
        <div class="outputs-grid">
          <div class="out-card"><h3>Par étape (par_etape)</h3><pre class="json">${j(q.all_outputs?.par_etape)}</pre></div>
          <div class="out-card"><h3>Tour final (tour_final)</h3><pre class="json">${j(q.all_outputs?.tour_final || q.turn_final)}</pre></div>
          <div class="out-card"><h3>État mental (mind_final)</h3><pre class="json">${j(q.mind_final)}</pre></div>
          <div class="out-card"><h3>ShowState final</h3><pre class="json">${j(q.show_final)}</pre></div>
        </div>
        <div class="section-label">Pipeline — I/O par nœud (${(q.pipeline||[]).length})</div>
        ${(q.pipeline||[]).map(stepCard).join('') || '<p style="color:var(--faint)">—</p>'}
      `;
    }

    function pick(i) {
      cur = i;
      openSteps.clear(); openSteps.add(1);
      document.querySelectorAll('.q-item').forEach((el,j) => el.classList.toggle('on', j===i));
      render(i);
    }

    document.getElementById('sub').textContent =
      `${LAB.persona_name} · ${LAB.personality} × ${LAB.domain} · ${LAB.architecture_id} · ${LAB.questions.length} questions`;

    LAB.questions.forEach((q, i) => {
      const el = document.createElement('div');
      el.className = 'q-item' + (i===0?' on':'');
      el.innerHTML = `<div class="q-num">Q${q.question_id}</div><div class="q-preview">${esc(q.question)}</div>`;
      el.onclick = () => pick(i);
      qList.appendChild(el);
    });
    pick(0);
  </script>
</body>
</html>
"""


def generate_html(lab, path: Path) -> Path:
    payload = json.dumps(asdict(lab), ensure_ascii=False)
    path.write_text(HTML.replace("__LAB_JSON__", payload), encoding="utf-8")
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=OUT,
        help="Directory for HTML/JSON outputs (default: docs/product)",
    )
    p.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the generated HTML in a browser",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    html_path = out / "philosopher_reflection_lab.html"
    json_path = out / "philosopher_reflection_traces.json"

    lab = run_philosopher_lab()
    export_philosopher_json(lab, json_path)
    generate_html(lab, html_path)
    print(f"Viewer : {html_path}")
    print(f"Traces : {json_path}")
    if not args.no_open:
        webbrowser.open(html_path.as_uri())


if __name__ == "__main__":
    main()
