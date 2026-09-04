# Where the log should live, and the DOI question

**September 4, 2026.** Two decisions: whether DOI handling needs external software (it does not), and what the spec 45 log should be stored in.

---

## 1. The DOI issue needs no outside software

It was a bad character class in my own regex, not a missing capability. DOI suffixes legitimately contain parentheses, angle brackets, colons, semicolons and square brackets, so a restrictive pattern truncates exactly the publishers that use them — Elsevier's parenthesised style and Wiley's older SICI style. The fix is to capture broadly and then trim, and to let Crossref resolve any ambiguity a pattern cannot.

`doi_tools.py` does this in three stdlib functions, tested against the hard cases:

| Input form | Result |
|---|---|
`10.1002/(SICI)1521-3773(19980703)37:12<1717::AID-ANIE1717>3.0.CO;2-T` | preserved intact, and confirmed to exist in Crossref |
| the same DOI wrapped as `(doi).`, `[doi];`, `https://doi.org/doi`, or mid-sentence `cited as doi, see also` | all five round-trip to the identical DOI |
| `doi: 10.1002/sim.8086`, `10.1126/science.aac4716.`, `(10.1002/wics.70074)` | prefix and sentence punctuation stripped, DOI intact |
| `10.31222/osf.io/fhdbs` (OSF preprint) | preserved |
| a plausible but fabricated DOI | pattern accepts it, **Crossref validation rejects it** |

That last row is the reason validation matters and a regex alone does not suffice: any pattern permissive enough to keep the Wiley DOI is also permissive enough to accept a DOI that was never issued. `doi_exists()` distinguishes 404 (absent) from a network failure (unknown) so the two are never conflated — which also makes it usable as the spec 33 audit's existence check, alongside the `updated-by` retraction check on the same record.

Trailing brackets are stripped only when unbalanced, which is what lets `(10.1002/(SICI)...)` lose its wrapper without losing its own parentheses.

**Recommended addition to the pipeline:** every DOI entering the log passes through `normalize_doi` then `doi_exists`. A source whose DOI does not resolve is not a citable source under spec 19, and catching that at extraction is cheaper than catching it at audit.

---

## 2. Options for the log itself

Airtable is the only storage service currently connected — the connector list holds no Notion, Sheets, Postgres, or Supabase, though others may be available to enable. So the real choice is between Airtable and a file-based store, which needs no connector at all.

| Option | Row ceiling | Queries for drift and prior-dominance | Human inspection | Setup |
|---|---|---|---|---|
| **Airtable** (connected) | Plan-dependent; free tier is around a thousand records per base | Filter and group in the UI; anything statistical means exporting anyway | Strong — grid views, sharing, comments | None, already connected |
| **SQLite** as an artifact | None that matters here | Native SQL, including the grouped comparisons spec 32 and 44 need | Weak on its own; needs a query or an export | None — stdlib, version 3.53.4 available |
| **Parquet + pandas** | None that matters | Strong for analysis | Weak | Needs `pyarrow` installed; pandas is present |
| **CSV per run** | None | Awkward across runs | Opens anywhere | None |

**Recommendation: SQLite as the canonical store, Airtable as an optional human-facing view.**

The reasoning is what the log is *for*. Spec 45 lists its purposes as follow-up batches, drift detection, and the prior-dominance check — all of which are grouped queries across runs and rubric versions ("tier distribution by rubric version", "agreement rate between sealed prior and graded output over the last N runs"). That is SQL, and in Airtable it means exporting to run it. SQLite also has no row ceiling, which matters because spec 44 requires stale claims from superseded rubric versions to be *retained and marked* rather than deleted, so the log only grows, and survey mode multiplies it by questions per survey.

Airtable earns its place for what SQLite is bad at: letting you look at a run, sort by tier, and read the reasoning without writing a query. That argues for mirroring the current run's claim rows into Airtable while keeping the full history in SQLite, rather than choosing one.

**Two caveats.** A SQLite file kept as an artifact needs a discipline about versions, explained in section 3. And if you expect collaborators to read or annotate the log directly, that pushes toward Airtable as the primary despite the query cost; it is a workflow question, not a technical one.

---

## 3. What "save as new versions of one artifact" means, and why it matters here

**The mechanism.** An artifact is a named file with an ordered chain of versions. Saving a file creates a *new artifact* by default; saving it as a *new version* of an existing artifact requires naming that artifact explicitly. So the same act — "save the log" — produces one of two very different structures depending on one parameter:

| | Result | Querying across runs |
|---|---|---|
| New artifact each run (`log_run1.db`, `log_run2.db`, …) | N unrelated artifacts, each a snapshot | You must know which file is newest, and whether it contains every earlier run |
| New version of one artifact (`evidence_log.db`, versions 1…N) | One artifact, linear history, latest version is the complete log | Fetch the latest version; it is the whole log by construction |

**Why the first option fragments rather than merely clutters.** Three properties of this setup combine badly.

The workspace is ephemeral: each session starts with no files. To append to the log you must first fetch the stored copy. If a session skips that step and creates a fresh database, it does not error — it starts a *parallel history*. You now hold two files, each containing runs the other lacks, and neither is wrong on its face.

SQLite is a single binary file, so a save is whole-file. Two sessions that each seeded from version 7 and appended their own run both save successfully; the second save simply wins, and the first session's rows are gone with no conflict and no warning. This is the one respect in which Airtable is structurally safer: it writes rows, so two writers interleave instead of overwriting.

And spec 44 makes the log append-only in practice — claims graded under a superseded rubric version are *marked stale and retained*, not deleted, so drift detection and the prior-dominance check both read across the full history. A fragmented log doesn't degrade those analyses; it makes them wrong, because the denominator silently changes with which file you happened to open.

**The protocol, in five rules.**

1. **One artifact, one filename**, for the life of the project. Never `log_v2.db`.
2. **Seed before writing.** At run start, resolve the artifact's latest version, copy it into the workspace, and open that. Creating the schema from scratch is a first-run-only path.
3. **Save as a version of that artifact**, passing its artifact id — not as a fresh save of the same filename.
4. **Record the parentage inside the database too.** A `runs` table holding, per run, the version id of the log it was seeded from makes the chain auditable from within the data, so a fork is detectable later rather than invisible.
5. **Single writer at a time.** If two sessions may log concurrently, either serialise them or use Airtable for the live writes and reconcile into SQLite afterwards. Rule 4 detects a fork; only this rule prevents one.

**On storage.** Every version keeps a full copy, which is the right default for a log you may need to roll back. At Stage 0 volumes that is trivial — a few hundred rows is tens of kilobytes. If the log later reaches the point where whole-file copies per run are wasteful, the storage intent can be declared so that only the latest copy is retained, with full snapshots kept deliberately at rubric-version boundaries — which is also the natural place to want a rollback point, since spec 36 allows validation to run only once per rubric version.