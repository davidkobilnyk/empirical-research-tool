---
name: evidence-dossier
description: Build an evidence dossier for a research question — search several literature connectors with balanced query sets, de-duplicate to distinct works, check retraction and correction status, extract descriptive per-source metadata with verbatim quotes, and render a source list with the selection rules stated. Presents evidence for the reader to evaluate; assigns no grades, scores or rankings. Use for literature triage, methodology-claim review, or any question where you need to see what the sources say and how the list was made.
---

# Evidence dossier

Finds sources for a question, says what each one is and what it reports, shows how
the list was made, and stops. It does not grade, score, rank by quality, or answer
the question — that is the reader's work, and the output says so.

## Before you run

1. **Ask the user for the disconfirming query.** It is required and has no default.
   Word it as the negated claim ("pre-registration does not reduce publication
   bias"), never as a meta-request about the claim ("evidence that pre-registration
   does not work"). This is measured, not stylistic: a template embedding the
   question doubled the number of sources returned by both query sets. Propose one
   and have the user confirm or replace it.
2. **Check the domains.** `api.crossref.org` and `api.datacite.org` must be
   reachable. Without them there is no retraction status, no canonical titles and
   weaker work linkage — the dossier still builds, and it will say what was missing.
   Request them with `request_network_access` if blocked.
3. **Connectors.** Needs at least one of `fasttrack-literature`, `consensus`,
   `scispace`, `scholar-gateway`. A connector that is absent or failing is recorded
   in the coverage note as unavailable, never silently dropped.

## Run it — two cells, in this order

The split is forced by where things are reachable: MCP connectors work only in the
control-plane kernel, and Crossref/DataCite are not reachable from there.

```python
# repl tool — retrieval
rundir, stats = dossier_retrieve(
    "Does X cause Y?",                     # the question, as the user asked it
    "X does not cause Y",                  # the negated claim, user-confirmed
    host.mcp)
print(rundir, stats["records_returned"], stats["unique_sources"])
```

```python
# python tool — integrity, linkage, extraction, dossier
path, stats = dossier_build(rundir, host.llm, email=<contact or None>)
print(path, stats)
```

Then `save_artifacts` the dossier and the run's `coverage-note.md`.

## What comes out

In the run directory: `evidence-dossier.md` (the deliverable), `coverage-note.md`
(what was searched and what was unreachable), `sources.json`, `works.json`,
`extracted.json`, `payloads.json` (the raw connector responses — keep them; they
are not reproducible and they are the fixture for any later parser change).

The dossier carries, per source: what it is, what it examined and how much of it,
what it reports, direction relative to the question, original-versus-replication,
its own pre-registration, precision or heterogeneity as stated, publication-bias
correction, data and code availability, claimed scope, retraction status, which
channels found it, and a verbatim quote.

## Reading the output honestly

- **"not stated" is a finding about the retrieved text**, not a gap in the
  extraction. Most sources arrive as an abstract or a passage, so a field the paper
  does report can still read "not stated".
- **Quote status has three values**: verified, verified (elided) — every word
  present in order with parentheticals dropped — and NOT FOUND. A not-found quote
  is grounds for distrusting every field on that source; it is displayed, never
  removed.
- **Direction is not agreement.** It describes what a source reports, not whether
  the source is right.
- **Selection is a decision.** By default every source with usable text is shown.
  Pass `term_groups=[["term","term"],["term"]]` to filter — a source must match one
  term from every group — and the groups are printed above the list with everything
  they excluded.

## Known limits

Extraction reads only the text a channel returned; full-text routes exist but are
not wired in. Citation chaining and saturation are not implemented. Titles for
DOI-bearing sources come from linkage in normalised form. Grading is deliberately
absent: see specs 61–68 of the tool's specification.
