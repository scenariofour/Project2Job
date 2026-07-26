from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def esc(value: object) -> str:
    return html.escape(str(value))


def output_cards(outputs: dict, kind: str) -> str:
    cards = []
    for output in outputs.values():
        if output.get("kind") != kind:
            continue
        if kind == "score":
            cards.append(
                f"""<article class="row">
                <div><strong>{esc(output['label'])}</strong><p>{esc(output.get('explanation', ''))}</p></div>
                <b>{esc(output['value'])}/5</b></article>"""
            )
        elif kind == "jd_match":
            status = output.get("match", "GAP")
            cards.append(
                f"""<article class="match">
                <div><strong>{esc(output['label'])}</strong><span class="status {status.lower().replace(' ', '-')}">{esc(status)}</span></div>
                <p>{esc(output.get('evidence', ''))}</p><small>Missing: {esc(output.get('missing', ''))}</small>
                </article>"""
            )
        elif kind == "story":
            cards.append(
                f"""<article class="story"><strong>{esc(output['label'])}</strong>
                <p>{esc(output.get('content', ''))}</p></article>"""
            )
    return "".join(cards)


def activity(trace: dict) -> str:
    items = []
    for index, step in enumerate(trace.get("steps", []), start=1):
        items.append(
            f"""<li><small>Step {index}</small><b>{esc(step['selected_action'].replace('_', ' ').title())}</b>
            <p>{esc(step.get('observation_summary', ''))}</p>
            <em>Validation: {esc(step.get('validation_result', 'not run'))}</em></li>"""
        )
    if not items:
        reason = trace.get("stop_reason", "complete").replace("_", " ")
        items.append(
            f"<li><small>Step 1</small><b>Checked current context</b><p>{esc(reason.title())}.</p></li>"
        )
    items.append(
        f"<li><small>Final</small><b>Stopped safely</b><p>{esc(trace.get('stop_reason', 'complete').replace('_', ' ').title())}.</p></li>"
    )
    return "".join(items)


def initial_view(data: dict) -> str:
    outputs = data["state"]["outputs"]
    route = next(
        (item for item in outputs.values() if item.get("kind") == "route"), {}
    )
    return f"""
    <p class="eyebrow">Preliminary Project2Job Brief</p>
    <h1>Strong supporting project with a clear reliability story</h1>
    <p class="lede">The project directly demonstrates bounded AI workflow judgment. Its largest limitation is the lack of a measured commercial outcome.</p>
    <section><h2>Preliminary Project Scores</h2>{output_cards(outputs, "score")}</section>
    <section><h2>JD Match</h2><div class="grid">{output_cards(outputs, "jd_match")}</div></section>
    <section><h2>Interview Value</h2>{output_cards(outputs, "story")}</section>
    <section class="agent-panel"><p class="eyebrow">Recommended Route</p>
      <h2>{esc(route.get('route', 'Review Next Build'))}</h2>
      <p>{esc(route.get('content', ''))}</p><button>Review Next Build</button></section>
    """


def inspection_view(data: dict) -> str:
    item = data["inspection"]
    sources = "".join(
        f"<article class='source'><strong>{esc(source['label'])}</strong><p>{esc(source['summary'])}</p></article>"
        for source in item["sources"]
    )
    preview = "".join(
        f"""<article class="change"><div><small>Before</small><p>{esc(change['before'])}</p></div>
        <div><small>After</small><p>{esc(change['after'])}</p></div>
        <p><strong>Why:</strong> {esc(change['why'])}</p></article>"""
        for change in item["correction"]["preview"]
    )
    affected = "".join(f"<li>{esc(value)}</li>" for value in item["affected_outputs"])
    return f"""
    <p class="eyebrow">Evidence Inspection</p><h1>Evidence behind this result</h1>
    <section><h2>Target claim</h2><blockquote>{esc(item['claim'])}</blockquote></section>
    <section><h2>Supporting sources</h2>{sources}</section>
    <section class="split"><div><h3>Attribution scope</h3><p>{esc(item['attribution_scope'])}</p></div>
    <div><h3>Affected outputs</h3><ul>{affected}</ul></div></section>
    <section class="agent-panel"><h2>Human correction</h2><p>{esc(item['correction']['prompt'])}</p>
    <textarea aria-label="Correction"></textarea><h3>Preview before approval</h3>{preview}
    <button>Approve &amp; Apply Correction</button></section>
    """


