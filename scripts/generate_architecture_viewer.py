#!/usr/bin/env python3
"""Génère le viewer HTML Architecture Lab — state + I/O par nœud du graphe."""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.personas.benchmark_architectures import (
    export_csv,
    export_json,
    run_architecture_benchmark_with_traces,
)
from show.personas.trace import export_traces_json

OUT = ROOT / "docs" / "product"

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>V.TV — Graph Trace Lab</title>
  <style>
    :root {
      --bg: #05080f;
      --panel: #0c121c;
      --panel2: #111a28;
      --line: #1c2738;
      --ink: #e8edf5;
      --dim: #8b95a8;
      --faint: #5a6478;
      --blue: #4da3ff;
      --coral: #ff6257;
      --gold: #e5b54d;
      --mind: #9b7aff;
      --mint: #00ffd1;
      --mod: #ffb347;
      --mono: "JetBrains Mono", Consolas, monospace;
      --sans: "Segoe UI", system-ui, sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: var(--sans);
      background: radial-gradient(ellipse 120% 80% at 50% -20%, #141e30 0%, var(--bg) 55%);
      color: var(--ink);
      min-height: 100vh;
    }
    header {
      position: sticky; top: 0; z-index: 20;
      padding: 14px 20px;
      border-bottom: 1px solid var(--line);
      background: rgba(5,8,15,0.92);
      backdrop-filter: blur(8px);
      display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;
    }
    header h1 { margin: 0; font-size: 1.1rem; letter-spacing: 0.1em; }
    .sub { color: var(--dim); font-size: 0.82rem; }
    .badge {
      font-size: 0.65rem; font-weight: 700; letter-spacing: 0.14em;
      padding: 5px 10px; border-radius: 4px;
      background: rgba(0,255,209,0.1); color: var(--mint); border: 1px solid rgba(0,255,209,0.35);
    }
    .shell {
      display: grid;
      grid-template-columns: 260px 1fr;
      min-height: calc(100vh - 58px);
    }
    aside {
      border-right: 1px solid var(--line);
      background: rgba(12,18,28,0.7);
      overflow-y: auto;
    }
    .arch {
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      cursor: pointer;
      transition: background 0.12s;
    }
    .arch:hover, .arch.on { background: rgba(77,163,255,0.09); }
    .arch.on { border-left: 3px solid var(--gold); }
    .arch-rank { color: var(--gold); font-weight: 700; font-size: 0.78rem; margin-right: 6px; }
    .arch-title { font-weight: 600; font-size: 0.9rem; }
    .arch-meta { color: var(--faint); font-size: 0.72rem; margin-top: 3px; }
    main { overflow-y: auto; padding: 16px 20px 48px; }
    .toolbar {
      display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
      margin-bottom: 14px;
    }
    .chip {
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--dim);
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 0.75rem;
      cursor: pointer;
      transition: all 0.12s;
    }
    .chip.on { color: var(--ink); border-color: var(--blue); background: rgba(77,163,255,0.12); }
    .chip.guest-a.on { border-color: var(--coral); background: rgba(255,98,87,0.12); }
    .chip.guest-b.on { border-color: var(--blue); background: rgba(77,163,255,0.12); }
    .metrics {
      display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px;
    }
    .metric {
      background: var(--panel); border: 1px solid var(--line);
      border-radius: 6px; padding: 8px 12px; min-width: 90px;
    }
    .metric label { display: block; font-size: 0.62rem; color: var(--faint); letter-spacing: 0.1em; }
    .metric strong { font-size: 1rem; color: var(--gold); }
    .flow-bar {
      display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 18px;
      padding: 10px; background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
    }
    .flow-node {
      font-family: var(--mono); font-size: 0.68rem;
      padding: 4px 8px; border-radius: 4px;
      border: 1px solid var(--line); background: var(--panel2);
      cursor: pointer; color: var(--dim);
    }
    .flow-node:hover { border-color: var(--mint); color: var(--ink); }
    .flow-node.hit { border-color: var(--gold); color: var(--gold); }
    .flow-arrow { color: var(--faint); align-self: center; font-size: 0.7rem; }
    .section-title {
      font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase;
      color: var(--faint); margin: 20px 0 10px;
    }
    .step-card {
      border: 1px solid var(--line);
      border-radius: 10px;
      margin-bottom: 14px;
      overflow: hidden;
      background: var(--panel);
      scroll-margin-top: 80px;
    }
    .step-card.hidden { display: none; }
    .step-head {
      display: flex; align-items: center; gap: 10px;
      padding: 10px 14px;
      background: rgba(0,0,0,0.2);
      border-bottom: 1px solid var(--line);
      cursor: pointer;
    }
    .step-idx {
      font-family: var(--mono); font-size: 0.72rem;
      color: var(--mint); min-width: 2rem;
    }
    .step-name { font-weight: 600; font-size: 0.88rem; flex: 1; }
    .step-agent {
      font-size: 0.68rem; padding: 2px 8px; border-radius: 3px;
      font-weight: 700; letter-spacing: 0.06em;
    }
    .agent-guest_a { background: rgba(255,98,87,0.18); color: var(--coral); }
    .agent-guest_b { background: rgba(77,163,255,0.18); color: var(--blue); }
    .agent-moderator { background: rgba(255,179,71,0.18); color: var(--mod); }
    .step-body { display: none; padding: 0; }
    .step-card.open .step-body { display: block; }
    .io-grid {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 0;
    }
    @media (max-width: 1200px) { .io-grid { grid-template-columns: 1fr; } .shell { grid-template-columns: 1fr; } aside { max-height: 200px; } }
    .io-col {
      border-right: 1px solid var(--line);
      min-height: 120px;
    }
    .io-col:last-child { border-right: none; }
    .io-col h4 {
      margin: 0; padding: 8px 12px;
      font-size: 0.65rem; letter-spacing: 0.12em;
      text-transform: uppercase; color: var(--faint);
      border-bottom: 1px solid var(--line);
      background: rgba(0,0,0,0.15);
    }
    .io-col.input h4 { color: var(--blue); }
    .io-col.llm h4 { color: var(--mind); }
    .io-col.output h4 { color: var(--mint); }
    .json-block {
      margin: 0; padding: 10px 12px;
      font-family: var(--mono); font-size: 0.72rem; line-height: 1.45;
      color: var(--dim); white-space: pre-wrap; word-break: break-word;
      max-height: 320px; overflow: auto;
    }
    .llm-block {
      border-bottom: 1px solid var(--line);
      padding: 10px 12px;
    }
    .llm-block:last-child { border-bottom: none; }
    .llm-phase {
      display: inline-block; font-size: 0.62rem; font-weight: 700;
      letter-spacing: 0.08em; text-transform: uppercase;
      padding: 2px 7px; border-radius: 3px;
      background: rgba(155,122,255,0.2); color: var(--mind);
      margin-bottom: 6px;
    }
    .llm-label { font-size: 0.62rem; color: var(--faint); margin: 6px 0 2px; letter-spacing: 0.08em; }
    .llm-text {
      font-family: var(--mono); font-size: 0.7rem; line-height: 1.4;
      color: var(--dim); white-space: pre-wrap; word-break: break-word;
      background: rgba(0,0,0,0.25); padding: 8px; border-radius: 4px;
      max-height: 160px; overflow: auto;
    }
    .state-panels { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    @media (max-width: 900px) { .state-panels { grid-template-columns: 1fr; } }
    .state-panel {
      border: 1px solid var(--line); border-radius: 8px; overflow: hidden;
      background: var(--panel);
    }
    .state-panel h3 {
      margin: 0; padding: 10px 12px;
      font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase;
      color: var(--faint); border-bottom: 1px solid var(--line);
    }
    .empty { color: var(--faint); font-style: italic; padding: 12px; font-size: 0.82rem; }
    .source { color: var(--blue); font-size: 0.78rem; text-decoration: none; }
    .source:hover { text-decoration: underline; }
    .chevron { color: var(--faint); font-size: 0.8rem; transition: transform 0.15s; }
    .step-card.open .chevron { transform: rotate(90deg); }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>V.TV — GRAPH TRACE LAB</h1>
      <div class="sub" id="hdr-sub">Chargement…</div>
    </div>
    <span class="badge">STATE · I/O · LLM</span>
  </header>
  <div class="shell">
    <aside id="arch-list"></aside>
    <main id="main"></main>
  </div>
  <script>
    const TRACES = __TRACES_JSON__;
    const archList = document.getElementById('arch-list');
    const main = document.getElementById('main');
    const hdrSub = document.getElementById('hdr-sub');
    let current = null;
    let agentFilter = 'all';
    let openSteps = new Set();

    function esc(s) {
      if (s == null) return '';
      return String(s)
        .replace(/&/g,'&amp;').replace(/</g,'&lt;')
        .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    function pretty(obj) {
      if (!obj || (typeof obj === 'object' && !Object.keys(obj).length)) return '—';
      return esc(JSON.stringify(obj, null, 2));
    }

    function agentClass(id) {
      if (id === 'guest_a') return 'agent-guest_a';
      if (id === 'guest_b') return 'agent-guest_b';
      return 'agent-moderator';
    }

    function renderLlmCalls(calls) {
      if (!calls || !calls.length) return '<p class="empty">Pas d\'appel LLM sur cette étape</p>';
      return calls.map((c, i) => `
        <div class="llm-block">
          <span class="llm-phase">${esc(c.phase)} #${i+1}</span>
          <div class="llm-label">SYSTEM</div>
          <div class="llm-text">${esc(c.system)}</div>
          <div class="llm-label">USER</div>
          <div class="llm-text">${esc(c.user)}</div>
          <div class="llm-label">RESPONSE</div>
          <div class="llm-text" style="color:var(--ink)">${esc(c.response)}</div>
        </div>
      `).join('');
    }

    function renderStep(step) {
      const open = openSteps.has(step.index);
      return `
        <article class="step-card ${open ? 'open' : ''}" id="step-${step.index}" data-agent="${esc(step.agent)}">
          <div class="step-head" onclick="toggleStep(${step.index})">
            <span class="step-idx">#${step.index}</span>
            <span class="step-name">${esc(step.label)} <code style="color:var(--faint);font-size:0.75rem">${esc(step.step)}</code></span>
            <span class="step-agent ${agentClass(step.agent)}">${esc(step.agent_name)}</span>
            <span class="chevron">▶</span>
          </div>
          <div class="step-body">
            <div class="io-grid">
              <div class="io-col input">
                <h4>Input — turn · mind · show</h4>
                <pre class="json-block"><b style="color:var(--faint)">// turn</b>
${pretty(step.input_turn)}

<b style="color:var(--faint)">// mind</b>
${pretty(step.input_mind)}

<b style="color:var(--faint)">// show</b>
${pretty(step.input_show)}</pre>
              </div>
              <div class="io-col llm">
                <h4>LLM I/O (${(step.llm_calls||[]).length})</h4>
                ${renderLlmCalls(step.llm_calls)}
              </div>
              <div class="io-col output">
                <h4>Output — delta nœud</h4>
                <pre class="json-block">${pretty(step.output)}</pre>
              </div>
            </div>
          </div>
        </article>
      `;
    }

    window.toggleStep = function(idx) {
      if (openSteps.has(idx)) openSteps.delete(idx);
      else openSteps.add(idx);
      const el = document.getElementById('step-' + idx);
      if (el) el.classList.toggle('open');
    };

    window.scrollToStep = function(idx) {
      openSteps.add(idx);
      renderMain();
      const el = document.getElementById('step-' + idx);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    function filteredPipeline(t) {
      const pipe = t.pipeline || [];
      if (agentFilter === 'all') return pipe;
      return pipe.filter(s => s.agent === agentFilter);
    }

    function renderMain() {
      if (!current) return;
      const t = current;
      const pipe = filteredPipeline(t);
      const seq = (t.cognitive_sequence || '').split('→');

      const agentChips = (t.agents || []).map(a => `
        <button class="chip ${a.id === 'guest_a' ? 'guest-a' : a.id === 'guest_b' ? 'guest-b' : ''} ${agentFilter === a.id ? 'on' : ''}"
          onclick="setAgent('${esc(a.id)}')">${esc(a.name)}</button>
      `).join('');

      const flowNodes = pipe.map((s, i) => {
        const arrow = i < pipe.length - 1 ? '<span class="flow-arrow">→</span>' : '';
        return `<span class="flow-node" onclick="scrollToStep(${s.index})" title="${esc(s.agent_name)}">${esc(s.step)}</span>${arrow}`;
      }).join('');

      const topology = seq.map(s => `<span class="flow-node" style="cursor:default;opacity:0.7">${esc(s)}</span><span class="flow-arrow">→</span>`).join('')
        .replace(/<span class="flow-arrow">→<\/span>$/, '');

      main.innerHTML = `
        <h2 style="margin:0 0 4px">${esc(t.architecture_name)}</h2>
        <a class="source" href="${esc(t.reference)}" target="_blank">${esc(t.source)}</a>
        <div class="metrics" style="margin-top:12px">
          <div class="metric"><label>SCORE</label><strong>${t.quality_score.toFixed(3)}</strong></div>
          <div class="metric"><label>ÉTAPES</label><strong>${(t.pipeline||[]).length}</strong></div>
          <div class="metric"><label>LLM TOTAL</label><strong>${(t.llm_calls||[]).length}</strong></div>
          <div class="metric"><label>TENSION</label><strong>${t.tension_final}</strong></div>
          <div class="metric"><label>ANTENNE</label><strong style="font-size:0.75rem;color:var(--coral)">${esc((t.on_air_response||'').slice(0,40))}…</strong></div>
        </div>
        <div class="section-title">Topologie architecture</div>
        <div class="flow-bar">${topology || '<span class="empty">—</span>'}</div>
        <div class="toolbar">
          <span style="font-size:0.72rem;color:var(--faint);margin-right:4px">FILTRE AGENT</span>
          <button class="chip ${agentFilter === 'all' ? 'on' : ''}" onclick="setAgent('all')">Tous</button>
          ${agentChips}
        </div>
        <div class="section-title">Pipeline exécuté (${pipe.length} nœuds)</div>
        <div class="flow-bar">${flowNodes || '<span class="empty">Aucune étape</span>'}</div>
        <div class="section-title">I/O par étape — cliquez pour déplier</div>
        ${pipe.length ? pipe.map(renderStep).join('') : '<p class="empty">Aucune trace step_io</p>'}
        <div class="section-title">ShowState global</div>
        <div class="state-panels">
          <div class="state-panel">
            <h3>État initial</h3>
            <pre class="json-block">${pretty(t.show_initial)}</pre>
          </div>
          <div class="state-panel">
            <h3>État final</h3>
            <pre class="json-block">${pretty(t.show_final)}</pre>
          </div>
        </div>
      `;
    }

    window.setAgent = function(id) {
      agentFilter = id;
      renderMain();
    };

    function selectTrace(i) {
      current = TRACES[i];
      openSteps = new Set([1]);
      document.querySelectorAll('.arch').forEach((n, j) => n.classList.toggle('on', j === i));
      renderMain();
    }

    if (TRACES.length) {
      const t0 = TRACES[0];
      hdrSub.textContent = `${t0.persona_name} · ${t0.personality} × ${t0.domain} · « ${t0.topic} »`;
    }

    TRACES.forEach((t, i) => {
      const el = document.createElement('div');
      el.className = 'arch' + (i === 0 ? ' on' : '');
      el.innerHTML = `
        <span class="arch-rank">#${t.rank}</span>
        <span class="arch-title">${esc(t.architecture_name)}</span>
        <div class="arch-meta">${(t.pipeline||[]).length} étapes · ${(t.llm_calls||[]).length} LLM · score ${t.quality_score.toFixed(3)}</div>
      `;
      el.onclick = () => selectTrace(i);
      archList.appendChild(el);
    });

    if (TRACES.length) selectTrace(0);
  </script>
</body>
</html>
"""


def generate_html(traces: list, path: Path) -> Path:
    payload = json.dumps([asdict(t) for t in traces], ensure_ascii=False)
    html = HTML_TEMPLATE.replace("__TRACES_JSON__", payload)
    path.write_text(html, encoding="utf-8")
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=OUT,
        help="Directory for HTML/CSV/JSON outputs (default: docs/product)",
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
    html_path = out / "architecture_lab.html"
    traces_path = out / "architecture_traces.json"

    rows, traces = run_architecture_benchmark_with_traces()
    export_csv(rows, out / "architecture_benchmark.csv")
    export_json(rows, out / "architecture_benchmark.json")
    export_traces_json(traces, traces_path)
    generate_html(traces, html_path)
    print(f"Viewer : {html_path}")
    print(f"Traces : {traces_path}")
    if not args.no_open:
        webbrowser.open(html_path.as_uri())


if __name__ == "__main__":
    main()
