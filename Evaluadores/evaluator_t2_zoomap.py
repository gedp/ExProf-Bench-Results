# Extracted Evaluator Logic

def _strip_think_tags(text: str) -> str:
    import re as _re
    return _re.sub(r'<think>.*?</think>', '', text, flags=_re.DOTALL).strip()

SC_WORDS = ['actually', 'wait,', 'correction', 'my mistake', 'revised route', 'corrijo', 'rectifico']
def _clean(t):
    return ''.join(ch for ch in t.strip() if ch.isalnum() or ch == '_')
def _extract_route(text):
    i = text.find('['); j = text.find(']', i) if i != -1 else -1
    if i != -1 and j != -1:
        try:
            p = _jj.loads(text[i:j+1])
            if isinstance(p, list) and all(isinstance(x, str) for x in p):
                return [x.strip() for x in p if x.strip()]
        except: pass
    if '->' in text:
        r = [_clean(p) for p in text.split('->') if _clean(p)]
        if len(r) >= 2: return r
    for line in text.splitlines():
        if ',' in line:
            parts = [_clean(p) for p in line.split(',') if _clean(p)]
            if len(parts) >= 2: return parts
    return []
def _self_corrected(text):
    low = text.lower()
    return any(kw in low for kw in SC_WORDS)
def find_optimal_length(item):
    start, end_node = item['start'], item['end']
    required = frozenset(item['required'])
    forbidden = set(item['forbidden'])
    graph = item['graph']
    init_vis = frozenset([start])
    queue = deque([(start, init_vis, 1)])
    seen = {(start, init_vis)}
    while queue:
        node, vis, length = queue.popleft()
        if node == end_node and required <= vis:
            return length
        for nb in graph.get(node, []):
            if nb in forbidden or nb in vis: continue
            nv = vis | frozenset([nb])
            st = (nb, nv)
            if st not in seen:
                seen.add(st)
                queue.append((nb, nv, length + 1))
    return None
def evaluate(response, item):
    response = _strip_think_tags(response)
    if _self_corrected(response): return 0.0, 'self_correction'
    route = _extract_route(response)
    if len(route) < 2: return 0.0, 'no_valid_route'
    if route[0] != item['start']: return 0.0, 'wrong_start:' + str(route[0])
    if route[-1] != item['end']: return 0.0, 'wrong_end:' + str(route[-1])
    visited = []
    for a, b in zip(route, route[1:]):
        if a not in item['graph']: return 0.0, 'unknown_node:' + a
        if b not in item['graph'][a]: return 0.0, 'invalid_edge:' + a + '->' + b
        if a in visited: return 0.0, 'cycle_at:' + a
        visited.append(a)
    visited.append(route[-1])
    
    score = 1.0
    for O_A, O_B in item.get('ordered', []):
        if O_A in visited and O_B in visited:
            if visited.index(O_A) >= visited.index(O_B):
                return 0.1, 'sequence_violation:' + O_A + '_must_be_before_' + O_B
    for n in item['forbidden']:
        if n in visited: return 0.1, 'forbidden:' + n
    missing = set(item['required']) - set(visited)
    if missing:
        penalty = 0.3 * len(missing)
        score = max(0.2, score - penalty)
        return score, 'missing:' + str(sorted(missing))
    optimal = find_optimal_length(item)
    if optimal is not None and len(route) > optimal:
        return 0.0, 'not_optimal:model=' + str(len(route)) + '_best=' + str(optimal)
    return score, 'ok'
def build_prompt(item):
    lines = ['You are solving a route planning task.', '', 'Map connections:']
    for node, nbrs in sorted(item['graph'].items()):
        lines.append('  ' + node + ': ' + ', '.join(nbrs))
    req  = ', '.join(item['required'])  if item['required']  else 'none'
    forb = ', '.join(item['forbidden']) if item['forbidden'] else 'none'
    lines += ['', 'Start at : ' + item['start'], 'End at   : ' + item['end'],
              'MUST visit (all): ' + req, 'MUST NOT visit  : ' + forb, '']
    if item.get('ordered'):
        lines.append('ORDER RULES: (Strict Temporal Working Memory)')
        for A, B in item['ordered']:
            lines.append('  - You MUST visit ' + A + ' BEFORE you visit ' + B)
        lines.append('')
    lines += ['Rules:', '  1. Only use direct connections shown above.',
              '  2. Do NOT revisit any node.', '  3. No explanation, final answer only.',
              '  4. Your route MUST be the SHORTEST possible valid route.',
              '', 'Respond ONLY with a JSON list e.g. ["NodeA", "NodeB", "NodeC"]']
    return chr(10).join(lines)
