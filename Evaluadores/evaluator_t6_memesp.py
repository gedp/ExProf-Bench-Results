# Extracted Evaluator Logic

# ── T6 Multi-Axis Evaluator ──────────────────────────────────────────────────
import re as _re, json as _json

_SELF_CORRECT_WORDS = [
    'actually', 'wait,', 'correction', 'my mistake', 'revised',
    'corrijo', 'rectifico', 'let me reconsider', 'on second thought',
    'i made an error', 'i was wrong',
]

def _normalize_zone(z):
    return _re.sub(r'[^a-z0-9]', '', z.lower().strip())

def _parse_t6_response(response):
    result = {'zones': [], 'tally': None, 'tally_b': None, 'raw_ok': False}

    # Step 1: unwrap markdown code blocks  ```json ... ```  or  ``` ... ```
    raw = _re.sub(r'```(?:json)?\s*', '', response)
    raw = raw.replace('```', '')

    # Step 2: replace unfilled template placeholders with JSON null
    # Models sometimes return the format string literally: "final_tally": <integer>
    raw = _re.sub(r'<(?:integer|number|int|num)>', 'null', raw)

    # Step 3: find the outermost { ... } block
    bs = raw.find('{')
    be = raw.rfind('}')
    if bs != -1 and be > bs:
        try:
            blob = _json.loads(raw[bs:be+1])
            result['raw_ok'] = True

            # Extract visited zones list
            if 'visited_zones' in blob and isinstance(blob['visited_zones'], list):
                result['zones'] = [str(z).strip() for z in blob['visited_zones']]

            # Extract primary tally (counter_a / final_tally)
            for key in ['final_tally', 'counter_a', 'arithmetic_answer']:
                val = blob.get(key)
                if val is not None:
                    try:
                        result['tally'] = int(val)
                        break
                    except (ValueError, TypeError):
                        pass

            # Extract secondary tally (counter_b)
            val_b = blob.get('counter_b')
            if val_b is not None:
                try:
                    result['tally_b'] = int(val_b)
                except (ValueError, TypeError):
                    pass

        except Exception:
            # JSON parse failed — try to salvage visited_zones from text
            result['raw_ok'] = False
            # Look for a list pattern ["Zone", ...]
            list_match = _re.search(r'\[([^\]]+)\]', raw)
            if list_match:
                items = _re.findall(r'"([^"]+)"', list_match.group(1))
                if items:
                    result['zones'] = items
            # Try to extract the last standalone integer as a tally
            nums = _re.findall(r'(?<![\d])-?\d+(?![\d])', raw)
            if nums:
                try:
                    result['tally'] = int(nums[-1])
                except Exception:
                    pass
    else:
        # No JSON block at all — treat as plain text, salvage what we can
        list_match = _re.search(r'\[([^\]]+)\]', raw)
        if list_match:
            items = _re.findall(r'"([^"]+)"', list_match.group(1))
            if items:
                result['zones'] = items
        nums = _re.findall(r'(?<![\d])-?\d+(?![\d])', raw)
        if nums:
            try:
                result['tally'] = int(nums[-1])
            except Exception:
                pass
    return result

