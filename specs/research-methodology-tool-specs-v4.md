# Research Methodology Evidence Tool — Specifications v3

Revised September 4, 2026. Supersedes v2 of the same date, which superseded the v1 handoff document.

**Numbering is stable.** Specs 1–56 keep the meaning they had in v2, so earlier references by number remain valid; amended specs are listed below and new requirements are appended as 57–60.

**Project:** a mostly-automated process that returns the most empirically validated knowledge on topics in research methodology and adjacent fields, with a calibrated sense of how much to trust each claim. The tool is used first to improve itself, then to build a separate tool for decision-making research. It is not used for decision-making research directly.

---


## Scope of v4

v4 is a **transparency tool**: it finds sources, tells you what they are and what they
report, shows you how the list was made, and stops. The grading layer specified in v2 and v3
is deferred — its specs are retained, marked, and out of scope.

Why the change, recorded so the reasoning survives the decision:

- v3's own two-layer split held retrieval and extraction trusted and grading provisional
  until validated. Dropping the grading layer puts everything the tool ships inside the
  trusted layer: no provisional labels, and no output whose meaning depends on a validation
  set that does not yet exist.
- The grading gates were blocking the tool from being used at all. Five clean runs, a 50-claim
  validation set, negligibility conventions and seven rubric decisions all stood between the
  specification and any usable output, and none of them could be settled without experience
  of the output they were gating.
- Grading consumes the evidence table; it does not produce it. Deferring it costs nothing
  structurally, and the checklist draft's trigger fields survive as the dossier's metadata
  fields — the fields a rubric would need in order to downgrade a source are the fields a
  reader needs in order to evaluate it. Removing the verdicts and keeping the fields is the
  whole of the change.

What is in scope: retrieval across channels with balanced query sets, source identity and
de-duplication to the level of works, retraction and correction status, access level,
descriptive per-source extraction with verbatim quotes, the coverage note, and the dossier.

What is out of scope: tiers, scores, confidence, weighting, ranking by quality, synthesis,
answering the question, the sealed prior, the adversarial pass, and validation of grades.

## What changed from v2 and why

Two things happened after v2 was written: the Stage 1 checklists were drafted, and the retrieval environment was tested rather than assumed. Both produced changes here.

**From drafting the checklists (spec 49, now closed).** The rubric needed things v2 named but did not define. Spec 26 now defines the tier scale operationally and points at the checklists as a *versioned companion document*, so that revising an item is a rubric version change rather than a specification change. Spec 37 now fixes tier adjacency and puts Cannot Grade off-scale, without which its own one-tier tolerance had nothing to measure. Spec 28 now covers the two-of-three case it left open. Spec 45 gains six logging fields, because the v2 field list could not reconstruct a grade.

**From testing the environment.** v2 assumed a retrieval environment; most of it is now measured, and three assumptions were wrong. Retraction status needs no new tooling — Crossref carries it per DOI and distinguishes retraction from correction — so spec 16 names it concretely and spec 33 makes it an audit gate, since a run citing a retracted source should fail rather than footnote it. Scite's citation intent turned out too sparse to evidence dissent, so spec 16 demotes it to a lead generator and spec 53 records the measurement. PubPeer refuses automated clients at its origin, so its component of spec 16 is manual. Conversely, OSF-hosted preprints are now retrievable as full text, which matters because spec 24 lets only full-text sources trigger a downgrade — while that route was closed, the tool was structurally unable to grade the metascience preprint literature at full strength.

**New requirements (57–60)** cover what those tests showed the specification had no rule for: verifying multi-hop retrieval routes instead of silently degrading to abstract-only; characterising a tool before trusting its output, which is spec 5's trust-layer logic applied to tools; preferring a lookup over a source's self-report where both exist; and recording that four checklist items are inert until the negligibility conventions of spec 50 exist.

**Also changed:** spec 4 lists the current connector and API set; spec 11 records that both handbooks are now directly reachable; spec 35 and spec 51 name the two sourcing routes that turn validation-set assembly into filtering, without weakening spec 35's rule that the user assembles it; spec 52 narrows the abstract-only limitation to what is actually still paywalled.

**Not changed:** the two-layer trust split (spec 5), the sealed prior (14), the removal of the probability output (40), the held-out discipline (36), the cap of eight (42), and the requirement that the user assemble the validation set (35). Nothing here makes grading less provisional; Stage 2 remains the only thing that can.