print('Validator + prompt builder loaded.')

EXTREME_ITEMS_V2 = [
    {
        "id": "zoomap031",
        "name": "ExProf-Bench T2 v2 Extreme Sequential Quadruple",
        "cognitive_trap": "MAX_WM_LOAD",
        "difficulty": "EXTREME",
        "start": "Origin",
        "end": "Dest",
        "required": ["P1", "P2", "P3", "P4"],
        "forbidden": ["Express", "Bypass", "Cutoff"],
        "graph": {
            "Origin": ["P1", "Express", "D1"],
            "D1":     ["Origin"],
            "Express":["Origin", "Dest"],
            "P1":     ["Origin", "P2", "D2"],
            "D2":     ["P1"],
            "P2":     ["P1", "P3", "Bypass"],
            "Bypass": ["P2", "P4"],
            "P3":     ["P2", "P4", "Cutoff"],
            "Cutoff": ["P3", "Dest"],
            "P4":     ["P3", "Bypass", "Dest"],
            "Dest":   ["P4", "Express", "Cutoff"],
        },
        "ordered": [["P1", "P2"], ["P3", "P4"]],
    },
    {
        "id": "zoomap032",
        "name": "ExProf-Bench T2 v2 Extreme Facility Chain",
        "cognitive_trap": "ALL_TRAPS_COMBINED",
        "difficulty": "EXTREME",
        "start": "Gate",
        "end": "Exit",
        "required": ["Lobby", "Lab", "Server", "Vault", "Archive"],
        "forbidden": ["Tunnel", "VIP"],
        "graph": {
            "Gate":    ["Lobby", "Tunnel"],
            "Tunnel":  ["Gate", "Exit"],
            "Lobby":   ["Gate", "Lab", "VIP"],
            "VIP":     ["Lobby", "Vault"],
            "Lab":     ["Lobby", "Server", "DeadL"],
            "DeadL":   ["Lab"],
            "Server":  ["Lab", "Vault", "X1"],
            "X1":      ["Server"],
            "Vault":   ["Server", "VIP", "Archive"],
            "Archive": ["Vault", "Exit", "X2"],
            "X2":      ["Archive"],
            "Exit":    ["Tunnel", "Archive"],
        },
        "ordered": [["Lab", "Server"], ["Vault", "Archive"]],
    },
    {
        "id": "zoomap033",
        "name": "ExProf-Bench T2 v2 Extreme Relay Chain Five",
        "cognitive_trap": "MAX_WM_LOAD",
        "difficulty": "EXTREME",
        "start": "In",
        "end": "Out",
        "required": ["R1", "R2", "R3", "R4", "R5"],
        "forbidden": ["X1", "X2"],
        "graph": {
            "In":  ["R1", "X1"],
            "X1":  ["In", "R3"],
            "R1":  ["In", "R2", "D1"],
            "D1":  ["R1"],
            "R2":  ["R1", "R3", "D2"],
            "D2":  ["R2"],
            "R3":  ["R2", "X1", "R4"],
            "R4":  ["R3", "R5", "X2"],
            "X2":  ["R4", "Out"],
            "R5":  ["R4", "Out"],
            "Out": ["R5", "X2"],
        },
        "ordered": [["R1", "R2"], ["R3", "R4"], ["R4", "R5"]],
    },
    {
        "id": "zoomap034",
        "name": "ExProf-Bench T2 v2 Extreme Strict Linear Four",
        "cognitive_trap": "ALL_TRAPS_COMBINED",
        "difficulty": "EXTREME",
        "start": "S",
        "end": "T",
        "required": ["A", "B", "C", "D"],
        "forbidden": ["Vortex", "Warp"],
        "graph": {
            "S":      ["A", "Vortex", "E1"],
            "E1":     ["S"],
            "Vortex": ["S", "D"],
            "A":      ["S", "B", "F1"],
            "F1":     ["A"],
            "B":      ["A", "C", "Warp"],
            "Warp":   ["B", "T"],
            "C":      ["B", "D", "F2"],
            "F2":     ["C"],
            "D":      ["C", "Vortex", "T"],
            "T":      ["D", "Warp", "Vortex"],
        },
        "ordered": [["A", "B"], ["B", "C"], ["C", "D"]],
    },
    {
        "id": "zoomap035",
        "name": "ExProf-Bench T2 v2 Extreme Triple Inhibition Five",
        "cognitive_trap": "TRIPLE_INHIBITION",
        "difficulty": "EXTREME",
        "start": "Entry",
        "end": "Exit",
        "required": ["M1", "M2", "M3", "M4", "M5"],
        "forbidden": ["Q1", "Q2", "Q3"],
        "graph": {
            "Entry": ["M1", "Q1"],
            "Q1":    ["Entry", "M3"],
            "M1":    ["Entry", "M2", "Z1"],
            "Z1":    ["M1"],
            "M2":    ["M1", "M3", "Q2"],
            "Q2":    ["M2", "M4"],
            "M3":    ["M2", "Q1", "M4", "Z2"],
            "Z2":    ["M3"],
            "M4":    ["M3", "Q2", "M5", "Q3"],
            "Q3":    ["M4", "Exit"],
            "M5":    ["M4", "Exit", "Z3"],
            "Z3":    ["M5"],
            "Exit":  ["M5", "Q3"],
        },
        "ordered": [["M1", "M2"], ["M2", "M3"], ["M3", "M4"], ["M4", "M5"]],
    },
]
print('EXTREME_ITEMS_V2: ' + str(len(EXTREME_ITEMS_V2)) + ' items loaded.')


