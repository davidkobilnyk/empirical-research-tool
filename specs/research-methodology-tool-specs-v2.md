# Research Methodology Evidence Tool — Specifications v2

Revised September 4, 2026. Supersedes the September 4 handoff document (v1).

**Project:** a mostly-automated process that returns the most empirically validated knowledge on topics in research methodology and adjacent fields, with a calibrated sense of how much to trust each claim. The tool is used first to improve itself, then to build a separate tool for decision-making research. It is not used for decision-making research directly.

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

4. **Environment.** Runs in a Claude project using skills and connectors (FastTrack Literature, Consensus, Airtable). A post-retrieval checkpoint — a pause showing retrieved sources and candidate claims before grading — is **on by default** and is removed only after Stage 2 validation passes.

5. **Two trust layers.** The retrieval and extraction layer (sections C–E) produces auditable outputs and is trusted from Stage 1. The grading layer (sections F–G) is labeled "provisional" in every output until Stage 2 passes. Users should treat provisional grades as a structured reading aid, not a verdict.

6. **Circularity.** The rubric rests on methodology claims (e.g., that pre-registration predicts replication). Rubric parameters are recorded with the claims they rest on (spec 33). When the tool grades one of those claims at Low or below, the run output flags a rubric-revision trigger. The external ground-truth validation set (section H) is the anchor that prevents the tool from simply confirming its own assumptions; without it, this rule is cosmetic.

---

## B. Build stages

7. **Stage 0 — retrieval layer.** Build and run search, chaining, extraction, and citation audit alone. Output is the structured evidence table with no grades. Passes when the citation audit (spec 30) is clean on five runs.

8. **Stage 1 — provisional grading.** Add grading, sealed prior, and adversarial pass. Single-question runs, cap of eight claims. All grades labeled provisional.

9. **Stage 2 — validation.** Section H. Grading stops being provisional only when this passes.

10. **Stage 3 — survey mode.** Full survey outputs, logging-driven follow-up batches, scheduled parameter re-checks.

11. **Orientation reading before Stage 1:** a handful of foundational metascience reviews plus the GRADE and Cochrane handbooks, read as sources of checklist items rather than as the rubric itself. This reading also produces the development set (spec 39).

---

## C. Input handling

12. **Vague inputs** are reshaped before any search. The chosen interpretation is stated and alternatives listed.

13. **Descriptive vs. normative.** "Pre-registered studies replicate more often" is descriptive. "You should pre-register" is normative and is graded only on its descriptive basis plus stated goal assumptions. The separation is maintained throughout.

14. **Sealed prior.** Before any retrieval, the model records its own answer to the question: the claims it expects, the direction, and a tier for each. This is stored and not shown to the grading step. It replaces the introspective reflexivity note. See spec 28 for how it is used.

---

## D. Retrieval

15. **Search strategy** is written before searching and reported verbatim in the coverage note.

16. **Balanced channels.** Literature search via FastTrack, including debate mapping, is run for both supporting and disconfirming evidence with parallel query sets. In addition, a targeted disconfirmation check queries replication trackers, Retraction Watch, PubPeer, and critical commentaries for each candidate claim. This is a check, not a weighted channel; disconfirming sources are graded by the same standards as any other source.

17. **Citation chaining** forward and backward from key papers is required; FastTrack's similarity tool is the primitive. Saturation — new searches with varied phrasing stop yielding new candidate claims — is observed after chaining.

18. **Access level.** Full text where legally available (Europe PMC, preprint servers, Unpaywall); extracted fields from services with full-text access (Consensus, once evaluated); abstracts otherwise. Each source is tagged **full text**, **extracted fields**, or **abstract only**. This tag governs spec 24.

---

## E. Claim extraction and consolidation

19. **Claims come from retrieved sources**, not from the model's prior knowledge. A claim with no retrieved source is not a candidate claim.

20. **Consolidation** proceeds by constant comparison during retrieval: merge when different names cover the same construct, split when one name covers several. Merges and splits are logged with reasons.

21. **Sharpening.** Each claim states direction, population or context, and magnitude. Magnitude reference: the pooled estimate from the most recent bias-corrected meta-analysis if one exists (with a note if an older but larger or better-designed synthesis disagrees); else the original estimate; else direction-only, stated as such. Small-sample originals are flagged as likely inflated rather than numerically adjusted.