---

## What changed from v1 and why

The tool is now split into two layers with different trust levels. The **retrieval and extraction layer** (search, chaining, field extraction, citation audit) is reliable by construction and is trusted from the first run. The **grading layer** (tiers, verdicts) is treated as provisional until it passes validation against external ground truth. This replaces v1's assumption that the whole pipeline was trustworthy once built.

Specific changes:

- **Validation set** is larger (50+), sourced from documented replication outcomes and known statistical results rather than drafted in chat, and is no longer used to trigger rubric revision (v1 specs 39–41 leaked the held-out set).
- **Probability output** (v1 spec 30) is removed until grading is validated. It was never scored against its own defined event, rested on a base rate that doesn't exist, and duplicated the tier while looking like an independent forecast.
- **Rubric** no longer formally adopts GRADE, RoB 2, ROBINS-I, and CERQual. Those fit clinical evidence; most methodology evidence is proofs, simulations, reanalyses, and arguments. Replaced with short evidence-type checklists and an explicit combination rule.
- **Model prior bias** is now addressed directly with a sealed prior verdict recorded before retrieval, replacing the unreliable introspective reflexivity note (v1 spec 14).
- **"Not reported" handling** distinguishes abstract-only from full-text-checked, and no downgrade is applied for fields that cannot be observed at the access level available (v1 specs 23, 25, 53 together penalized paywalled papers).
- **Negative-evidence channel** is no longer structurally asymmetric. Both supporting and disconfirming evidence are searched for; targeted disconfirmation sources are kept.
- **Triage and SESOI** are no longer anchored to the undesigned downstream tool. Triage is by centrality and gradeability; magnitude thresholds use a stated convention.
- **Post-retrieval checkpoint** is on by default until validation passes, rather than added only after a failure rate is observed.
- **Removed as low value for cost:** member-check step, realist context–mechanism–outcome format, formal Toulmin labels, Type M magnitude adjustment (kept as a flag), jingle-jangle terminology (merge/split rule kept), reliability-criterion threshold (spec 44), registered-report vs. pre-registered distinction as a separate upgrade (kept as a field).
- **Added:** regrading policy when the rubric changes; a defined tier scale so test-retest tolerance means something; a rule for what "empirically validated" means for a statistical method.

---

## A. Purpose and scope

1. **Input and output.** Input is a question about research methodology. Output is the set of claims the literature makes in answer, each with extracted evidence fields, a provisional grade, and applicability tags. The tool assesses evidence; it does not recommend practice.

2. **Fields in scope.** Metascience; statistics and psychometrics; meta-analysis and publication-bias methods; causal inference; measurement theory; systematic review methodology; evidence-based medicine (as the source of most grading tools); simulation methodology; philosophy of science and philosophy of statistics; information retrieval and scientometrics; qualitative methodology; structured expert elicitation and forecasting/calibration science; argumentation theory; research integrity and open science; LLM and AI-system evaluation; judgment and decision-making methodology (the eventual target domain). The list is provisional and the tool can be asked about it.

3. **Two uses, in order.** First, improving this tool: claims about evidence synthesis, rater reliability, calibration, and structured judgment feed directly into rubric revision. Second, building the decision-making research tool. Where these pull in different directions, the first takes precedence until validation passes.

4. **Environment.** Runs in a Claude project using skills and connectors. Retrieval and extraction: FastTrack Literature, Consensus, SciSpace, Scholar Gateway, alphaXiv, Scite, and platform servers for PubMed, OpenAlex/arXiv, and ClinicalTrials.gov. Logging: Airtable. Direct API access is additionally granted for Europe PMC, the OSF API and its file hosts, Zenodo, Crossref including the bulk Retraction Watch dataset at Crossref Labs, PROSPERO (page access only), PhilPapers (OAI-PMH only), and the Cochrane and GRADE handbooks. Per-tool routes and measured reliability are held in the source-coverage companion document, not here, because they change without the specification changing. A post-retrieval checkpoint — a pause showing retrieved sources and candidate claims before grading — is **on by default** and is removed only after Stage 2 validation passes.

