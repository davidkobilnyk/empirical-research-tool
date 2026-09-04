# What remains to complete the tool

**Against:** specs v3 (`research-methodology-tool-specs-v3.md`), rubric version `stage1-checklists-v0.1`, coverage map v0.4
**Date:** September 4, 2026

**Where the build stands.** Design work is substantially done and the environment is largely tested. What has *not* happened is a single end-to-end run: no question has gone through search, chaining, extraction, and audit and produced an evidence table. Spec 7 gates Stage 1 on five such runs with a clean citation audit, and the count is zero. Everything below is ordered by that fact.

Fifteen specs still carry an unmet condition: 3, 5, 11, 16, 25, 35, 38, 40, 49, 51, 53, 54, 57, 58, 60.

---

## 1. The critical path, in order

| # | Work | Spec | Owner | Done when |
|---|---|---|---|---|
| 1 | **Airtable base with the spec 45 schema** — the original eleven fields plus the six added in v3 (per-source tiers, items fired, double-count decisions, overlay result, cap applied, on-type sources) | 45 | either | A run can be logged and a grade reconstructed from the log alone |
| 2 | **Stage 0 pipeline**: search strategy written before searching, balanced query sets, chaining and saturation, access-level tagging, claim extraction and consolidation, field extraction by type, applicability and provenance tags, triage, evidence table output | 15–25, 41–43, 46 | model | An evidence table with no grades is produced from one question |
| 3 | **Route verification and tool characterisation** — confirm the OSF chain and the Retraction Watch fetch; characterise FastTrack's debate and saturation tools, SciSpace's field extraction, and Scite's citation intent on a known sample before any of them counts as evidence | 57, 58, 53 | model | Each tool has a measured result recorded in the coverage map, or is demoted to lead generator |
| 4 | **Five clean Stage 0 runs**, citation audit passing including the new retraction gate; measure runtime and cost | 7, 33, 54 | model | Spec 7 satisfied; spec 54's unknowns replaced with numbers |
| 5 | **Negligibility conventions, first set** — four checklist items and the High tier definition are inert without them | 22, 50, 60 | user decides, model drafts candidates | A convention exists per claim type, recorded and overridable |
| 6 | **Sign-off on the seven checklist draft decisions** — starting tiers, movement bounds, the two-of-three overlay cap, the code-availability item, Cannot Grade in test-retest, and the two unanchored parameters | 26, 49 | user | Rubric version promoted from draft to adopted |
| 7 | **Orientation reading** — the two handbooks, now directly reachable, plus foundational metascience reviews; anchor the two rubric parameters that lack a source, and produce the ~20-claim development set | 11, 39, 49 | model drafts, user confirms | Both parameters anchored or explicitly marked as conventions; development set exists and is logged |
| 8 | **Stage 1 runs** — grading, sealed prior, adversarial pass, cap of eight, everything labeled provisional; tune checklists on the development set only | 8, 14, 26–34, 39 | model | Grading runs end to end; checkpoint still on |
| 9 | **Validation set, 50+ claims with documented outcomes** | 35, 51 | **user only** | Set exists, disjoint from the development set, each key entry citing its source |
| 10 | **Stage 2 validation** — three runs per claim, reasoning order varied; 80% agreement, no systematic direction of error, test-retest bar met | 9, 37, 38 | model | Pass or fail recorded; run at most once per rubric version |
| 11 | **On pass:** drop the provisional label, remove the post-retrieval checkpoint, optionally add the probability output scored with Brier | 4, 5, 38, 40 | model | Grades stop being labeled provisional |
| 12 | **Stage 3 survey mode** — survey outputs, verbatim strategy and coverage note, evidence gap map, logging-driven follow-up batches, scheduled parameter re-checks | 10, 44, 47 | model | Survey output produced for one question |

---

## 2. What only you can do

- **Assemble the validation set** (35, 36). The model may surface candidates with citations but must not write the key — that is the leakage failure v1 had. Both sourcing routes are now open: the bulk Retraction Watch dataset for the retracted and refuted share, and the OSF-hosted replication databases for replication outcomes.
- **Decide the negligibility conventions** (22, 50) and sign off the seven checklist decisions (49). These are value choices about what counts as a practically meaningful effect and how harshly to penalise weak evidence; they are not empirical questions the tool can settle for itself.
- **Decide whether a second model acts as adversary** (55). Currently the adversarial pass and sealed prior share one model's blind spots, which spec 55 acknowledges. Prior dominance detected in Stage 1 is the trigger to reconsider.
- **Confirm the scope list** (2) and the precedence rule in spec 3 — that improving this tool takes priority over the decision-making tool until validation passes.

---

## 3. Open questions that still have no answer

| Spec | Question | Blocking? |
|---|---|---|
| 48 | Field base rate for metascience, needed for the prior-dominance check | No — approximable from the validation set's own established/refuted mix |
| 50 | Negligibility conventions per claim type | Yes, for four checklist items |
| 51 | How many of the 50 validation claims each source can fill, and the share of well-established claims needed to detect over-skepticism | Yes, for Stage 2 |
| 51 | How claims whose documented outcome is mixed rather than pass/fail are keyed | Yes, for Stage 2 |
| 49 | Anchors for the expert-calibration and rater-agreement premises | No — they can stay declared conventions, but then spec 37's bars are conventions too |

---

## 4. Limits that will still be true when the tool is finished

These are not tasks. They belong in the coverage note (47) so that no output overstates itself.

- No licensed index (Scopus, Web of Science, Dimensions) and no Google Scholar. Every index available here derives from OpenAlex, Semantic Scholar, PubMed, or arXiv, which is adequate for a documented survey and short of a systematic review's conventional coverage claim.
- No book-length literature, which is where much of measurement theory and philosophy of statistics lives. The two named handbooks are reachable; monographs are not.
- PubPeer is unavailable to automated access; that component of spec 16 is a manual check.
- Paywalled sources outside the OSF, arXiv, Europe PMC open-access, and Scite-served routes remain abstract-only, and spec 24 keeps that from becoming a penalty without recovering the fields.
- Single-model grading (55), unless a second model is introduced.

---

## 5. The shortest route to a working tool

Items 1 through 4 are the whole of Stage 0 and involve no judgement calls from you: schema, pipeline, tool characterisation, five clean runs with measured cost. They also produce the first real evidence about whether the retrieval layer's trusted-by-construction claim (spec 5) holds.

Items 5 through 7 are the gate into Stage 1 and mix your decisions with model drafting; they can proceed in parallel with Stage 0 since they touch the grading layer only.

Item 9 — the validation set — is the long pole and the only one nobody else can do. It is worth starting early and in parallel, because until it exists, item 11 cannot happen and every grade the tool produces stays provisional however well it performs.