def evaluate_t6(response, item):
    axes = {'spatial': 0.0, 'arithmetic': 0.0, 'robustness': 0.0}
    if any(kw in response.lower() for kw in _SELF_CORRECT_WORDS):
        return 0.0, 'self_correction', axes
    parsed = _parse_t6_response(response)
    if not parsed['raw_ok'] and not parsed['zones']:
        return 0.0, 'unparseable_response', axes
    axes['robustness'] = 1.0 if parsed['raw_ok'] else 0.5

    # ── Spatial accuracy ──────────────────────────────────────────────────────
    gt_zones = item['excluded_zones']
    aliases  = item.get('zone_aliases', {})
    norm_to_canonical = {}
    for canonical in gt_zones:
        norm_to_canonical[_normalize_zone(canonical)] = canonical
    for canonical, alias_list in aliases.items():
        for alias in alias_list:
            norm_to_canonical[_normalize_zone(alias)] = canonical

    matched_canonicals = set()
    false_positives = 0
    for mz in parsed['zones']:
        norm_mz = _normalize_zone(mz)
        if norm_mz in norm_to_canonical:
            matched_canonicals.add(norm_to_canonical[norm_mz])
        else:
            false_positives += 1

    n_gt = len(gt_zones)
    recall    = len(matched_canonicals) / n_gt if n_gt > 0 else 0.0
    precision = (len(matched_canonicals) / (len(matched_canonicals) + false_positives)
                 if (len(matched_canonicals) + false_positives) > 0 else 0.0)
    if recall + precision > 0:
        axes['spatial'] = 2 * recall * precision / (recall + precision)
    missing = set(gt_zones) - matched_canonicals
    extra   = false_positives

    # ── Arithmetic accuracy ───────────────────────────────────────────────────
    has_dual = item.get('arithmetic_answer_b') is not None
    gt_a     = item['arithmetic_answer']
    gt_b     = item.get('arithmetic_answer_b')

    if has_dual:
        if parsed['tally'] is not None and parsed['tally_b'] is not None:
            a_ok = (parsed['tally']   == gt_a)
            b_ok = (parsed['tally_b'] == gt_b)
            axes['arithmetic'] = 1.0 if (a_ok and b_ok) else (0.5 if (a_ok or b_ok) else 0.0)
        elif parsed['tally'] is not None:
            axes['arithmetic'] = 0.25
        else:
            axes['arithmetic'] = 0.0
    else:
        if parsed['tally'] is not None:
            if parsed['tally'] == gt_a:
                axes['arithmetic'] = 1.0
            elif abs(parsed['tally'] - gt_a) <= 1:
                axes['arithmetic'] = 0.5
            else:
                axes['arithmetic'] = 0.0

    score = round(0.50 * axes['spatial']
                + 0.40 * axes['arithmetic']
                + 0.10 * axes['robustness'], 4)

    reason_parts = []
    if missing:
        reason_parts.append('missing_zones:' + str(sorted(missing)[:2]))
    if extra > 0:
        reason_parts.append('false_positives:' + str(extra))
    if has_dual:
        a_str = str(parsed['tally'])  if parsed['tally']   is not None else '?'
        b_str = str(parsed['tally_b']) if parsed['tally_b'] is not None else '?'
        reason_parts.append('counters:got(' + a_str + ',' + b_str + ')_expected(' + str(gt_a) + ',' + str(gt_b) + ')')
    else:
        tally_str = str(parsed['tally']) if parsed['tally'] is not None else '?'
        reason_parts.append('tally:got_' + tally_str + '_expected_' + str(gt_a))
    reason = ' | '.join(reason_parts) if reason_parts else 'ok'
    return score, reason, axes

def build_t6_prompt(item):
    lines = [
        'You are evaluating a spatial memory task under cognitive load.',
        '',
        'Read the following scenario carefully. You must track:',
        '  (A) Every physical location visited (INCLUDING transit/passage areas).',
        '  (B) A numerical running tally described in the text.',
        '',
        'Important rules:',
        '  - Include transit corridors if the agent physically walked through them.',
        '  - Do NOT include locations only seen/observed but not physically entered.',
        '  - If two names refer to the SAME location, count it as ONE location.',
        '  - Do NOT revisit a count if the narrative says it was revisited but NOT re-counted.',
        '',
        '--- SCENARIO ---',
        item['context'],
        '--- END SCENARIO ---',
        '',
        item['question'],
    ]
    return '\n'.join(lines)

print('T6 evaluator and prompt builder ready.')
print('Axes: Spatial(50%) | Arithmetic(40%) | Robustness(10%) | PASS threshold: 0.70')




# ---

# ── ExProf-Bench T6 — MemEsp-Dual Evaluation Task ───────────────────────────
# v18 display engine: results pinned at TOP via display_id handles.

