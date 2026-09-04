---
name: doi-source-identity
description: Extract, normalise and validate DOIs from free text or connector output; deduplicate retrieval results across literature search channels; check retraction and correction status via Crossref. Use when building or auditing a literature-retrieval pipeline, merging results from several paper-search connectors, or verifying that cited sources exist and are not retracted.
---

# DOI handling and source identity

Helpers for the step every literature pipeline starts with: turning messy
retrieval output into a set of uniquely identified, existent, non-retracted
sources. `kernel.py` loads with this skill, so the functions below already
exist in the python kernel.

## Why not just a regex

DOI suffixes legitimately contain parentheses, angle brackets, colons,
semicolons and square brackets. A restrictive character class silently
truncates exactly the publishers that use them — Elsevier's parenthesised
style and Wiley's older SICI style — and a truncated DOI is worse than a
missing one, because it looks valid and resolves to nothing.

`normalize_doi` therefore captures broadly and trims afterwards, removing
closing brackets only when they are unbalanced. That is what lets
`(10.1002/(SICI)1521-3773(19980703)37:12<1717::AID-ANIE1717>3.0.CO;2-T).`
lose its wrapper without losing its own brackets.

The converse also holds: any pattern permissive enough to keep that DOI will
accept a fabricated one. **Pattern-match, then validate.**

## Functions

| Call | Returns |
|---|---|
| `normalize_doi(s)` | Canonical lowercase DOI from a bare string, a `https://doi.org/...` URL, a `doi:` prefix, or one embedded mid-sentence. `None` if there is no DOI. |
| `extract_dois(text)` | Every distinct DOI in free text, normalised, order preserved. |
| `doi_exists(doi, email=None)` | `True` / `False` / `None`. **`None` means the check failed** (network or server), not that the DOI is absent — never treat it as `False`. |
| `normalize_title(t)` | Accent- and punctuation-stripped title, for use as a fallback identity. |
| `dedupe_sources(records)` | `(unique, index)` — canonical key to record, and canonical key to the set of channels that returned it. |
| `crossref_record(doi, email=None)` | Full Crossref message, or `None`. |
| `retraction_status(doi, email=None)` | `{'retracted', 'corrected', 'notices'}`, or `None` if unfetchable. |

Pass `email` where a contact address is available; obtain it from
`host.get_user_email()` and omit the argument if that raises.

## Deduplicating across search channels

Key on DOI first, normalised title second. Some connectors return their own
paper links rather than DOIs, so a DOI-only key treats the same paper from two
channels as two sources — and, worse, reports near-zero cross-channel overlap,
which looks like evidence that the channels are complementary when it is an
artefact of the key.

```python
recs = [{"channel": "engine_a", "doi": "10.1002/sim.8086", "title": "..."},
        {"channel": "engine_b", "doi": None, "title": "Using simulation studies ..."}]
unique, index = dedupe_sources(recs)
len(unique)                                  # distinct sources
sum(1 for ch in index.values() if len(ch) > 1)   # found by more than one channel
```

Report per-channel yield alongside the deduplicated total. Channels drawing on
overlapping upstream corpora can still return largely disjoint sets at default
limits, so measure the overlap rather than assuming it.

## Validating a citation list

```python
for doi in extract_dois(manuscript_text):
    ok = doi_exists(doi, email)
    rs = retraction_status(doi, email)
    if ok is False:
        ...   # DOI does not resolve: not a citable source
    elif rs and rs["retracted"]:
        ...   # cited source is retracted
    elif ok is None or rs is None:
        ...   # unknown, not clean -- re-check rather than pass
```

Keep "unknown" distinct from "clean" in whatever you write out. Both
`doi_exists` and `retraction_status` return `None` on a failed lookup
specifically so that a network problem cannot be recorded as a passing check.

Retraction and correction notices come from the same Crossref record as the
existence check, so one fetch answers both; `retraction_status` distinguishes
`type: "retraction"` from `type: "correction"`, which matters because a
corrigendum is not a retraction and should not be treated as one.