5. **Two trust layers.** The retrieval and extraction layer (sections C–E) produces auditable outputs and is trusted from Stage 1. The grading layer (sections F–G) is labeled "provisional" in every output until Stage 2 passes. Users should treat provisional grades as a structured reading aid, not a verdict.

6. **Circularity.** The rubric rests on methodology claims (e.g., that pre-registration predicts replication). Rubric parameters are recorded with the claims they rest on (spec 33). When the tool grades one of those claims at Low or below, the run output flags a rubric-revision trigger. The external ground-truth validation set (section H) is the anchor that prevents the tool from simply confirming its own assumptions; without it, this rule is cosmetic.

---

## B. Build stages

7. **The tool: an evidence dossier.** Given a question, the tool searches, identifies and de-duplicates sources, extracts descriptive metadata from the text each channel returned, and presents the result for the reader to evaluate. It produces no grade, no score, no ranking and no synthesised answer. Passes when a run produces a dossier in which every source is accounted for and every extracted field is either traceable to a quoted span or marked not stated (specs 61-65).

8. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Stage 1 — provisional grading.** Add grading, sealed prior, and adversarial pass. Single-question runs, cap of eight claims. All grades labeled provisional.

9. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Stage 2 — validation.** Section H. Grading stops being provisional only when this passes.

10. **Survey mode (later).** Many questions per run, with the same dossier output per question plus an evidence-gap map. Out of scope until single-question runs have been used enough to know what the output should contain.

11. **Orientation reading before Stage 1:** a handful of foundational metascience reviews plus the GRADE and Cochrane handbooks, read as sources of checklist items rather than as the rubric itself. Both handbooks are directly reachable (`training.cochrane.org`, `gdt.gradepro.org`). The Stage 1 checklists were drafted from the GRADE journal series and the named tool papers rather than the handbooks themselves; two items still need the handbooks' own wording, and two rubric parameters need an anchor that this reading is expected to supply (spec 49). This reading also produces the development set (spec 39).

---

## C. Input handling

12. **Vague inputs** are reshaped before any search. The chosen interpretation is stated and alternatives listed.

13. **Descriptive vs. normative.** "Pre-registered studies replicate more often" is descriptive. "You should pre-register" is normative and is graded only on its descriptive basis plus stated goal assumptions. The separation is maintained throughout.

14. **Sealed prior.** Before any retrieval, the model records its own answer to the question: the claims it expects, the direction, and a tier for each. This is stored and not shown to the grading step. It replaces the introspective reflexivity note. See spec 28 for how it is used.

---

## D. Retrieval

15. **Search strategy** is written before searching and reported verbatim in the coverage note.

16. **Balanced channels.** Literature search, including debate mapping, is run for both supporting and disconfirming evidence with parallel query sets. Those parallel sets are the load-bearing part of this requirement; the per-claim checks below supplement them and do not replace them. The targeted disconfirmation check runs, for each candidate claim: **retraction and correction status** from the Crossref `updated-by` field, which distinguishes a retraction from a correction and names the notice DOI (reliable, and also a spec 33 gate); **replication outcomes** from the databases named in spec 51; **citing-paper stance** from Scite citation intent, used as a lead generator only, because measured intent labels are sparse and skewed toward 'mentioning' (spec 53); and **PubPeer** as a manual check, its origin refusing automated clients. This is a check, not a weighted channel; disconfirming sources are graded by the same standards as any other source.

17. **Citation chaining** forward and backward from key papers is required; FastTrack's similarity tool is the primitive. Saturation — new searches with varied phrasing stop yielding new candidate claims — is observed after chaining.

18. **Access level.** Full text where legally available: Europe PMC for its open-access and in-EPMC subset; OSF for OSF-hosted preprints, which much of the metascience literature uses; alphaXiv for arXiv; PMC via the PubMed server; and Scite's full-text read, which returns an explicit flag separating served full text from a fallback abstract. Each source is tagged **full text**, **extracted fields**, or **abstract only**, and the tag is taken from that flag or from the retrieval route actually used — never inferred from the publisher or from whether a paywall was expected. This tag governs spec 24.

---

## E. Claim extraction and consolidation

19. **Claims come from retrieved sources**, not from the model's prior knowledge. A claim with no retrieved source is not a candidate claim.

20. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Consolidation** proceeds by constant comparison during retrieval: merge when different names cover the same construct, split when one name covers several. Merges and splits are logged with reasons.

21. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Sharpening.** Each claim states direction, population or context, and magnitude. Magnitude reference: the pooled estimate from the most recent bias-corrected meta-analysis if one exists (with a note if an older but larger or better-designed synthesis disagrees); else the original estimate; else direction-only, stated as such. Small-sample originals are flagged as likely inflated rather than numerically adjusted.

22. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Negligibility threshold.** In place of a per-claim SESOI tied to the downstream tool: each claim states the magnitude below which it would be practically negligible, using a stated convention per claim type (e.g., a fraction of the reference magnitude, or a field-standard benchmark). The convention is recorded and can be overridden by the user. This threshold is what spec 32 tests against.

---

## F. Source classification

23. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Evidence type first:** proof or analytic result; simulation; empirical meta-research (replication projects, reanalyses, observational studies of the literature); expert consensus or guideline; theoretical argument. Each is graded by its own checklist (spec 26).

24. **Extracted fields by type.**
    - *Empirical:* design (RCT, natural experiment, regression discontinuity, difference-in-differences, longitudinal, cross-sectional, pre-post), N, pre-registration status (including registered report), original vs. replication, effect size, heterogeneity and prediction interval, bias-correction method by name.
    - *Simulation:* whether parameter ranges cover realistic conditions; whether results were checked against real data with known answers; whether code is available.
    - *Proof:* stated assumptions; whether the result is asymptotic or finite-sample.
    - *Consensus/argument:* who, on what basis, whether dissent is documented.
    - *All types:* retraction and correction status, from Crossref `updated-by` — the type, the source, and the notice DOI.
    - *Simulation and empirical:* code or data deposit, resolved by lookup (Zenodo, OSF, or the paper's repository) rather than taken from the source's own availability statement (spec 59).

    Missing fields are recorded as **not reported (full text checked)** or **not observable (abstract only)**. Only the first can trigger a downgrade. The pre-registration silence rule — silence after 2015 means not pre-registered for empirical primaries — applies only to full-text sources.

25. **Tags, not ratings:** applicability (field studied, era, data type, task or design type, sample characteristics) and provenance (lab of origin, whether all positive results come from one group, stated funding or conflicts). Where a claim rests on a contested construct (e.g., "research quality"), the measure is named and the contest noted.

---

## G. Grading

26. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Rubric.** Versioned. Four tiers plus abstain: **High, Moderate, Low, Very Low, Cannot Grade.** The tier scale is defined operationally in terms of evidence state and what would move it, not in terms of likelihood, so that spec 40's removal of the probability output is not undone by the tier definitions; tier adjacency is fixed so that spec 37's tolerance is meaningful. Each evidence type has a short checklist of named downgrade and upgrade conditions; every downgrade or upgrade cites the extracted field that triggered it. The checklists are adapted from GRADE, RoB 2, and ROBINS-I where those apply and written fresh for proofs, simulations, and arguments where they don't. **The checklist contents are a versioned companion document** (current rubric version `stage1-checklists-v0.1`), holding the tier scale, a starting tier per evidence type, items across the five evidence types, an explicit combination rule, a double-count register, and the adversarial-pass and sealed-prior checklists. Amending the checklists is a rubric version change under spec 44; amending this specification is not.

27. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Upgrades:** independent replication; bias-corrected synthesis surviving the most conservative method; multiverse or specification-curve robustness; convergence across evidence types. Convergence counts only when each contributing source would independently reach at least Low on its own checklist — a proof plus a weak simulation is not convergence.

28. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Statistical methods.** A method is "empirically validated" to the degree it has all three: proof of properties under stated assumptions; simulation coverage of realistic conditions; demonstrated performance on real data with known answers. The output reports which of the three are present. A method with only one cannot exceed Moderate. Where two are present the tier is also capped at Moderate, unless the missing standard is argued non-applicable and that argument is recorded; where all three are present no overlay cap applies.

29. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Weighting rules.** Replications, registered reports, and bias-corrected syntheses outweigh originals — but in methodology, a "replication" that is a reanalysis under different analytic choices is classed as a reanalysis, not a replication. Where bias-correction methods disagree, both estimates are reported and the tier follows the more conservative. Citation count is a retrieval signal only; journal prestige is neither.

30. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Reasoning before verdict.** Each grade is preceded by written reasoning: what the evidence shows, the strongest objection, and how the objection is resolved. The verdict follows. This is a necessary but not sufficient guard against rationalization; the adversarial pass and prior comparison are the substantive guards.

31. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Adversarial pass.** A separate call, with a different role prompt, receives each claim's extracted fields and provisional grade and must argue for a different tier, citing extracted fields. It specifically checks for: sources cited beyond what their retrieved text supports; the same weakness downgraded twice; "contested" calls that are really absent evidence; and whether each piece of evidence was weighed against alternative explanations. The original grade stands only if the adversarial argument fails on the evidence.

32. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Prior comparison.** After grading, the sealed prior (spec 14) is compared with the graded output. Per run, the output reports how many claims and tiers matched. Across runs, if the retrieved-evidence grades agree with the sealed prior at a rate that the validation set shows is higher than the prior's own accuracy, that is flagged as prior dominance and triggers rubric review.

33. **Citation audit.** Every source shown appears in a tool result, carries the identifiers the tool reports for it, and — where a field asserts what the source found — a verbatim span from the retrieved text supporting that field. Retraction and correction status is checked for every source via Crossref `updated-by`. The audit is now a property of the dossier rather than a gate on grading: a field with no locatable span is displayed as unsupported, not suppressed.

34. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Contested vs. absent.** Contested: each position stated in its strongest form, the type of disagreement named (boundary conditions, data quality, analysis method, interpretation), the conditions under which each holds, and what evidence would settle it. Failed replications are explained, not just listed. Absent: distinguished from evidence of absence by whether adequately powered studies looked and found effects below the negligibility threshold (spec 22). "Evidence of no meaningful effect" is a positive finding. Cannot Grade is reserved for genuinely absent evidence and its frequency is tracked.

---

## H. Validation

35. **Validation set: 50 or more claims with external ground truth.** Sources: outcomes of large replication projects; statistical results with mathematical or simulation-established answers; claims documented as retracted or refuted; and a deliberate share of well-established claims to detect over-skepticism. Two routes reduce assembly to filtering rather than trawling: the bulk Retraction Watch dataset, one CSV of roughly 72,000 rows carrying subject, retraction nature, documented reason, and original-paper DOI, for the retracted and refuted share; and the replication databases in spec 51 for replication outcomes. The answer key is the documented outcome, not an opinion, and each key entry cites its source. The set is assembled by the user, not drafted by the model in the grading environment; the model may surface candidates with their citations but does not write the key.

36. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Held-out means held-out.** Nothing in the validation set is used to tune the rubric, and validation results do not trigger rubric revision directly. A separate development set (spec 39) is used for tuning. Validation is run at most once per rubric version.

37. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Test-retest.** Each validation claim runs three times independently with reasoning order varied. Any tier disagreement is recorded; a disagreement of more than one tier on more than 10% of claims fails validation. Tiers are adjacent in the order High–Moderate–Low–Very Low. **Cannot Grade is off-scale:** any disagreement between Cannot Grade and a rated tier counts as more than one tier, and therefore against the 10% bar, which makes abstention behaviour part of what validation tests. Results are aggregated as in structured expert elicitation.

38. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Pass criterion.** Validation passes when the tool reproduces the documented status on at least 80% of the held-out set, with no systematic direction of error (established claims graded low or refuted claims graded high at rates that differ), and meets the test-retest bar. Until then, all grades remain labeled provisional and the checkpoint stays on.

39. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Development set.** Roughly 20 claims drawn from the orientation reading, used to tune checklists and thresholds. It is disjoint from the validation set and its use is logged.

40. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Probability output** may be added after validation passes, defined as the chance that a large, independent, pre-registered test finds an effect above the negligibility threshold, and scored with Brier on the validation set. Until then it is not produced.

---

## I. Triage and cap

41. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Triage** ranks candidate claims by centrality to the input question, with gradeability as a floor. Where the question is about improving this tool, centrality to rubric parameters ranks first. Triage reasons are stored and collapsed by default.

42. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Cap** of eight graded claims per run, tuned after first runs.

43. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Surfaced but ungraded.** Claims beyond the cap or failing triage are listed with one-line reasons. A follow-up request passes prior claim IDs as exclusions and grades from the surfaced pool first.

---

## J. Tracking

44. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Rubric versioning.** Each output records the rubric version and the metascience claims its parameters rest on. When the rubric changes, logged claims graded under the previous version are marked stale; they are regraded on the next run that touches them or on request. Parameters are re-checked against current metascience on a schedule.

45. **Logging to Airtable** is required: claim ID, sharpened claim, tier, provisional flag, applicability tags, evidence-type mix, access-level mix, prior-match flag, abstain, rubric version, run date. Six further fields are required for a grade to be reconstructable from the log rather than re-derived: per-source tier before combination; the IDs of every checklist item that fired, each with the field that triggered it; the double-count decisions taken; which of the three method-validation standards were met; which cap bound the tier, if any; and which sources were treated as on-type for the claim. Supports follow-up batches, drift detection, and the prior-dominance check.

---

## K. Output

46. **Summary table first:** claim, tier (with provisional flag), applicability summary including prediction interval where available, best-supported version in one line. **Per-claim detail below:** best-supported version, effect sizes in practical units with intervals, which of the three method-validation standards are met where relevant, what would change the grade, sources with access level. Reasoning, adversarial-pass results, triage log, and prior comparison collapsed by default.

47. **Survey outputs** add the verbatim search strategy, coverage note, and an evidence gap map: what was studied, by what evidence type, and what wasn't.

---

## L. Open questions for the new chat

48. **Field base rate.** Metascience has no replication-rate estimate of its own. With the probability output deferred, this is needed only for the prior-dominance check (spec 32) and can be approximated from the validation set's own established/refuted mix initially.

49. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Checklist contents** for proofs, simulations, and arguments (spec 26) — **drafted** as rubric version `stage1-checklists-v0.1`, generated from a single item table so the document and its machine-readable copy cannot drift. What remains: sign-off on the seven draft decisions recorded there (starting tiers, total-movement bounds, the two-of-three overlay cap, the code-availability item, Cannot Grade's treatment in test-retest, and the two unanchored parameters), and anchoring those two parameters — the expert-calibration premise behind the consensus upgrade, and the rater-agreement premise behind the tier scale and spec 37's tolerance. Until the second is anchored, the one-tier and 10% bars are conventions, not calibrated thresholds.

50. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Negligibility conventions** (spec 22) per claim type need a first set.

51. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] **Validation set sourcing.** Concrete routes now exist and are reachable: the bulk Retraction Watch dataset for retracted and refuted claims; OSF for the FORRT Replication Database and for the project-level datasets of the large replication projects (Reproducibility Project: Psychology, Many Labs 1–5, the Social Sciences Replication Project, Reproducibility Project: Cancer Biology, ManyBabies); ReplicationWiki for economics; Curate Science if it proves still maintained. Open: how many of the 50 each source can fill, what share of well-established claims is needed to detect over-skepticism, and how claims whose documented outcome is mixed rather than pass or fail are handled.

---

## M. Known limits

52. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] Abstract-only access for a fraction of sources — reduced but not eliminated. OSF-hosted preprints, arXiv, the Europe PMC open-access subset, and papers Scite serves as full text are now genuinely full text; paywalled sources outside those routes stay abstract-only. Spec 24 prevents this from becoming a penalty but cannot recover the missing fields.