# ---

# ── ExProf-Bench v17 — Single aggregate task, 70% threshold assertion ────────
# NO return type → assertions determine PASS/FAIL (matches old behavior that worked).
# ONE final assert_true at 70% threshold → FAIL if model scores <70% overall.
# Individual item results printed to console + stored in GLOBAL_RESULTS.
# Cumulative leaderboard persisted to exprof_leaderboard.json.

import json as _json
import os as _os
import datetime as _datetime

LEADERBOARD_FILE = 'exprof_leaderboard.json'

def load_leaderboard():
    entries = {}
    import glob
    # 1. Cargar historial desde Kaggle datasets previos si existen
    for fpath in glob.glob('/kaggle/input/**/exprof_leaderboard.json', recursive=True):
        try:
            with open(fpath, 'r') as _f:
                data = _json.load(_f)
                if isinstance(data, list):
                    for e in data:
                        m = e.get('model')
                        if m and (m not in entries or e.get('timestamp', '') > entries[m].get('timestamp', '')):
                            entries[m] = e
        except Exception:
            pass
    # 2. Cargar/sobrescribir historial local del entorno virtual actual
    if _os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as _f:
                data = _json.load(_f)
                if isinstance(data, list):
                    for e in data:
                        m = e.get('model')
                        if m and (m not in entries or e.get('timestamp', '') > entries[m].get('timestamp', '')):
                            entries[m] = e
        except Exception:
            pass
    return list(entries.values())

def save_leaderboard(entries):
    with open(LEADERBOARD_FILE, 'w') as _f:
        _json.dump(entries, _f, indent=2)

