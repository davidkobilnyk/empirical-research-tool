# Not depending on an ephemeral setup

**September 4, 2026.** What currently exists only in a place that will not survive, and what to do about each. Includes the Canva Sheets question, since it is the same question in a different form.

---

## 1. Canva Sheets is not a candidate for the log

The Canva connector exposes 32 methods; all of them operate on designs, not on data. Create, copy, edit, merge, resize, export, folders, comments, brand templates, autofill, asset upload. `search-designs` can *find* a sheet, and `read-design` returns a design's metadata and page content, and `export-design` can emit CSV — but there is **no method that appends a row, and none that queries**.

That makes the write path for a log "export the whole sheet, modify, re-import", which is exactly the whole-file overwrite problem described for SQLite in the storage note, with worse tooling and no version chain. A log needs row-level append and grouped queries; Canva offers neither.

**Where Canva does fit:** as an output surface rather than a store. `get-design-dataset` plus autofill takes a brand template with named fields and fills them from data you supply, and `export-design` produces a PDF. That is a reasonable route for the spec 46 output tables and the spec 47 survey document once the log exists elsewhere — a formatting layer, not a database.

---

## 2. What survives what

| Tier | Contents | Survives session end | Survives leaving this platform |
|---|---|---|---|
| **Ephemeral** | Workspace files, kernel variables, loaded skill state | No | No |
| **Platform-durable** | Artifacts and their versions, memory rows, published skills, network-domain grants, connector attachments | Yes | **No** |
| **Externally durable** | Your Airtable base, an OSF or Zenodo deposit, a git repository, files on your own machine | Yes | Yes |

The important line is the second one. Everything produced in this project so far is *platform*-durable, which is enough for continuity between sessions and not enough for a tool you intend to publish or hand to a collaborator.

---

## 3. The checklist

### A. Nothing load-bearing left only in the workspace

The workspace-versus-store diff, when it was first run, held **19 files: 10 with a durable copy and 9 without.** Every one of the nine is accounted for below, with its disposition and the reason.

The governing rule: **a file is saved if regenerating it is expensive, or if it cannot be regenerated identically.** Connector and API output falls in the second category and is the easy one to miss, because it looks reproducible.

| Unsaved file | Size | Disposition |
|---|---|---|
| `handoff_refs_full.json` | 5.7 KB | **Saved** as `anchor-references-verified.json` — 24 DOI-resolved anchor records, expensive to rebuild because Crossref rate-limited the original pass and it took four attempts |
| `handoff/stage0_raw.json` | 293 KB | **Saved** as `stage0-retrieval-raw-2026-09-04.json` — raw connector payloads behind the yield measurement, **not reproducible at all**: corpora and default limits change, so re-running gives a different answer and this is the only evidence for the 93-source figure |
| `handoff/probe_new_connectors.json` | 2.5 KB | **Saved** as `connector-probe-2026-09-04.json` — also connector output, therefore also irreproducible; keeping it is what applying the rule consistently requires |
| `retractionwatch.csv` | 64.9 MB | Not saved — a 20-second re-fetch from a stable endpoint, and by far the largest file here |
| `osf_fhdbs.pdf` | 378 KB | Not saved — re-downloadable through the documented three-hop route, which spec 57 requires verifying at each run series anyway |
| `handoff/stage0_counts.json` | 0.3 KB | Not saved — derived deterministically from the saved raw payloads, and its outputs are transcribed into the logging-volume note |
| `handoff/stage0_volume.json` | 14.5 KB | Not saved — same derivation, and it is the superseded first pass, computed before the deduplication bug was fixed |
| `handoff_refs.json` | 15 KB | Not saved — the pre-correction reference pass, containing the corrigendum mis-resolution that the saved version fixes. Keeping it would preserve a known-wrong record next to the right one |
| `handoff_retraction_probe.json` | 0.4 KB | Not saved — Crossref output, which unlike connector output *is* stably reproducible, and the result is recorded in section 3 |