import json as _json, os as _os, datetime as _datetime

T6_LEADERBOARD_FILE = 'exprof_t6_mesp_leaderboard.json'

def _load_lb():
    if _os.path.exists(T6_LEADERBOARD_FILE):
        try:
            with open(T6_LEADERBOARD_FILE) as _f: return _json.load(_f)
        except: return []
    return []

def _save_lb(entries):
    with open(T6_LEADERBOARD_FILE, 'w') as _f: _json.dump(entries, _f, indent=2)

def _render_t6_lb(entries, current_model=None, progress=None):
    from IPython.display import HTML
    sorted_e = sorted(entries, key=lambda x: x.get('avg_score',0), reverse=True)
    rows = ''
    for i, e in enumerate(sorted_e):
        pr   = e.get('pass_rate', 0)
        sp   = e.get('avg_spatial', 0)
        ar   = e.get('avg_arithmetic', 0)
        epi  = e.get('epi', 1.0)
        pc   = '#34a853' if pr >= 70 else '#ea4335'
        ep_c = '#34a853' if epi <= 0.2 else '#fbbc04' if epi <= 0.4 else '#ea4335'
        ts   = e.get('timestamp','')[:16].replace('T',' ')
        rows += (
            f'<tr style="border-bottom:1px solid #e8eaed;">'
            f'<td style="padding:6px 8px;color:#5f6368;">{i+1}</td>'
            f'<td style="padding:6px 8px;font-weight:bold;">{e.get("model","")}</td>'
            f'<td style="padding:6px 8px;color:{pc};font-weight:bold;">{pr/100:.2f}</td>'
            f'<td style="padding:6px 8px;color:#4285f4;">{sp:.2f}</td>'
            f'<td style="padding:6px 8px;color:#34a853;">{ar:.2f}</td>'
            f'<td style="padding:6px 8px;color:{ep_c};font-weight:bold;">{epi:.3f}</td>'
            f''
            f'<td style="padding:6px 8px;font-size:10px;color:#9aa0a6;">{ts}</td>'
            f'</tr>'
        )
    if current_model:
        prog_txt = f'⏳ {progress}' if progress else '⏳ iniciando...'
        rows += (
            f'<tr style="background:#fff8e1;">'
            f'<td style="padding:6px;">—</td>'
            f'<td style="padding:6px;font-weight:bold;color:#f9ab00;">{current_model}</td>'
            f'<td colspan="6" style="padding:6px;color:#f9ab00;">{prog_txt}</td>'
            f'</tr>'
        )
    cnt = len(entries) + (1 if current_model else 0)
    return HTML(
        f'<div style="background:#f8f9fa;padding:16px;border-radius:10px;border-left:6px solid #4285f4;margin:8px 0;">'
        f'<h3 style="margin:0 0 4px;color:#202124;font-size:15px;">🧩 ExProf-Bench T6 MemEsp-Dual — Leaderboard ({cnt} modelo{"s" if cnt!=1 else ""})</h3>'
        f'<p style="font-size:11px;color:#5f6368;margin:0 0 10px;">CANTAB-SWM · Narrativa Implícita · Interferencia Aritmética · 25 ítems · 5 grupos</p>'
        f'<table style="width:100%;border-collapse:collapse;font-size:12px;">'
        f'<thead style="background:#e3edf9;"><tr>'
        f'<th style="padding:6px;color:#111111;font-weight:700;">#</th><th style="padding:6px;text-align:left;color:#111111;font-weight:700;">Modelo</th>'
        f'<th style="padding:6px;color:#111111;font-weight:700;">Pass Rate</th><th style="padding:6px;color:#111111;font-weight:700;">Spatial</th>'
        f'<th style="padding:6px;color:#111111;font-weight:700;">Arith.</th><th style="padding:6px;color:#111111;font-weight:700;">EPI</th>'
        f'<th style="padding:6px;color:#111111;font-weight:700;">Timestamp</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div>'
    )

