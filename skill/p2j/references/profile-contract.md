# Profile and Selective Routing Contract

Use three bounded, consented context layers. Validate them against the canonical
schemas before reuse.

## Context layers

### Project Evidence Profile

Build deeply once per Project version through `$p2j-audit`. Store source-linked
verified facts, ownership, decisions, architecture, results, bad cases, story
directions, and hiring signals. Keep source paths on every section.

- Reuse the same profile across JDs.
- Compare the artifact manifest before retrieval.
- On a Project change, reopen only added or changed sources. Changed or removed
  paths invalidate their dependent sections. Because an added source cannot
  appear in old `source_paths`, inspect its evidence surfaces first and keep
  every potentially affected section stale until that inspection is complete.
- Never treat the profile as evidence independent of its current sources.

### Company Intelligence Profile

Build through `$p2j-intel` and key by normalized company plus the exact
normalized track string. Store
culture and values, product/AI direction, role or team priorities, interview
signals, exact sources, source fingerprint, research date, and `fresh_until`.

- Reuse only when both normalized company and normalized track match exactly.
- Refresh only when stale or when official source fingerprints materially
  change. A different normalized track is a different profile key, not a
  "compatible track" judgment.
- Reparse a changed JD without reopening unchanged Project evidence or repeating
  fresh company research.

### JD Demand Map

Extract per JD. Keep it lightweight: role tasks, stated level, hiring signals,
must-haves, and preferred qualifications. Bind `company_profile_key` to the
resolved Company Intelligence Profile and reuse the map only while those keys
match. A changed JD invalidates this map and role matching, not the other two
profiles.

## Plan one request

Run `scripts/profile_router.py` or apply its deterministic routing rules before
opening sources. Generate only the requested asset.

| Request | Normal specialist invocation |
| --- | --- |
| fast verdict | reuse fresh Company Intelligence or run bounded `$p2j-intel`, then `$p2j-brief` |
| company/interview intelligence | `$p2j-intel` |
| deep evidence audit | `$p2j-audit` |
| one interview answer | `$p2j-answer` |
| interactive defense | `$p2j-mock` |
| one project improvement | `$p2j-upgrade` |
| Project Highlights, introduction, or resume bullets | no specialist when all required profiles are fresh; otherwise build only the missing profile |

Do not run Brief, Intel, Audit, Answer, Mock, and Upgrade together merely because
a JD and Project are present.

Use **Full Preparation** only when the user explicitly requests complete
application and interview preparation. Assemble the full canonical pack and use
all six specialist capabilities, while satisfying fresh Audit/Intel dependencies
from cached profiles rather than rerunning them.

## Hiring strategy

Make the strategic decision. Select one strongest defensible story and
positioning; do not ask the user to choose. Translate technical evidence into
product, user, business, and AI PM value. Adapt selection, ordering, terminology,
and emphasis to the Company Intelligence Profile and JD Demand Map without
changing the verified fact pool.

Never claim company or culture adaptation when the Company Intelligence Profile
is missing, stale, materially changed, or for a different normalized track.

Ask at most one question, and only when one missing historical fact materially
changes the claim. Never invent dates, launch status, experiments, ownership,
users, metrics, or outcomes.

## External assets and Private Defense

Keep weaknesses, caveat lists, missing-validation summaries, unsupported claims,
difficult follow-ups, and fallback language out of copyable career assets. Store
them under `Private Defense` for Mock preparation. Include a boundary in the
copyable asset only when omission would make an asserted fact false or materially
misleading.

Frame a relevant bad case in this order:

```text
early signal or constraint
→ diagnosis
→ deliberate decision
→ system or product change
→ stronger result
→ target hiring signal
```

End on judgment, improvement, control, or achievement.

## Usage record

For every run record the exact file paths opened, specialist Skills invoked,
model calls, input tokens, cached input tokens, uncached input tokens, output
tokens, and stop reason. Use `profile_router.usage_report` to validate token
arithmetic. Record unavailable host telemetry as unavailable; never estimate it
silently.