Two notes on reading a diff like this. Filename matching alone would have reported the two saved-under-a-new-name files as unsaved, so the check compares content hashes as well. And the count moves as work proceeds — it is a snapshot, not a property of the project, which is why the disposition table above is the durable statement rather than the totals.

### B. Nothing load-bearing left only in the conversation

This is the largest gap. The Stage 0 retrieval procedure — which channels, which query shapes, how results are parsed per connector, how they are deduplicated — currently exists as cells in a chat log and prose in the specification. Neither is executable.

- Write the retrieval pipeline as a script artifact with the per-connector parsers, since each connector returns a different shape (two return dicts with a `results` array, two return prose that must be parsed, and one returns passages that need collapsing to articles).
- Capture the run procedure as a skill, so a future session executes it rather than re-deriving it. `doi-source-identity` already does this for the identity layer; the retrieval layer needs the same treatment.

### C. Nothing load-bearing left only in a memory row

Memory persists across sessions but does not leave the platform and is not visible to a collaborator. Every durable decision should therefore live in a document, with memory holding only pointers. Currently satisfied: the measured yields, the schema recommendation, the access ledger, and the DOI rule are all in artifacts. Keep it that way — if a decision is worth a memory row, it is worth a line in the specification or a companion document.

### D. No environment-specific identifier in anything you keep

- **Connector server ids** (the `directory-…` strings) are specific to this environment's connector attachments. Any script must resolve a connector by name at call time, never store the id.
- **OSF download URLs are signed and expire.** Store the API path and re-resolve; the three-hop chain is documented in the coverage note and required by spec 57.
- **Artifact version ids** are fine to cite inside this platform and meaningless outside it. Where a document references another, name the file as well as the id.

### E. One external copy of everything that matters

Pick a destination you control and put the document set there: the specification, the checklists, the coverage note, the storage decision, this checklist, and the skill source. Options, in rough order of usefulness for this project:

1. **A Zenodo deposit** — access is already granted, and it mints a DOI, which makes the rubric version citable. That matters for a methodology tool whose outputs are meant to be auditable: "graded under rubric version X" is a stronger claim when X has a DOI.
2. **A git repository** — best for the code and specification, worst for the log.
3. **A folder on your own machine** — simplest, and I can write directly to it if you grant access.
4. **OSF** — natural if the validation set ends up there too.

### F. The validation set belongs outside the platform from the start

It is the asset that takes the most human effort and the only one nobody else can rebuild (spec 35 assigns its assembly to you). Whatever store you choose, that set should live there rather than only as an artifact here, and it should be versioned, because spec 36 permits validation to run only once per rubric version — so which version of the set was used is part of the result.

### G. Reconstructable access, not remembered access

If this project moves, three things need re-establishing, and each is already documented rather than remembered: the fourteen granted domains (coverage note section 5), the connector set (specification 4), and the per-connector reliability findings (coverage note 3b). Nothing needs re-discovering. Add one line to the specification recording that no credentials are stored in the project — the Crossref contact address is supplied by the platform, and the connector entitlements are account-level.

### H. Date-stamp every measurement, and re-measure rather than trust

Connector corpora, default limits, and entitlements change without notice. Every measured number in these documents carries its date for that reason. Spec 58 already requires characterisation before trust; the corollary is that a characterisation has a shelf life. Re-run the yield measurement at the start of each run series, and treat a large change as a finding about the environment rather than as noise.

### I. Environment reproducibility is already in hand

The DOI and dedupe layer is standard library only, so it runs anywhere with Python and needs no environment file. The retrieval layer depends on connectors, which are not portable — so if portability matters, the pipeline should be written so each channel is optional and the run records which channels were available. That also makes the coverage note honest when one is missing.

### J. Record identifiers once the base exists

When the Airtable base is created, record its base and table ids in the specification. They are stable, external, and impossible to guess later — and they are the one identifier worth storing, since the base itself lives in your account rather than here.

---

## 4. Priority

Items **B** and **E** are the two that matter. Everything else is either done, cheap, or a discipline to maintain. B is the difference between a tool and a transcript describing a tool; E is the difference between a project and a publication.