22. **Negligibility threshold.** In place of a per-claim SESOI tied to the downstream tool: each claim states the magnitude below which it would be practically negligible, using a stated convention per claim type (e.g., a fraction of the reference magnitude, or a field-standard benchmark). The convention is recorded and can be overridden by the user. This threshold is what spec 32 tests against.

---

## F. Source classification

23. **Evidence type first:** proof or analytic result; simulation; empirical meta-research (replication projects, reanalyses, observational studies of the literature); expert consensus or guideline; theoretical argument. Each is graded by its own checklist (spec 26).

24. **Extracted fields by type.**
    - *Empirical:* design (RCT, natural experiment, regression discontinuity, difference-in-differences, longitudinal, cross-sectional, pre-post), N, pre-registration status (including registered report), original vs. replication, effect size, heterogeneity and prediction interval, bias-correction method by name.
    - *Simulation:* whether parameter ranges cover realistic conditions; whether results were checked against real data with known answers; whether code is available.
    - *Proof:* stated assumptions; whether the result is asymptotic or finite-sample.
    - *Consensus/argument:* who, on what basis, whether dissent is documented.

    Missing fields are recorded as **not reported (full text checked)** or **not observable (abstract only)**. Only the first can trigger a downgrade. The pre-registration silence rule — silence after 2015 means not pre-registered for empirical primaries — applies only to full-text sources.

25. **Tags, not ratings:** applicability (field studied, era, data type, task or design type, sample characteristics) and provenance (lab of origin, whether all positive results come from one group, stated funding or conflicts). Where a claim rests on a contested construct (e.g., "research quality"), the measure is named and the contest noted.

---

## G. Grading

26. **Rubric.** Versioned. Four tiers plus abstain: **High, Moderate, Low, Very Low, Cannot Grade.** Each evidence type has a short checklist of named downgrade and upgrade conditions; every downgrade or upgrade cites the extracted field that triggered it. The checklists are adapted from GRADE, RoB 2, and ROBINS-I where those apply and written fresh for proofs, simulations, and arguments where they don't.

27. **Upgrades:** independent replication; bias-corrected synthesis surviving the most conservative method; multiverse or specification-curve robustness; convergence across evidence types. Convergence counts only when each contributing source would independently reach at least Low on its own checklist — a proof plus a weak simulation is not convergence.

28. **Statistical methods.** A method is "empirically validated" to the degree it has all three: proof of properties under stated assumptions; simulation coverage of realistic conditions; demonstrated performance on real data with known answers. The output reports which of the three are present. A method with only one cannot exceed Moderate.

29. **Weighting rules.** Replications, registered reports, and bias-corrected syntheses outweigh originals — but in methodology, a "replication" that is a reanalysis under different analytic choices is classed as a reanalysis, not a replication. Where bias-correction methods disagree, both estimates are reported and the tier follows the more conservative. Citation count is a retrieval signal only; journal prestige is neither.

30. **Reasoning before verdict.** Each grade is preceded by written reasoning: what the evidence shows, the strongest objection, and how the objection is resolved. The verdict follows. This is a necessary but not sufficient guard against rationalization; the adversarial pass and prior comparison are the substantive guards.

31. **Adversarial pass.** A separate call, with a different role prompt, receives each claim's extracted fields and provisional grade and must argue for a different tier, citing extracted fields. It specifically checks for: sources cited beyond what their retrieved text supports; the same weakness downgraded twice; "contested" calls that are really absent evidence; and whether each piece of evidence was weighed against alternative explanations. The original grade stands only if the adversarial argument fails on the evidence.

32. **Prior comparison.** After grading, the sealed prior (spec 14) is compared with the graded output. Per run, the output reports how many claims and tiers matched. Across runs, if the retrieved-evidence grades agree with the sealed prior at a rate that the validation set shows is higher than the prior's own accuracy, that is flagged as prior dominance and triggers rubric review.

33. **Citation audit.** Every cited source appears in a tool result, and its retrieved text supports the claim attributed to it. A run with an audit failure is marked invalid.

34. **Contested vs. absent.** Contested: each position stated in its strongest form, the type of disagreement named (boundary conditions, data quality, analysis method, interpretation), the conditions under which each holds, and what evidence would settle it. Failed replications are explained, not just listed. Absent: distinguished from evidence of absence by whether adequately powered studies looked and found effects below the negligibility threshold (spec 22). "Evidence of no meaningful effect" is a positive finding. Cannot Grade is reserved for genuinely absent evidence and its frequency is tracked.