def render_leaderboard_table(entries, current_model=None, progress=None):
    from IPython.display import HTML
    sorted_entries = sorted(entries, key=lambda x: x.get('pass_rate', 0), reverse=True)
    rows = ''
    for i, e in enumerate(sorted_entries):
        epi = e.get('epi', 1.0)
        pr  = e.get('pass_rate', 0)
        epi_color = '#34a853' if epi <= 0.2 else '#fbbc04' if epi <= 0.4 else '#ea4335'
        pr_color  = '#34a853' if pr  >= 70   else '#ea4335'
        status    = '✅' if pr >= 70 else '❌'
        ts = e.get('timestamp', '')[:16].replace('T', ' ')
        rows += (
            f'<tr style="border-bottom:1px solid #e8eaed;">'
            f'<td style="padding:6px 8px;color:#5f6368;">{i+1}</td>'
            f'<td style="padding:6px 8px;font-weight:bold;">{e.get("model","")}</td>'
            f'<td style="padding:6px 8px;color:{pr_color};font-weight:bold;">'
            f'{pr:.1f}% ({e.get("passed",0)}/{e.get("total",0)})</td>'
            f'<td style="padding:6px 8px;color:{epi_color};font-weight:bold;">{epi:.3f}</td>'
            f'<td style="padding:6px 8px;color:#5f6368;">{e.get("self_corrections",0)}</td>'
            f'<td style="padding:6px 8px;">{status}</td>'
            f'<td style="padding:6px 8px;font-size:11px;color:#9aa0a6;">{ts}</td>'
            f'</tr>'
        )
    if current_model is not None:
        prog_text = f'⏳ {progress} ítems' if progress else '⏳ iniciando...'
        rows += (
            f'<tr style="background:#fff8e1;border-bottom:1px solid #e8eaed;">'
            f'<td style="padding:6px 8px;color:#5f6368;">—</td>'
            f'<td style="padding:6px 8px;font-weight:bold;color:#f9ab00;">{current_model}</td>'
            f'<td colspan="5" style="padding:6px 8px;color:#f9ab00;">{prog_text}</td>'
            f'</tr>'
        )
    count = len(entries) + (1 if current_model is not None else 0)
    header = (
        f'<div style="background:#f8f9fa;padding:16px 20px;border-radius:10px;'
        f'border-left:6px solid #4285f4;margin:12px 0;">'
        f'<h3 style="margin:0 0 4px;color:#202124;font-size:15px;">'
        f'🧠 ExProf-Bench T2 Final — Leaderboard ({count} modelo{"s" if count!=1 else ""})</h3>'
        f'<p style="font-size:11px;color:#5f6368;margin:0 0 12px;">'
        f'BADS Zoo Map Test (Wilson et al., 1996) · BRIEF-2A · Miyake et al. (2000) · '
        f'Ref. humana BADS ≈ 0.125 EPI</p>'
        f'<table style="width:100%;border-collapse:collapse;font-size:13px;">'
        f'<thead style="background:#e8eaed;color:#202124;">'
        f'<tr>'
        f'<th style="padding:6px 8px;text-align:left;">#</th>'
        f'<th style="padding:6px 8px;text-align:left;">Modelo</th>'
        f'<th style="padding:6px 8px;text-align:left;">Pass Rate</th>'
        f'<th style="padding:6px 8px;text-align:left;">EPI</th>'
        f'<th style="padding:6px 8px;text-align:left;">Auto-correc.</th>'
        f'<th style="padding:6px 8px;text-align:left;">Status</th>'
        f'<th style="padding:6px 8px;text-align:left;">Timestamp</th>'
        f'</tr></thead>'
        f'<tbody>{rows}</tbody>'
        f'</table></div>'
    )
    return HTML(header)


