# Research Methodology Evidence Tool

A staged, validation-gated tool that grades the strength of evidence behind
**research-methodology claims** — the kind of claim that says a method, design,
or analytic practice works better than an alternative. Existing frameworks
(GRADE, RoB 2, ROBINS-I, CERQual) assume clinical trial evidence; most
methodology evidence is proofs, simulations, reanalyses, and arguments, so the
rubric adapts those frameworks where they fit and is written fresh where they
do not.

## Design commitments

Two are load-bearing and everything else follows from them.

**A two-layer trust split.** Retrieval and extraction are trusted from Stage 1.
Grading is labelled **provisional** and stays that way until validation passes
against a held-out set the user assembles. No output presents a grade as a
verdict before then.

**Nothing is claimed that has not been measured.** Every capability statement in
`notes/` carries the test that established it and the date it was run. Where a
tool was found weaker than its documentation implied, the claim is withdrawn in
place rather than quietly dropped.

## Layout

| Path | Contents |
|---|---|
| `specs/` | The specification. v3 is current; v2 is retained because spec numbers 1–56 keep their v2 meaning and earlier references must stay resolvable |
| `rubric/` | Stage 1 grading checklists — tier scale, per-type starting tiers, items, combination rule, double-count register. Current rubric version `stage1-checklists-v0.1` |
| `notes/` | Measured findings and decisions: source coverage and access, logging volume, storage choice, build plan, durability |
| `build/` | Generators. The checklist document and its machine-readable table are emitted from one item list so they cannot drift; the specification is revised by line-keyed edits with every anchor asserted to match exactly once |
| `skills/` | Reusable procedure: DOI normalisation, validation, cross-channel deduplication, retraction status |
| `records/` | Dated evidence for claims made in `notes/` |

## Revising

Do not hand-edit `rubric/stage1-*` or `specs/*-v3.md`. Edit the generator in
`build/` and re-run it, so the document, its machine-readable copy, and the
audit trail stay consistent:

```bash
python build/build_checklists.py     # rubric document + item table
python build/build_specs_v3.py       # specification from the v2 text
```

Amending the checklists is a **rubric version change**; amending the
specification is not.

## Status

Design is largely complete; **the pipeline has not been run end to end.** The
specification gates Stage 1 on five retrieval runs with a clean citation audit,
and that count is zero. `notes/build-plan-to-completion.md` lists what remains
in dependency order, including the items only the project owner can do — chiefly
assembling the validation set, which must not be drafted by the model.

## Deliberately not in this repository

- **The Retraction Watch bulk dataset** (~65 MB) — re-fetched from Crossref Labs
  in about 20 seconds; a stale committed copy would be worse than none.
- **Source PDFs** — cache extracted text instead: a twentieth of the size, and
  the citation audit checks retrieved text, not layout.
- **Derived intermediates** — recomputable from `records/` by the build scripts.
- **The validation set** — it does not exist yet, and when it does it is the
  project's highest-effort asset; it should be versioned deliberately, since
  which version was used is part of every validation result.

## Provenance note

`records/stage0-retrieval-raw-2026-09-04.json` holds raw literature-connector
payloads. These are **not reproducible**: the underlying corpora and default
result limits change without notice, so re-running yields different output. The
file is dated for that reason and is the only evidence for the retrieval-yield
figures quoted in `notes/stage0-logging-volume.md`. Treat any measurement in
`notes/` as having a shelf life, and re-measure rather than trust.

## Commit identity

Commits here were made with a placeholder identity (`tool@localhost`) because
the authoring environment had no configured git identity. Set your own before
publishing further history.