---

## H. Validation

35. **Validation set: 50 or more claims with external ground truth.** Sources: outcomes of large replication projects; statistical results with mathematical or simulation-established answers; claims documented as retracted or refuted; and a deliberate share of well-established claims to detect over-skepticism. The answer key is the documented outcome, not an opinion, and each key entry cites its source. The set is assembled by the user, not drafted by the model in the grading environment.

36. **Held-out means held-out.** Nothing in the validation set is used to tune the rubric, and validation results do not trigger rubric revision directly. A separate development set (spec 39) is used for tuning. Validation is run at most once per rubric version.

37. **Test-retest.** Each validation claim runs three times independently with reasoning order varied. Any tier disagreement is recorded; a disagreement of more than one tier on more than 10% of claims fails validation. Results are aggregated as in structured expert elicitation.

38. **Pass criterion.** Validation passes when the tool reproduces the documented status on at least 80% of the held-out set, with no systematic direction of error (established claims graded low or refuted claims graded high at rates that differ), and meets the test-retest bar. Until then, all grades remain labeled provisional and the checkpoint stays on.

39. **Development set.** Roughly 20 claims drawn from the orientation reading, used to tune checklists and thresholds. It is disjoint from the validation set and its use is logged.

40. **Probability output** may be added after validation passes, defined as the chance that a large, independent, pre-registered test finds an effect above the negligibility threshold, and scored with Brier on the validation set. Until then it is not produced.

---

## I. Triage and cap

41. **Triage** ranks candidate claims by centrality to the input question, with gradeability as a floor. Where the question is about improving this tool, centrality to rubric parameters ranks first. Triage reasons are stored and collapsed by default.

42. **Cap** of eight graded claims per run, tuned after first runs.

43. **Surfaced but ungraded.** Claims beyond the cap or failing triage are listed with one-line reasons. A follow-up request passes prior claim IDs as exclusions and grades from the surfaced pool first.

---

## J. Tracking

44. **Rubric versioning.** Each output records the rubric version and the metascience claims its parameters rest on. When the rubric changes, logged claims graded under the previous version are marked stale; they are regraded on the next run that touches them or on request. Parameters are re-checked against current metascience on a schedule.

45. **Logging to Airtable** is required: claim ID, sharpened claim, tier, provisional flag, applicability tags, evidence-type mix, access-level mix, prior-match flag, abstain, rubric version, run date. Supports follow-up batches, drift detection, and the prior-dominance check.

---

## K. Output

46. **Summary table first:** claim, tier (with provisional flag), applicability summary including prediction interval where available, best-supported version in one line. **Per-claim detail below:** best-supported version, effect sizes in practical units with intervals, which of the three method-validation standards are met where relevant, what would change the grade, sources with access level. Reasoning, adversarial-pass results, triage log, and prior comparison collapsed by default.

47. **Survey outputs** add the verbatim search strategy, coverage note, and an evidence gap map: what was studied, by what evidence type, and what wasn't.

---

## L. Open questions for the new chat

48. **Field base rate.** Metascience has no replication-rate estimate of its own. With the probability output deferred, this is needed only for the prior-dominance check (spec 32) and can be approximated from the validation set's own established/refuted mix initially.

49. **Checklist contents** for proofs, simulations, and arguments (spec 26) need drafting from the orientation reading.

50. **Negligibility conventions** (spec 22) per claim type need a first set.

51. **Validation set sourcing.** Which replication projects and known-answer statistical results are usable, and how many of the 50 can be filled from each.

---

## M. Known limits

52. Abstract-only access for a substantial fraction of sources; spec 24 prevents this from becoming a penalty but cannot recover the missing fields.

53. FastTrack's debate-mapping and saturation tools are unassessed; Consensus is not yet loaded.

54. Run time, cost, and environment reliability unknown until Stage 0.

55. Single-model grading. The adversarial pass and sealed prior reduce but do not remove shared bias; a second model as adversary is the natural next step if prior dominance is detected.

56. The validation set's ground truth is itself a judgment about the empirical record, though a far more constrained one than v1's. Documented outcomes can be revised; the set should be re-checked when the rubric parameters are.
