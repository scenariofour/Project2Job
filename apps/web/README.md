# Thin Agent Report

This is a local, read-only demonstration surface for structured Stateful Agent
output. It is not a production Web application.

Build the four shared-shell report states:

```bash
make agent-demo
python3 -m http.server --directory dist/agent-report 8080
```

Open `http://localhost:8080/initial_analysis.html`. The other reports are
`evidence_inspection.html`, `project_updated.html`, and
`no_relevant_changes.html`.

`scripts/build_agent_demo.py` creates the committed structured fixtures by
running the Agent orchestration code. `render_report.py` renders each fixture
through one shared three-column shell. Generated HTML stays under ignored
`dist/`; the renderer and fixtures are the source of truth.

The report intentionally shows plain-language activity rather than raw internal
state. Corrections remain previews until approval, changed outputs use
Before / After / Why, and preserved output names come from the actual trace.

The real Etsy dogfood outputs also render through this same shell. Open the
self-contained files under `docs/dogfood/etsy-agent-v0/`, or regenerate one:

```bash
python3 apps/web/render_report.py \
  docs/dogfood/etsy-agent-v0/03-project-updated.json \
  --output /tmp/project2job-update.html
```
