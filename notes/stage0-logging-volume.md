# Stage 0 logging volume, and what it implies for the Airtable schema

**Measured September 4, 2026** on one question, with spec 16's parallel supporting and disconfirming query sets, at each connector's default limit.

## What one question actually retrieves

| Channel | Supporting arm | Disconfirming arm |
|---|---|---|
| FastTrack `search_papers` | 20 | 18 |
| Scholar Gateway `semanticSearch` (passages collapsed to articles) | 15 | 14 |
| SciSpace `search-papers` | 10 | 10 |
| Consensus `search` | 10 | 10 |

**107 records returned → 93 unique sources** after deduplication (13% duplicates). 78 carry a resolvable DOI; the remaining 15 are title-only, almost all from Consensus, which returns its own paper links rather than DOIs.

Citation chaining is a parameter rather than a measurement: seeded with three papers at `max_edges=300`, Scite returned 305 nodes and reported the cap hit. What reaches the log is therefore whatever triage keeps (spec 41), not what chaining returns.

**Two findings worth acting on.**

Only **2 of 93 sources were returned by more than one engine.** Despite drawing on overlapping upstream corpora, the four channels produce nearly disjoint result sets at these limits. This revises the earlier conclusion that the five-deep index redundancy buys nothing: for recall it evidently does. It also means deduplication is cheap and the coverage note (spec 47) should report per-channel yield, since no single channel substitutes for another.

**Deduplication needs title matching, not just DOIs.** With 15 of 93 sources arriving without a DOI, keying only on DOI silently treats the same paper from two channels as two sources — my first attempt at this measurement did exactly that and reported 0% cross-engine overlap. The pipeline needs DOI-first, normalised-title-fallback matching, and a DOI regex that survives parenthesised Elsevier DOIs.

## Rows per run, by schema choice

Assumptions, stated so they can be argued with: 10–25 candidate claims per question before the spec 42 cap of eight graded; 20–40 chained sources kept after triage; 2–5 sources cited per claim; 30–60 sources reaching field extraction; 8–12 extracted fields per source. The Airtable connector accepts up to **50 records per create call**.

| Schema | Rows per run | Create calls | Rows over the five Stage 0 runs |
|---|---|---|---|
| **A.** Claim-level only, literal spec 45 | 10–25 | 1 | 50–125 |
| **B.** A + a row per source that reaches extraction + claim-source links | 61–211 | 2–5 | 305–1,055 |
| **C.** B + a row per retrieved source | 144–284 | 3–6 | 720–1,420 |
| **D.** C + extracted fields in long format | 384–1,004 | 8–21 | 1,920–5,020 |

## Recommendation

**Schema B**, with fields stored as columns rather than rows. It logs what spec 45 needs (claim, tier, tags, rubric version, and the six v3 additions), plus an auditable source trail for the spec 33 citation audit, at 2–5 create calls per run. Schema D's long-format field storage multiplies volume by roughly five for no analytical gain, since drift detection and the prior-dominance check both operate at claim level.

Keep the full 93-source discovery list out of Airtable and in the run's coverage note (spec 47), where it belongs as evidence of search breadth. Logging every retrieved record makes the base grow with retrieval effort rather than with graded output, and it is retrieval breadth — not row count — that the coverage note is meant to demonstrate.

**One thing to check before building:** Airtable's per-base record limits are plan-dependent, and the free tier is low enough (on the order of a thousand records per base) that schema D would exhaust it during Stage 0 alone. Confirm the plan on your workspace, since it decides whether schema C or D is even available later at survey scale.

## Scaling note for Stage 3

Stage 0 and Stage 1 are single-question runs. Survey mode (spec 10) runs many questions and adds follow-up batches, so multiply by the number of questions per survey: at schema B, a twenty-question survey logs roughly 1,200–4,200 rows. That is the volume that decides the plan, not Stage 0.