def updated_view(data: dict) -> str:
    trace = data["trace"]
    outputs = data["state"]["outputs"]
    changes = []
    for output_id in trace["affected_outputs"]:
        output = outputs[output_id]
        after = output.get("value", output.get("match", output.get("content", "")))
        changes.append(
            f"""<article class="change"><div><small>Before</small><p>{esc(output.get('before', 'Not available'))}</p></div>
            <div><small>After</small><p>{esc(after)}</p></div>
            <p><strong>{esc(output.get('label', output_id))}</strong><br><strong>Why:</strong> {esc(output.get('why', 'Source evidence changed.'))}</p></article>"""
        )
    preserved = "".join(
        f"<li>{esc(outputs[item].get('label', item))}</li>"
        for item in trace["preserved_outputs"]
        if item in outputs
    )
    return f"""
    <p class="eyebrow agent-color">Project Updated</p>
    <h1>Selective Update Summary</h1>
    <p class="lede">Only outputs supported by the new evaluation evidence were updated.</p>
    <section><div class="section-title"><h2>Changed outputs</h2><b>{len(trace['affected_outputs'])} updated</b></div>
    {''.join(changes)}</section>
    <section class="preserved"><h2>Preserved without regeneration</h2><ul>{preserved}</ul></section>
    """


def unchanged_view(data: dict) -> str:
    usage = data["trace"]["usage"]
    return f"""
    <div class="empty"><span class="pip"></span><h1>No relevant changes found</h1>
    <p class="lede">Project evidence, target JD, and confirmed facts match the previous analysis. The existing result remains current.</p>
    <div class="metrics"><div><b>0</b><span>Repeated questions</span></div>
    <div><b>{usage.get('capability_calls', 0)}</b><span>Capability calls</span></div>
    <div><b>0</b><span>Files reopened</span></div><div><b>0</b><span>Outputs regenerated</span></div></div>
    <button>Open Current Result</button><button class="secondary">Analyze From Scratch</button></div>
    """