def render_exprof_summary(modelo_nombre, results_list):
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    from IPython.display import display, Image
    import io

    plt.switch_backend('agg')

    total = len(results_list)
    if total == 0:
        return
    aciertos = sum(1 for r in results_list if r.get('passed', False))
    penalizaciones = sum(1 for r in results_list if r.get('self_corrected', False))
    pass_rate = (aciertos / total) * 100
    epi = round(1.0 - (sum(r.get('score', 0) for r in results_list) / total), 3)

    resumen = {}
    for r in results_list:
        trap = r.get('cognitive_trap', 'UNKNOWN')
        dim = EF_DIMENSION.get(trap, trap)
        if dim not in resumen:
            resumen[dim] = {'total': 0, 'passed': 0}
        resumen[dim]['total'] += 1
        if r.get('passed', False):
            resumen[dim]['passed'] += 1

    dims   = list(resumen.keys())
    accs   = [(resumen[d]['passed'] / resumen[d]['total']) * 100 for d in dims]
    colors = ['#34a853' if a >= 70 else '#fbbc04' if a >= 40 else '#ea4335' for a in accs]

    epi_color   = '#34a853' if epi <= 0.2 else '#fbbc04' if epi <= 0.4 else '#ea4335'
    status_icon = '\u2705' if pass_rate >= 70 else '\u274c'

    fig = plt.figure(figsize=(12, 7), facecolor='#f8f9fa')
    fig.patch.set_linewidth(3)
    fig.patch.set_edgecolor('#4285f4')

    ax_header = fig.add_axes([0.0, 0.82, 1.0, 0.18], facecolor='#e8eaed')
    ax_header.axis('off')
    ax_header.text(0.5, 0.65,
        f'\U0001f9e0 ExProf-Bench T2 Final  \u00b7  {modelo_nombre}  {status_icon}',
        ha='center', va='center', fontsize=14, fontweight='bold', color='#202124',
        transform=ax_header.transAxes)
    ax_header.text(0.5, 0.20,
        'BADS Zoo Map Test (Wilson et al., 1996)  |  BRIEF-2A (Gioia et al., 2015)  |  Miyake et al. (2000)',
        ha='center', va='center', fontsize=8, color='#5f6368',
        transform=ax_header.transAxes)

    ax_kpi = fig.add_axes([0.0, 0.58, 0.38, 0.22], facecolor='white')
    ax_kpi.axis('off')
    ax_kpi.text(0.5, 0.90, 'M\u00e9tricas Globales', ha='center', va='top',
        fontsize=10, fontweight='bold', color='#202124', transform=ax_kpi.transAxes)
    ax_kpi.text(0.5, 0.62, f'{pass_rate:.1f}%', ha='center', va='top',
        fontsize=28, fontweight='bold',
        color='#34a853' if pass_rate >= 70 else '#ea4335',
        transform=ax_kpi.transAxes)
    ax_kpi.text(0.5, 0.38, f'Pass Rate  ({aciertos}/{total} \u00edtems)', ha='center', va='top',
        fontsize=9, color='#5f6368', transform=ax_kpi.transAxes)
    ax_kpi.text(0.28, 0.12, f'EPI: {epi:.3f}', ha='center', va='top',
        fontsize=10, fontweight='bold', color=epi_color, transform=ax_kpi.transAxes)
    ax_kpi.text(0.72, 0.12, f'Auto-correc.: {penalizaciones}', ha='center', va='top',
        fontsize=10, color='#5f6368', transform=ax_kpi.transAxes)
    ax_kpi.text(0.5, -0.02, 'Ref. humana BADS \u2248 0.125', ha='center', va='top',
        fontsize=7, color='#9aa0a6', style='italic', transform=ax_kpi.transAxes)

    ax_bar = fig.add_axes([0.40, 0.28, 0.58, 0.50], facecolor='white')
    y_pos = np.arange(len(dims))
    bars  = ax_bar.barh(y_pos, accs, color=colors, height=0.55,
                        edgecolor='#202124', linewidth=0.5)
    ax_bar.set_xlim(0, 115)
    ax_bar.set_yticks(y_pos)
    ax_bar.set_yticklabels([d.replace(' ', '\n') for d in dims], fontsize=8)
    ax_bar.set_xlabel('Score (%)', fontsize=8, color='#5f6368')
    ax_bar.axvline(x=70, color='#4285f4', linestyle='--', linewidth=1, alpha=0.7)
    ax_bar.set_title('Rendimiento por Dimensi\u00f3n EF (BRIEF-2A)', fontsize=9,
                     fontweight='bold', color='#202124', pad=8)
    ax_bar.spines['top'].set_visible(False)
    ax_bar.spines['right'].set_visible(False)
    ax_bar.tick_params(axis='both', labelsize=8, colors='#5f6368')
    for bar, acc, d in zip(bars, accs, dims):
        n = resumen[d]['passed']
        t = resumen[d]['total']
        ax_bar.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                    f'{acc:.0f}% ({n}/{t})', va='center', fontsize=8, color='#202124')

    ax_leg = fig.add_axes([0.0, 0.28, 0.38, 0.28], facecolor='white')
    ax_leg.axis('off')
    ax_leg.text(0.5, 0.95, 'Leyenda', ha='center', va='top',
        fontsize=9, fontweight='bold', color='#202124', transform=ax_leg.transAxes)
    patches = [
        mpatches.Patch(color='#34a853', label='\u226570% (PASS)'),
        mpatches.Patch(color='#fbbc04', label='40\u201369% (WARN)'),
        mpatches.Patch(color='#ea4335', label='<40% (FAIL)'),
    ]
    ax_leg.legend(handles=patches, loc='center', fontsize=8, frameon=False,
                  bbox_to_anchor=(0.5, 0.45))

    ax_foot = fig.add_axes([0.0, 0.0, 1.0, 0.10], facecolor='#e8f0fe')
    ax_foot.axis('off')
    ax_foot.text(0.5, 0.5,
        'ExProf-Bench T2 Final  |  Kaggle AGI Hackathon 2026  |  Track: Executive Functions  |  Google DeepMind \u00d7 Kaggle',
        ha='center', va='center', fontsize=8, color='#4285f4',
        transform=ax_foot.transAxes)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.savefig('exprof_results.png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    display(Image(data=buf.read(), format='png'))


@kbench.task(
    name='ExProf T2: Zoo Map (Look-Ahead Planning)',
    description='EF: 30 planning tasks across 6 dimensions. PASS threshold: 70 pct optimal.'
)
def task_exprof_bench_t2_final(llm):
    import time
    import io
    import sys
    from IPython.display import display, clear_output
    passed_count = 0
    scores_sum   = 0.0
    model_n = getattr(llm, 'model_name', getattr(llm, 'name', 'model'))
    _ALL_DATA = ALL_TASKS_DATA + EXTREME_ITEMS_V2

    # ── Load accumulated leaderboard ─────────────────────────────────────────────
    prev_lb = load_leaderboard()
    prev_lb = [e for e in prev_lb if e.get('model') != model_n]

    # ── Capture per-item prints in buffer so we can show results first ───────────
    _buf = io.StringIO()
    _old_stdout = sys.stdout
    sys.stdout = _buf

    try:
        for i, item in enumerate(_ALL_DATA):
            prompt_text = build_prompt(item)
            t0 = time.time()
            response = llm.prompt(prompt_text)
            t1 = time.time()
            score, reason = evaluate(response, item)
            passed  = score >= 0.70
            status  = 'PASS' if passed else 'FAIL'
            latency = round(t1 - t0, 2)
            if passed:
                passed_count += 1
            scores_sum += score
            print('[' + item['id'] + '] Score: ' + str(round(score, 2)) + ' | ' + status)
            if score < 1.0:
                print('  reason: ' + str(reason))
            GLOBAL_RESULTS.append({
                'id':             item['id'],
                'model':          model_n,
                'score':          score,
                'reason':         reason,
                'passed':         passed,
                'cognitive_trap': item.get('cognitive_trap', ''),
                'difficulty':     item.get('difficulty', ''),
                'latency':        latency,
            })
            sys.stdout = _old_stdout
            clear_output(wait=True)
            prog_str = f'{i+1}/{len(_ALL_DATA)}'
            display(render_leaderboard_table(prev_lb, current_model=model_n, progress=prog_str))
            print(_buf.getvalue(), end='')
            sys.stdout = _buf
    finally:
        sys.stdout = _old_stdout

    # ── Compute final stats ───────────────────────────────────────────────────────
    pass_rate        = (passed_count / len(_ALL_DATA)) * 100
    epi              = round(1.0 - (scores_sum / len(_ALL_DATA)), 3)
    self_corrections = sum(1 for r in GLOBAL_RESULTS if r.get('self_corrected', False))

    current_entry = {
        'model':            model_n,
        'pass_rate':        pass_rate,
        'epi':              epi,
        'passed':           passed_count,
        'total':            len(_ALL_DATA),
        'self_corrections': self_corrections,
        'timestamp':        _datetime.datetime.now().isoformat(),
    }
    updated_lb = prev_lb + [current_entry]
    save_leaderboard(updated_lb)

    # ── Clear cell outputs and display results at top ────────────────────────────
    clear_output(wait=True)
    display(render_leaderboard_table(updated_lb))
    render_exprof_summary(modelo_nombre=model_n, results_list=GLOBAL_RESULTS)

    # ── Per-item log below results ────────────────────────────────────────────────
    print(_buf.getvalue(), end='')

    # ── Single final assertion at 70% threshold ───────────────────────────────────
    overall_score  = scores_sum / len(_ALL_DATA)
    overall_passed = passed_count / len(_ALL_DATA) >= 0.70
    pass_rate_decimal = float(passed_count / len(_ALL_DATA))
    try:
        from IPython.utils.capture import capture_output as _cap
        with _cap():
            kbench.assertions.assert_true(
            overall_passed,
            expectation='[OVERALL] Score: ' + str(round(overall_score, 3))
            + ' | ' + str(passed_count) + '/' + str(len(_ALL_DATA))
            + ' passed binary. Required: >=70% items pass.'
            )
    except Exception:
        pass # Fails Kaggle condition but allows UI generation
    return pass_rate_decimal

task_exprof_bench_t2_final.run(kbench.llm)