53. FastTrack's debate-mapping and saturation tools remain unassessed, as does SciSpace's field extraction. Scite's citation intent is characterised and thin: on one 40-edge sample it returned 26 *mentioning*, 1 *supporting*, 14 unlabeled and no *contrasting* edge, and preprint DOIs resolved no edges at all — so it generates leads and does not evidence dissent. Consensus is loaded and reachable; the v2 statement that it was not is superseded. PubPeer is unavailable to automated access at its origin, so spec 16's PubPeer component is manual. No licensed index (Scopus, Web of Science, Dimensions) and no book-length literature is reachable, which bounds what spec 47's coverage note may claim.

54. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] Run time, cost, and environment reliability unknown until Stage 0.

55. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] Single-model grading. The adversarial pass and sealed prior reduce but do not remove shared bias; a second model as adversary is the natural next step if prior dominance is detected.

56. **[DEFERRED in v4 — grading layer.** Retained for its numbering and its design, not in scope for the shipped tool. See Scope of v4.] The validation set's ground truth is itself a judgment about the empirical record, though a far more constrained one than v1's. Documented outcomes can be revised; the set should be re-checked when the rubric parameters are. Where a key entry rests on a retraction, note that the documented reason is a publisher or journal determination — constrained and citable, but not a neutral adjudication.