def _progress_html(done, total, model_n):
    pct = int(done/total*100)
    bc  = '#34a853' if pct==100 else '#4285f4'
    return (
        f'<div style="font-family:sans-serif;padding:8px 14px;border-radius:8px;'
        f'background:#f8f9fa;border-left:4px solid {bc};margin:4px 0;">'
        f'<b>🧩 T6 MemEsp-Dual · {model_n}</b> — <span style="color:{bc};">{done}/{total} ítems ({pct}%)</span>'
        f'<div style="margin-top:4px;background:#e0e0e0;border-radius:4px;height:6px;">'
        f'<div style="width:{pct}%;background:{bc};height:6px;border-radius:4px;transition:width 0.3s;"></div></div></div>'
    )

def _trap_breakdown_html(results):
    from collections import defaultdict
    by_trap = defaultdict(lambda: {'total':0,'passed':0,'sp':[],'ar':[]})
    for r in results:
        t = r.get('secondary_trap','')
        by_trap[t]['total']  += 1
        by_trap[t]['passed'] += 1 if r.get('passed') else 0
        by_trap[t]['sp'].append(r.get('axes',{}).get('spatial',0))
        by_trap[t]['ar'].append(r.get('axes',{}).get('arithmetic',0))
    cards = ''
    trap_icons = {'RULE_SHIFT':'🔄','ACCESS_ORDER':'🗺️','ZONE_ALIAS':'🏷️','DUAL_COUNTER':'⚖️','ALL_TRAPS_COMBINED':'💀'}
    for trap, stats in by_trap.items():
        pr  = (stats['passed']/stats['total'])*100
        sp  = sum(stats['sp'])/len(stats['sp']) if stats['sp'] else 0
        ar  = sum(stats['ar'])/len(stats['ar']) if stats['ar'] else 0
        pc  = '#34a853' if pr>=70 else '#fbbc04' if pr>=40 else '#ea4335'
        icon= trap_icons.get(trap,'🔹')
        label = SECONDARY_TRAP_LABELS.get(trap, trap)
        cards += (
            f'<div style="background:white;border-radius:8px;padding:10px 12px;'
            f'border-left:4px solid {pc};margin:5px 0;box-shadow:0 1px 3px rgba(0,0,0,0.07);">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<div><span style="font-size:16px;">{icon}</span> <b style="margin-left:4px;font-size:13px;">{label[:55]}</b></div>'
            f'<div style="text-align:right;"><span style="font-size:18px;font-weight:bold;color:{pc};">{pr:.0f}%</span>'
            f'<span style="font-size:10px;color:#5f6368;display:block;">{stats["passed"]}/{stats["total"]} pass</span></div>'
            f'</div>'
            f'<div style="margin-top:6px;font-size:11px;color:#5f6368;">'
            f'Spatial: <b style="color:#4285f4;">{sp:.2f}</b>  |  Arithmetic: <b style="color:#34a853;">{ar:.2f}</b></div>'
            f'</div>'
        )
    return f'<div style="padding:10px;"><h4 style="margin:0 0 8px;color:#202124;">🃏 Breakdown por Trampa Secundaria</h4>{cards}</div>'