def render(data: dict) -> str:
    views = {
        "initial_analysis": initial_view,
        "evidence_inspection": inspection_view,
        "project_updated": updated_view,
        "no_relevant_changes": unchanged_view,
    }
    body = views[data["view"]](data)
    project = data["project"]
    jd = data["jd"]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Project2Job — {esc(data['view'].replace('_', ' ').title())}</title>
    <style>
    :root{{--paper:#f6f5f1;--ink:#181818;--line:#d8d5d0;--purple:#5c5ce2;--green:#12513c;--amber:#8a6534;--red:#c44133;--muted:#68666f}}
    *{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:14px/1.5 Inter,ui-sans-serif,system-ui}}
    header{{height:72px;border-bottom:1px solid var(--line);display:flex;align-items:center;padding:0 28px;gap:42px;background:#fbfaf7}}
    .brand,h1{{font-family:Newsreader,Georgia,serif}}.brand{{font-size:34px}}header span:last-child{{margin-left:auto;color:var(--muted)}}
    .desk{{display:grid;grid-template-columns:220px minmax(540px,760px) 360px;min-height:calc(100vh - 72px);justify-content:center}}
    nav,aside{{padding:28px 22px}}nav{{border-right:1px solid var(--line);background:#f2f0ec}}aside{{border-left:1px solid var(--line)}}
    nav a{{display:block;padding:10px 0;color:var(--muted)}}nav a.active{{color:var(--purple);font-weight:700}}
    main{{padding:54px 40px}}h1{{font-size:42px;line-height:1.12;font-weight:500;margin:8px 0 18px}}h2{{font-size:19px}}h3{{font-size:13px;text-transform:uppercase;letter-spacing:.06em}}
    .lede{{font-size:17px;color:#4d4b53;max-width:650px}}section{{margin:34px 0;border-top:1px solid var(--line);padding-top:18px}}
    .eyebrow{{text-transform:uppercase;letter-spacing:.1em;font-size:11px;font-weight:800;color:var(--green)}}.agent-color{{color:var(--purple)}}
    .row,.match,.story,.source,.change,.split,.preserved,.agent-panel,.empty{{border:1px solid var(--line);border-radius:8px;background:#fbfaf7;padding:16px;margin:10px 0}}
    .row{{display:flex;justify-content:space-between;gap:24px}}.row p,.match p,.story p,.source p{{margin:5px 0;color:#54515b}}
    .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}.match div{{display:flex;gap:8px;justify-content:space-between}}
    .status{{font-size:10px;font-weight:800}}.exact-match{{color:var(--green)}}.transferable{{color:var(--amber)}}.gap{{color:var(--red)}}
    .agent-panel{{border-color:var(--purple);background:#f3f1ff}}button{{border:0;border-radius:8px;background:var(--ink);color:white;padding:11px 16px;font-weight:700}}button:focus-visible,textarea:focus-visible{{outline:3px solid var(--purple);outline-offset:2px}}
    button.secondary{{background:transparent;color:var(--ink);border:1px solid var(--line);margin-left:8px}}textarea{{width:100%;height:90px;border:1px solid var(--line);background:white;margin:8px 0 14px}}
    .split,.change{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.change>p{{grid-column:1/-1}}.change small{{text-transform:uppercase;color:var(--muted);letter-spacing:.06em}}
    .section-title{{display:flex;align-items:center;justify-content:space-between}}.section-title b{{color:var(--purple)}}.preserved{{color:var(--muted)}}
    .empty{{margin-top:18vh;padding:36px}}.pip{{display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--green)}}.empty h1{{display:inline;margin-left:12px}}
    .metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:28px 0}}.metrics div{{border:1px solid var(--line);padding:14px}}.metrics b{{display:block;font-size:26px}}.metrics span{{font-size:10px;text-transform:uppercase}}
    aside h2{{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--purple)}}aside ol{{list-style:none;padding:0}}aside li{{border-left:1px solid var(--line);padding:0 0 24px 18px}}aside li>b,aside li>small{{display:block}}aside p{{color:var(--muted);margin:4px 0}}aside small{{color:var(--purple);text-transform:uppercase;letter-spacing:.06em}}aside em{{color:var(--green);font-size:12px;font-style:normal}}
    blockquote{{font-family:Georgia,serif;font-size:20px;margin:0}}@media(max-width:1050px){{.desk{{grid-template-columns:180px 1fr}}aside{{grid-column:1/-1;border-left:0;border-top:1px solid var(--line)}}.grid{{grid-template-columns:1fr}}}}
    </style></head><body>
    <header><span class="brand">Project2Job</span><strong>{esc(project['name'])}</strong><strong>{esc(jd['label'])}</strong><span>Local evidence report</span></header>
    <div class="desk"><nav><p class="eyebrow">Project</p><h2>{esc(project['name'])}</h2><p>Version {esc(project['version'])}</p><p class="eyebrow">Target role</p><strong>{esc(jd['label'])}</strong>
    <a class="active">Overview</a><a>JD Match</a><a>Evidence</a><a>Interview Value</a><a>What Changed</a></nav>
    <main>{body}</main><aside><h2>Agent Activity</h2><ol>{activity(data['trace'])}</ol></aside></div></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.fixture.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