---

## N. Operating rules added in v3

57. **Route verification.** Retrieval routes with more than one hop or a signed URL are verified at the start of each run series rather than assumed. The OSF download chain is the current instance: the API's download link redirects twice, ending at a signed URL in a specific storage bucket, and the final URL must be rewritten to its bucket-qualified form. A route failure is a retrieval-layer failure — it invalidates the run under spec 7's criterion and is never allowed to degrade silently into an abstract-only tag, because that would convert a fixable access problem into a permanent evidence gap.

58. **Tool characterisation before trust.** A connector's output is used as evidence only after it has been characterised on a sample with a known answer; before that it is a lead generator whose output must be confirmed by a second route. This is spec 5's trust-layer rule applied to tools rather than to layers, and it currently binds FastTrack's debate-mapping and saturation tools, SciSpace's field extraction, and Scite's citation intent. Characterisation results are recorded in the source-coverage companion document with the sample they were measured on.

59. **Lookup over self-report.** Where a field can be resolved by lookup — code or data availability, retraction or correction status, pre-registration in a registry — the lookup takes precedence over the source's own statement about itself, and the output records which was used. A source claiming its code is available is evidence about the claim, not about the code.

60. **Dependency on the negligibility conventions.** Four checklist items — the imprecision downgrade, the bias-correction-failure downgrade, the robustness upgrade — and the High tier definition depend on spec 22 and the conventions still owed under spec 50. Until a first set exists, those items fire on direction and interval width alone, and the run output states that they did.