@kbench.task(
    name='ExProf T6 — MemEsp-Dual (Spatial WM + Arithmetic Interference)',
    description='T6: 25 implicit-narrative spatial-arithmetic tasks. 5 secondary trap groups. PASS: >=70%. CANTAB-SWM inspired.'
)
def task_t6_mesp_dual(llm):
    import time, io as _io
    from IPython.display import display, HTML, Image
    from collections import defaultdict
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    model_n     = getattr(llm, 'model_name', getattr(llm, 'name', 'model'))
    total_items = len(T6_TASKS_DATA)

    prev_lb = _load_lb()
    prev_lb = [e for e in prev_lb if e.get('model') != model_n]

    # ── Pin display slots at TOP ──────────────────────────────────────────────
    lb_handle    = display(_render_t6_lb(prev_lb, current_model=model_n), display_id=True)
    prog_handle  = display(HTML(_progress_html(0, total_items, model_n)), display_id=True)
    chart_handle = display(HTML(
        '<div style="height:40px;background:#f8f9fa;border-radius:8px;display:flex;'
        'align-items:center;justify-content:center;color:#9aa0a6;font-family:sans-serif;font-size:12px;">'
        '📊 Gráfico T6 — disponible al finalizar los 25 ítems</div>'
    ), display_id=True)
    card_handle  = display(HTML(
        '<div style="height:30px;background:#f8f9fa;border-radius:8px;display:flex;'
        'align-items:center;justify-content:center;color:#9aa0a6;font-family:sans-serif;font-size:12px;">'
        '🃏 Tarjetas por trampa — disponibles al finalizar</div>'
    ), display_id=True)

    print("─"*65)
    print(f"  ExProf-Bench T6 — MemEsp-Dual (Spatial WM + Arithmetic)")
    print(f"  Modelo: {model_n}  |  Ítems: {total_items}  |  PASS: ≥70%")
    print("─"*65)

    passed_count = 0
    scores_sum   = 0.0

    for i, item in enumerate(T6_TASKS_DATA):
        prompt_text = build_t6_prompt(item)
        t0 = time.time()
        response = llm.prompt(prompt_text)
        t1 = time.time()
        score, reason, axes = evaluate_t6(response, item)
        passed  = score >= 0.70
        latency = round(t1 - t0, 2)

        if passed: passed_count += 1
        scores_sum += score

        GLOBAL_RESULTS.append({
            'id':             item['id'],
            'name':           item['name'],
            'model':          model_n,
            'score':          score,
            'reason':         reason,
            'passed':         passed,
            'secondary_trap': item['secondary_trap'],
            'difficulty':     item['difficulty'],
            'latency':        latency,
            'axes':           axes,
        })

        flag = '✅' if passed else '❌'
        trap_lbl = SECONDARY_TRAP_LABELS.get(item['secondary_trap'],item['secondary_trap'])[:40]
        sp = axes['spatial']; ar = axes['arithmetic']; rb = axes['robustness']
        print(f"{flag} [{item['id']}] {'PASS' if passed else 'FAIL'}  score={score:.2f}  lat={latency}s")
        print(f"     trap: {trap_lbl}")
        print(f"     spatial={sp:.2f}  arithmetic={ar:.2f}  robustness={rb:.2f}")
        if reason != 'ok': print(f"     reason: {reason[:65]}")
        print()

        prog_handle.update(HTML(_progress_html(i+1, total_items, model_n)))

    # ── Final stats ───────────────────────────────────────────────────────────
    overall_score = scores_sum / total_items
    pass_rate     = (passed_count / total_items) * 100
    epi           = round(1.0 - overall_score, 3)

    # Trap breakdown
    by_trap = defaultdict(lambda: {'total':0,'passed':0,'sp':[],'ar':[]})
    for r in GLOBAL_RESULTS:
        t = r['secondary_trap']
        by_trap[t]['total']  += 1
        by_trap[t]['passed'] += 1 if r['passed'] else 0
        by_trap[t]['sp'].append(r['axes']['spatial'])
        by_trap[t]['ar'].append(r['axes']['arithmetic'])

    current_entry = {
        'model':           model_n,
        'pass_rate':       pass_rate,
        'avg_score':       overall_score,
        'avg_spatial':     sum(r['axes']['spatial'] for r in GLOBAL_RESULTS)/total_items,
        'avg_arithmetic':  sum(r['axes']['arithmetic'] for r in GLOBAL_RESULTS)/total_items,
        'epi':             epi,
        'passed':          passed_count,
        'total':           total_items,
        'trap_breakdown':  {t: {'pass_rate':(by_trap[t]['passed']/by_trap[t]['total'])*100} for t in by_trap},
        'timestamp':       _datetime.datetime.now().isoformat(),
    }
    updated_lb = prev_lb + [current_entry]
    _save_lb(updated_lb)

    print("─"*65)
    print(f"  COMPLETADO: {model_n}")
    print(f"  Pass Rate : {pass_rate/100:.2f}  ({passed_count}/{total_items})")
    print(f"  EPI       : {epi:.3f}")
    print(f"  Spatial   : {current_entry['avg_spatial']:.3f}  |  Arithmetic: {current_entry['avg_arithmetic']:.3f}")
    print("─"*65)

    lb_handle.update(_render_t6_lb(updated_lb))
    prog_handle.update(HTML(_progress_html(total_items, total_items, model_n)))

    # ── Chart ─────────────────────────────────────────────────────────────────
    plt.switch_backend('agg')
    traps  = list(by_trap.keys())
    accs   = [(by_trap[t]['passed']/by_trap[t]['total'])*100 for t in traps]
    sp_avg = [sum(by_trap[t]['sp'])/len(by_trap[t]['sp'])*100 for t in traps]
    ar_avg = [sum(by_trap[t]['ar'])/len(by_trap[t]['ar'])*100 for t in traps]
    labels = [SECONDARY_TRAP_LABELS.get(t,t)[:30] for t in traps]
    cols   = ['#34a853' if a>=70 else '#fbbc04' if a>=40 else '#ea4335' for a in accs]
    si_col = '✅' if pass_rate>=70 else '❌'
    epi_c  = '#34a853' if epi<=0.2 else '#fbbc04' if epi<=0.4 else '#ea4335'

    fig = plt.figure(figsize=(14, 8), facecolor='#f8f9fa')
    fig.patch.set_linewidth(3); fig.patch.set_edgecolor('#4285f4')

    ax_hd = fig.add_axes([0.0, 0.86, 1.0, 0.14], facecolor='#4285f4')
    ax_hd.axis('off')
    ax_hd.text(0.5, 0.70, f'🧩 ExProf-Bench T6  ·  MemEsp-Dual  ·  {model_n}  {si_col}',
        ha='center', va='center', fontsize=13, fontweight='bold', color='white', transform=ax_hd.transAxes)
    ax_hd.text(0.5, 0.18, 'CANTAB Spatial Working Memory + Arithmetic Dual-Task  |  25 items  |  5 trap groups',
        ha='center', va='center', fontsize=8, color='#d0e8ff', transform=ax_hd.transAxes)

    ax_kpi = fig.add_axes([0.0, 0.62, 0.28, 0.22], facecolor='white')
    ax_kpi.axis('off')
    ax_kpi.text(0.5, 0.92, 'Global T6', ha='center', fontsize=10, fontweight='bold', color='#202124', transform=ax_kpi.transAxes)
    ax_kpi.text(0.5, 0.62, f'{pass_rate:.1f}%', ha='center', fontsize=26, fontweight='bold',
        color='#34a853' if pass_rate>=70 else '#ea4335', transform=ax_kpi.transAxes)
    ax_kpi.text(0.5, 0.42, f'Pass Rate ({passed_count}/{total_items})', ha='center', fontsize=9, color='#5f6368', transform=ax_kpi.transAxes)
    ax_kpi.text(0.30, 0.18, f'(ER + (1 - PD)) / 2: {epi:.3f}', ha='center', fontsize=9, fontweight='bold', color=epi_c, transform=ax_kpi.transAxes)
    ax_kpi.text(0.70, 0.18, f'Spatial: {current_entry["avg_spatial"]:.2f}', ha='center', fontsize=9, color='#4285f4', transform=ax_kpi.transAxes)

    # Grouped bar — pass rate + spatial + arithmetic per trap
    ax_bar = fig.add_axes([0.30, 0.28, 0.68, 0.56], facecolor='white')
    y = np.arange(len(traps))
    w = 0.25
    ax_bar.barh(y + w,   accs,   color=['#34a853' if a>=70 else '#ea4335' for a in accs], height=w, label='Pass Rate')
    ax_bar.barh(y,       sp_avg, color='#4285f4', height=w, alpha=0.7, label='Spatial')
    ax_bar.barh(y - w,   ar_avg, color='#fbbc04', height=w, alpha=0.7, label='Arithmetic')
    ax_bar.set_xlim(0, 120)
    ax_bar.set_yticks(y)
    ax_bar.set_yticklabels(labels, fontsize=7.5)
    ax_bar.axvline(x=70, color='#ea4335', linestyle='--', linewidth=1, alpha=0.6)
    ax_bar.set_xlabel('Score (%)', fontsize=8, color='#5f6368')
    ax_bar.set_title('Rendimiento por Trampa Secundaria — T6 MemEsp-Dual', fontsize=9, fontweight='bold', color='#202124', pad=8)
    ax_bar.spines['top'].set_visible(False); ax_bar.spines['right'].set_visible(False)
    ax_bar.tick_params(axis='both', labelsize=7.5, colors='#5f6368')
    ax_bar.legend(fontsize=8, frameon=False, loc='lower right')

    # Axes bar in legend area
    ax_lg = fig.add_axes([0.0, 0.28, 0.28, 0.32], facecolor='white')
    ax_lg.axis('off')
    ax_lg.text(0.5, 0.95, 'Scoring Axes', ha='center', fontsize=8, fontweight='bold', color='#202124', transform=ax_lg.transAxes)
    for j,(lbl,w,c) in enumerate([('Spatial accuracy','50%','#4285f4'),('Arithmetic accuracy','40%','#34a853'),('Robustness','10%','#fbbc04')]):
        ax_lg.text(0.08, 0.75-j*0.22, '■', fontsize=14, color=c, transform=ax_lg.transAxes)
        ax_lg.text(0.20, 0.75-j*0.22, f'{lbl} ({w})', fontsize=8, color='#202124', va='center', transform=ax_lg.transAxes)

    ax_ft = fig.add_axes([0.0, 0.0, 1.0, 0.08], facecolor='#e8f0fe')
    ax_ft.axis('off')
    ax_ft.text(0.5, 0.5, 'ExProf-Bench T6 MemEsp-Dual  |  CANTAB-SWM inspired  |  Kaggle AGI Hackathon 2026  |  Google DeepMind × Kaggle',
        ha='center', va='center', fontsize=8, color='#4285f4', transform=ax_ft.transAxes)

    buf = _io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.savefig('exprof_t6_mesp_results.png', dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig); buf.seek(0)
    chart_handle.update(Image(data=buf.read(), format='png'))
    card_handle.update(HTML(_trap_breakdown_html(GLOBAL_RESULTS)))

    # ── Final assertion ───────────────────────────────────────────────────────
    # assert_true registers PASS/FAIL in Kaggle's scoring system.
    # We capture its Bokeh widget output so the broken widget doesn't appear.
    # The assertion itself still runs and is recorded correctly.
    overall_passed = passed_count / total_items >= 0.70
    _assertion_label = (
        '[T6-MESP-DUAL] Score: ' + str(round(overall_score, 3))
        + ' | ' + str(passed_count) + '/' + str(total_items)
        + ' tasks pass. Required: >=70% tasks pass.'
    )
    try:
        from IPython.utils.capture import capture_output as _cap
        with _cap(display=True):
            kbench.assertions.assert_true(overall_passed, expectation=_assertion_label)
    except Exception:
        kbench.assertions.assert_true(overall_passed, expectation=_assertion_label)
    # Return 1.0 (Pass) or 0.0 (Fail) per item based on the 0.70 threshold.
    # Kaggle will average these (e.g. 24 passes out of 25 items -> 0.96) which perfectly equals the Pass Rate.
    return float(passed_count / total_items)

task_t6_mesp_dual.run(kbench.llm)






