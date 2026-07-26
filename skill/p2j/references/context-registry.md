# Local Context Registry

Use the registry automatically before every Project2Job Skill run. It is shared
infrastructure, not a Skill or the future Agent.

## Resolve

Run:

```text
python ../p2j/scripts/context_registry.py resolve \
  --project <project> --jd-file <jd>
```

For a URL-backed JD, also pass `--jd-url <url>` so changed page content becomes
a new version of the same JD. For pasted text, use a temporary `--jd-file` plus
`--jd-key <stable role label>` or pipe it with `--jd-stdin`.

- Reuse returned confirmed facts, ownership boundaries, compatible evidence,
  unresolved questions, and output references.
- When `reuse_notice` is true, say: “Previous Project2Job context found. The
  unchanged project evidence and confirmed information were reused.” Adjust
  “project” to “JD” when only JD context was reused.
- Never show internal context states, versions, IDs, hashes, paths, or storage
  details in normal user output.
- If identity is ambiguous, ask one focused Project or JD identity question
  before merging records.
- Treat current sources as authoritative. Follow `changes`, `recompute`, and
  invalidated output references; do not revive a saved claim whose source
  changed or disappeared.
- Do not reopen unchanged source content unless a named evidence gap requires it.
  The resolver reuses cached fingerprints for unchanged files.

`--mode refresh` forces source analysis and result recomputation while retaining
compatible confirmed facts. `--mode fresh` bypasses all reuse without deleting
history.

## Save

After producing a useful result, prepare a small JSON analysis record and run:

```text
python ../p2j/scripts/context_registry.py save-run \
  --project <project> --jd-file <jd> --skill <skill> \
  --analysis <analysis.json>
```

The first persistent write must follow the user's one-time consent and include
`--consent`. If the user says not to save, add `--do-not-save`; this writes
nothing and does not request consent.

One-time Skill use remains a first-class path. `$p2j`, `$p2j-brief`,
`$p2j-intel`, and `$p2j-upgrade` may produce their normal useful host-native
result without loading or invoking the stateful update runtime. Do not create a
registry directory or consent file merely because a Skill was invoked.

Save only supported or user-confirmed facts, claim-level ownership boundaries,
source references, the canonical Agent evidence/claim/output/dependency state,
privacy-safe traces, observed usage, unresolved questions, known gaps, output
references, and the recommended route. Never save source bodies, credentials,
secrets, full generated answers, or unrelated personal data.
Use `fact_id`, `claim_id`, `question_id`, or `gap_id` plus `source_paths` on
saved items, and use the canonical lowercase evidence statuses in JSON.

The default directory is `~/.project2job`. Respect `P2J_HOME`; tests must point
it to a temporary directory.

## Forget

Run `forget` with the selected `--project`, `--jd-file`, or `--jd-url`. Delete
only that record and linked Project2Job runs; do not delete source files or
unrelated Project2Job context.

If the registry is corrupt or unreadable, report the failure visibly, do not
write over it, and continue without reuse only after telling the user.