## Specs added in v4 — transparency requirements

61. **No evaluative output.** The tool assigns no tier, score, confidence, weight or quality
    ranking, and produces no synthesised answer to the question. Where two sources report
    opposite findings, both are shown with equal prominence and reconciling them is the
    reader's work. Descriptive fields that report *what a source found* are in scope; fields
    that report *how good a source is* are not. The distinction is the boundary of the tool.

62. **Selection and ordering are stated in the output.** Which sources appear, and in what
    order, are decisions that can smuggle evaluation into a tool that claims to make none.
    Every dossier states the channels searched, the inclusion rule as executed, and the
    ordering rule, above the source list. Ordering defaults to something with no plausible
    reading as merit — alphabetical by title — and never to a relevance score.

63. **Nothing is dropped silently.** Every source a search returned but the dossier does not
    show is listed with the reason it was excluded and a count. A metadata gap is not grounds
    for exclusion: a source whose record carries no DOI is shown and marked as not
    integrity-checkable, because hiding it would misrepresent the evidence base in exactly
    the direction the tool is meant to expose.

64. **Absence is recorded as absence.** Every extracted field is either a value the retrieved
    text states or the literal value "not stated". "Not stated" is a finding about what the
    source's retrieved text says, and the output distinguishes it from a field that was never
    examined. Nothing is inferred from outside the retrieved text.

65. **Quotes are the audit surface.** Any field asserting what a source found carries a
    verbatim span from the retrieved text, checked mechanically against that text. The check
    reports three outcomes and shows all three: found, found with elision (every word present
    in order, with material omitted between), and not found. A not-found span is grounds for
    distrusting every field on that source, and the output says so rather than removing the
    quote.

66. **The extraction is machine-produced and labelled as such.** The dossier states that the
    metadata was extracted by a model from the text a channel returned — for most sources an
    abstract or a passage, not the full paper — and therefore that "not stated" may reflect the
    snippet rather than the paper.

67. **Retracted sources are excluded and named.** A source with a retraction notice is
    excluded from the dossier and listed in the exclusions with its notice. Corrections are
    not retractions: a corrected source is shown with its correction status. This replaces the
    v3 arrangement in which a retracted source failed a run outright.

68. **Grading returns only after use.** The grading layer (specs marked deferred) is
    reconsidered only after the dossier output has been used on real questions and the
    extraction's failure modes are known from that use. The validation set of spec 35 remains
    the precondition for any grade leaving the tool, and no grade is shown before it passes.
