"""Builds the Stage 1 grading-checklist draft (markdown) and a machine-readable
item table (CSV) from one shared list of checklist items, so the two cannot drift.

Inputs: handoff_refs.json (Crossref-verified anchor references).
Outputs: stage1-grading-checklists-v0.1.md, stage1-checklist-items-v0.1.csv
"""
import csv, json

REFS = json.load(open("handoff_refs.json"))

# ---------------------------------------------------------------- references
# key -> (crossref key or explicit dict, short label used in the Anchor column)
ANCHOR_PICK = {
    "GRADE_intro":        (0, "GRADE"),
    "GRADE_imprecision":  (2, "GRADE-6"),
    "GRADE_inconsistency":(1, "GRADE-7"),
    "GRADE_pubbias":      (2, "GRADE-5"),
    "RoB2":               (None, "RoB 2"),
    "ROBINS_I":           (None, "ROBINS-I"),
    "ADEMP":              (0, "ADEMP"),
    "TRISS":              (None, "TRISS"),
    "siepe_simtemplate":  (1, "Siepe"),
    "neutral_comparison": (0, "Boulesteix"),
    "multiverse":         (0, "Multiverse"),
    "spec_curve":         (0, "Spec-curve"),
    "vibration_effects":  (0, "Vibration"),
    "pred_interval":      (0, "IntHout"),
    "bias_correction_cmp":(1, "Carter"),
    "OSC2015":            (0, "OSC 2015"),
    "camerer2018":        (None, "Camerer"),
    "nosek_preregistration": (1, "Nosek"),
    "gelman_loken":       (0, "Forking paths"),
    "TypeM":              (0, "Type M"),
    "AGREE_II":           (2, "AGREE II"),
    "Delphi":             (0, "Fink"),
    "CERQual":            (2, "CERQual"),
    "many_analysts":      (2, "Many analysts"),
}

FULL = json.load(open("handoff_refs_full.json"))  # untruncated, DOI-resolved records

def resolve(key):
    entry = REFS[key]
    idx, label = ANCHOR_PICK[key]
    rec = FULL.get(key) or (entry if isinstance(entry, dict) else entry[idx])
    assert "doi" in rec and "error" not in rec, (key, rec)
    return label, rec

ANCHORS = {k: resolve(k) for k in ANCHOR_PICK}
LABEL2KEY = {v[0]: k for k, v in ANCHORS.items()}

# ---------------------------------------------------------------- items
# (id, kind, condition, trigger_field, move, notes, anchor_label)
# kind: down | up | cap | reclass | frame
EMPIRICAL = [
 ("E-D1", "down", "No independent replication of the finding, and the source is not itself a multi-site or multi-lab project",
  "original vs. replication", "-1",
  "Not applied when the claim is about a single documented event (a retraction, one journal's policy change). If E-D11 reclassified a 'replication' as a reanalysis, apply this item afterwards.", "OSC 2015"),
 ("E-D2", "down", "Empirical primary, published after 2015, silent on pre-registration",
  "pre-registration status", "-1",
  "Spec 24 silence rule. Full-text sources only; on abstract-only sources the field is 'not observable' and this item does not fire.", "Nosek"),
 ("E-D3", "down", "Several outcomes, subgroups, or analytic specifications reported with no pre-specified primary and no multiverse or specification-curve check",
  "pre-registration status; design", "-1",
  "Fires only when the source itself shows analytic multiplicity. If the source is silent on pre-registration and shows no multiplicity, E-D2 alone fires (see double-count register). Selective-reporting domain of [RoB 2](#references).", "Forking paths"),
 ("E-D4", "down", "Imprecision: the interval on the reference magnitude includes the negligibility threshold, or N is below the source's own stated power target",
  "N; effect size; heterogeneity and prediction interval", "-1 (-2)",
  "Take -2 when the interval spans both a negligible and a large effect, i.e. the evidence does not distinguish 'no practical effect' from 'the largest effect claimed in the literature'.", "GRADE-6"),
 ("E-D5", "down", "Synthesis reports substantial heterogeneity, or a prediction interval that crosses the direction boundary, with no moderator or subgroup account of it",
  "heterogeneity and prediction interval", "-1",
  "Where a synthesis reports no prediction interval at all, record the field as not reported and fire this item once; do not additionally fire E-D4 for the same silence. See also [GRADE-7](#references).", "IntHout"),
 ("E-D6", "down", "Synthesis of a literature with documented publication bias that names no bias-correction method, or whose estimate does not survive the most conservative method applied",
  "bias-correction method by name", "-1 (-2)",
  "Take -2 when the corrected estimate crosses the negligibility threshold. Spec 29: where methods disagree, report both estimates and follow the more conservative. See also [GRADE-5](#references).", "Carter"),
 ("E-D7", "down", "Indirectness: the field, era, data type, task or design type, or sample characteristics studied differ from the context the claim states",
  "applicability tags", "-1",
  "Fires once per claim however many tags mismatch. Record which tag drove it. Not a downgrade when the claim's stated context is narrowed to match the source instead.", "ROBINS-I"),
 ("E-D8", "down", "All positive results trace to one lab, author group, or shared dataset",
  "provenance tags", "-1",
  "Does not fire when an independent group has replicated, since E-D1 is then already satisfied. This item is also the independence test that the convergence upgrade (X-U1) depends on.", "Camerer"),
 ("E-D9", "down", "Observational study of the literature with no design feature or covariate strategy addressing the obvious confound",
  "design; applicability tags", "-1 (-2)",
  "Example: pre-registration uptake is confounded with field, era, and author cohort. Take -2 when the confound could plausibly produce the whole association.", "ROBINS-I"),
 ("E-D10", "down", "The outcome rests on a contested construct and the source does not name the measure used",
  "measure named and contest noted (spec 25)", "-1",
  "Naming a measure is enough to avoid the downgrade; the contest is recorded as a tag either way, not as a second downgrade.", "CERQual"),
 ("E-D11", "reclass", "The source calls a study a replication, but it re-analyses the same data under different analytic choices",
  "original vs. replication", "reclassify",
  "Spec 29: this is a reanalysis, not a replication. Reclassify, do not downgrade, then re-apply E-D1 and the convergence independence test.", "Many analysts"),
 ("E-D12", "down", "Effect size is from a small original study and no bias-corrected or replication-based estimate exists",
  "N; effect size", "flag only",
  "Spec 21: flag as likely inflated, do not adjust numerically. This item carries no tier movement; it exists so the flag is recorded rather than silently folded into E-D4.", "Type M"),
 ("E-U1", "up", "Independent direct replication, concordant in direction, with magnitude inside the reference prediction interval",
  "original vs. replication; effect size", "+1", "", "OSC 2015"),
 ("E-U2", "up", "Estimate survives the most conservative bias-correction method applied and at least two methods agree in direction",
  "bias-correction method by name", "+1", "Mutually exclusive with E-D6 by construction.", "Carter"),
 ("E-U3", "up", "Multiverse or specification-curve analysis present, and the majority of defensible specifications stay in the same direction above the negligibility threshold",
  "design; effect size", "+1",
  "Also satisfied by a vibration-of-effects analysis over model specifications. See also [Multiverse](#references), [Vibration](#references).", "Spec-curve"),
 ("E-U4", "up", "Registered report, or pre-registration with a public analysis plan and documented adherence",
  "pre-registration status", "+1",
  "Adherence must be observable. Pre-registration without a checkable plan prevents E-D2 from firing but does not earn this upgrade.", "Nosek"),
]

SIMULATION = [
 ("S-D1", "down", "Data-generating mechanism not stated, or stated too incompletely to re-implement",
  "parameter ranges cover realistic conditions", "-1",
  "If the claim depends entirely on the unrecoverable mechanism, this is Cannot Grade rather than a downgrade (see spec 34 checklist).", "ADEMP"),
 ("S-D2", "down", "Parameter ranges do not cover the conditions the claim is stated over",
  "parameter ranges cover realistic conditions", "-1 (-2)",
  "Take -2 when only the region favourable to the method is explored, e.g. sample sizes far above typical practice, or no low-signal condition.", "Siepe"),
 ("S-D3", "down", "No relevant comparator, or the comparator runs at defaults while the proposed method is tuned, or the study is run by the method's proponents with no neutral study available",
  "code available; provenance tags", "-1",
  "The simulation analogue of E-D8. Neutral-comparison framing: a comparison designed by a proponent is evidence about the best case, not the typical case.", "Boulesteix"),
 ("S-D4", "down", "Number of repetitions not reported, or Monte Carlo standard error not reported and not negligible relative to the difference claimed",
  "parameter ranges cover realistic conditions", "-1",
  "ADEMP requires performance measures with uncertainty. A difference smaller than its own Monte Carlo error supports no claim.", "ADEMP"),
 ("S-D5", "down", "The performance measures reported do not match the claim (a coverage claim supported only by bias or power results)",
  "parameter ranges cover realistic conditions", "-1", "", "TRISS"),
 ("S-D6", "down", "No check against real data with a known answer",
  "results checked against real data with known answers", "-1",
  "This is the second of the three method-validation standards (spec 28). When the spec-28 overlay already caps the tier for the same missing standard, fire the item or the cap, not both.", "Boulesteix"),
 ("S-D7", "down", "Code unavailable and the mechanism, estimand, or tuning is described too incompletely to re-implement",
  "code available", "-1",
  "Unavailable code with a fully specified mechanism is recorded as a transparency tag, not a downgrade; otherwise older sources are penalised for a norm that did not exist.", "TRISS"),
 ("S-D8", "down", "Data are simulated from exactly the model the method assumes, with no misspecification condition",
  "parameter ranges cover realistic conditions", "-1",
  "A self-fulfilling design demonstrates internal consistency, not performance.", "Siepe"),
 ("S-U1", "up", "Neutral comparison study: authors are not the method's proponents, and the protocol and performance measures were fixed in advance",
  "provenance tags", "+1", "", "Boulesteix"),
 ("S-U2", "up", "Misspecification conditions present and the result holds across them",
  "parameter ranges cover realistic conditions", "+1", "", "Siepe"),
 ("S-U3", "up", "Simulation reproduced independently with different code",
  "code available", "+1", "", "ADEMP"),
 ("S-C1", "cap", "Simulation-only evidence",
  "-", "cap Moderate",
  "Aligns with spec 28: coverage of realistic conditions is one of three standards, and one standard alone cannot exceed Moderate. Simulation reaches High only through convergence with another evidence type.", "ADEMP"),
]

PROOF = [
 ("P-F1", "frame", "What is graded is the claim's support, not the theorem's truth",
  "-", "framing",
  "A correct theorem can be weak support for a claim about practice. Never record a proof source as Cannot Grade because the mathematics is beyond audit; grade the fit between result and claim.", ""),
 ("P-D1", "down", "Assumptions not stated",
  "stated assumptions", "-1",
  "If the claim concerns behaviour under conditions the proof never names, this is Cannot Grade for that claim rather than a downgrade.", ""),
 ("P-D2", "down", "Assumptions stated but known to be violated in the context the claim is stated over, with no robustness or sensitivity result",
  "stated assumptions; applicability tags", "-2",
  "Do not also fire E-D7 for the same mismatch (see double-count register).", "GRADE"),
 ("P-D3", "down", "Result is asymptotic, the claim is about realistic finite samples, and no finite-sample bound or simulation is supplied",
  "asymptotic or finite-sample", "-1", "", ""),
 ("P-D4", "down", "Result is worst-case or existence-only while the claim is about typical performance, or the reverse",
  "asymptotic or finite-sample; stated assumptions", "-1", "", ""),
 ("P-D5", "down", "The result depends on a quantity the proof leaves unidentified (an unknown constant or rate) and no empirical calibration is supplied",
  "stated assumptions", "-1", "", ""),
 ("P-D6", "down", "Recent or disputed result, not independently checked, not machine-verified, and published without proof review",
  "who, on what basis, whether dissent is documented", "-1",
  "Kept deliberately mild: the default assumption is that a published proof is correct.", ""),
 ("P-U1", "up", "Finite-sample result with explicit constants",
  "asymptotic or finite-sample", "+1", "", ""),
 ("P-U2", "up", "Assumptions shown to be testable and tested, or verified to hold, in the claim's context",
  "stated assumptions", "+1", "", ""),
 ("P-U3", "up", "Independent proof by a different route, or a machine-checked proof",
  "-", "+1", "", ""),
 ("P-C1", "cap", "Proof-only evidence for a claim with an empirical component (about what happens in practice or in real literatures)",
  "-", "cap Moderate",
  "A purely mathematical claim, scoped to its assumptions, is not capped: a proof is the on-type evidence for it and can reach High.", ""),
]

CONSENSUS = [
 ("C-F1", "frame", "Consensus is not independent evidence",
  "-", "framing",
  "When the statement cites its basis, retrieve those sources and grade them (C-U2). The consensus itself contributes only through the quality of its process.", "AGREE II"),
 ("C-D1", "down", "Basis not stated: no cited evidence and no described reasoning",
  "who, on what basis, whether dissent is documented", "cap Very Low", "", "AGREE II"),
 ("C-D2", "down", "No structured process: panel undefined, or no documented aggregation rule or stopping rule",
  "who, on what basis, whether dissent is documented", "-1", "", "Fink"),
 ("C-D3", "down", "Dissent not documented, or unanimity asserted with no record of how disagreement was handled",
  "who, on what basis, whether dissent is documented", "-1", "", "Fink"),
 ("C-D4", "down", "Panel composition undisclosed, or single-discipline for a claim that spans disciplines",
  "who, on what basis, whether dissent is documented; applicability tags", "-1", "", "AGREE II"),
 ("C-D5", "down", "Funding or conflicts undisclosed",
  "provenance tags", "-1", "", "AGREE II"),
 ("C-D6", "down", "Guideline restates an earlier version with no documented re-review, and relevant evidence has appeared since",
  "who, on what basis, whether dissent is documented", "-1", "", "AGREE II"),
 ("C-D7", "reclass", "The statement is normative and its descriptive basis cannot be separated out",
  "-", "reclassify",
  "Spec 13: grade the descriptive basis. If inseparable, return Cannot Grade for the normative claim and say which descriptive claim would need to be graded instead.", ""),
 ("C-U1", "up", "Structured expert elicitation with a documented aggregation rule and some calibration evidence for the experts",
  "who, on what basis, whether dissent is documented", "+1",
  "Raises the cap from Low to Moderate. The calibration premise behind this item is one of the two rubric parameters currently without a verified anchor (section 15).", "Fink"),
 ("C-U2", "reclass", "The statement's evidence base is retrieved and gradeable",
  "-", "reclassify",
  "Grade the underlying sources on their own checklists and treat the consensus as a retrieval pointer, not as a source. This is the expected path, not an exception.", ""),
 ("C-C1", "cap", "Consensus or guideline as the only source",
  "-", "cap Low", "Cap becomes Moderate when C-U1 applies.", "AGREE II"),
]

ARGUMENT = [
 ("A-F1", "frame", "Argument is on-type for conceptual, definitional, and normative-basis claims, and off-type for empirical claims",
  "-", "framing",
  "Grading an argument as though it were empirical evidence is one of the errors the adversarial pass checks for (AP-6).", ""),
 ("A-D1", "down", "A load-bearing premise is an empirical claim with no retrieved source",
  "who, on what basis, whether dissent is documented", "-1 per premise, max -2",
  "Spec 19: if the argument rests on a single unsupported empirical premise, grade that premise as its own claim instead of grading the argument.", ""),
 ("A-D2", "down", "The inference step is unstated, or the conclusion is broader than the premises support",
  "-", "-1 (-2)",
  "Take -2 when the conclusion generalises across fields, eras, or task types that no premise covers.", ""),
 ("A-D3", "down", "Rebuttals present in the retrieved literature are not addressed",
  "who, on what basis, whether dissent is documented", "-1", "", ""),
 ("A-D4", "down", "A key term shifts meaning between premises and conclusion",
  "measure named and contest noted (spec 25)", "-1",
  "Log the merge or split decision under spec 20 when this fires.", ""),
 ("A-D5", "down", "The claim is empirically testable, untested, and supported only by argument",
  "-", "cap Low",
  "Record the claim in the evidence gap map (spec 47) as well as in the tier.", ""),
 ("A-D6", "down", "Transfer by analogy from another field with no stated disanalogies",
  "applicability tags", "-1", "", ""),
 ("A-U1", "reclass", "The argument is formalised, or its key step is proved",
  "-", "reclassify", "Grade under Checklist C (proof).", ""),
 ("A-U2", "up", "A published critical exchange exists and the argument survives the documented rebuttals",
  "who, on what basis, whether dissent is documented", "+1", "", ""),
 ("A-U3", "up", "Every load-bearing premise is independently supported at Moderate or better",
  "-", "+1", "", ""),
 ("A-C1", "cap", "Argument-only evidence",
  "-", "cap Low (empirical claims) / Moderate (conceptual claims)",
  "Argument-only evidence never reaches High.", ""),
]

CHECKLISTS = [
 ("A", "Empirical meta-research", "replication projects, reanalyses, randomised methodological experiments, observational studies of the literature", EMPIRICAL),
 ("B", "Simulation", "Monte Carlo studies of method performance", SIMULATION),
 ("C", "Proof or analytic result", "theorems, identifiability and consistency results, impossibility results", PROOF),
 ("D", "Expert consensus or guideline", "handbooks, reporting guidelines, panel statements, structured elicitations", CONSENSUS),
 ("E", "Theoretical argument", "conceptual and methodological arguments without formal proof", ARGUMENT),
]

BASELINES = [
 ("Empirical meta-research", "**High**", "Multi-site or multi-lab pre-registered replication project; bias-corrected synthesis of 10 or more studies reporting a prediction interval."),
 ("Empirical meta-research", "**Moderate**", "Single pre-registered empirical meta-research study with adequate N; randomised methodological experiment (random assignment of reviewers, analysts, or procedures)."),
 ("Empirical meta-research", "**Low**", "Non-pre-registered primary; cross-sectional corpus or bibliometric study; reanalysis of one dataset."),
 ("Empirical meta-research", "**Very Low**", "Single-corpus descriptive or pre-post report with no comparison condition."),
 ("Simulation", "**Low**", "Any simulation study. Movement is by S-items; the S-C1 cap holds at Moderate."),
 ("Proof or analytic result", "**Moderate**", "Any published proof relevant to the claim. High is reachable via P-U items for claims scoped to the mathematics; P-C1 caps claims with an empirical component."),
 ("Expert consensus or guideline", "**Very Low**", "Any consensus statement or guideline. C-C1 caps at Low, or Moderate with C-U1."),
 ("Theoretical argument", "**Very Low**", "Any argument source. A-C1 caps at Low for empirical claims, Moderate for conceptual ones."),
]

TIERS = [
 ("High", "Direction is established by more than one independent line of evidence, at least two of which reach Low or better on their own checklist, and the reference magnitude comes from a replication-based or bias-corrected estimate whose prediction interval excludes the negligibility threshold.",
  "A large, well-designed study with a contrary result, or the discovery that the independent lines share a data source or author group."),
 ("Moderate", "Direction is well supported but rests on one evidence line, or the reference magnitude is uncorrected or imprecise, or a documented boundary condition limits transfer to the claim's stated context.",
  "One well-designed new study, or a bias-corrected synthesis, could move the magnitude materially; direction is unlikely to flip."),
 ("Low", "Direction is supported, but at least one serious weakness is uncorrected: no replication and no bias correction, or a simulation that does not cover realistic conditions, or a proof whose assumptions are not met in the claim's context.",
  "Direction could plausibly flip on new evidence of the same kind."),
 ("Very Low", "The claim appears in the retrieved literature, but the evidence does not constrain direction: a single small unregistered study, an argument with unsupported premises, or a consensus statement with no cited basis.",
  "Almost any adequately designed study would be more informative than everything now retrieved."),
 ("Cannot Grade", "Reserved for genuinely absent evidence (spec 34): no retrieved source addresses the claim's core relation, or every retrieved source is abstract-only and the deciding field is not observable, so no rated tier is defensible.",
  "Retrieval at a different access level, or any source that addresses the relation directly."),
]

DOUBLE_COUNT = [
 ("Missing or unverifiable pre-registration", "E-D2 **or** E-D3", "E-D3 fires only when the source itself shows analytic multiplicity; otherwise E-D2 alone."),
 ("No prediction interval reported in a synthesis", "E-D5 **or** E-D4", "Fire E-D5 (inconsistency); do not also fire E-D4 for the same silence."),
 ("No real-data check for a statistical method", "S-D6 **or** the spec-28 overlay cap", "Whichever is more restrictive, recorded by name; never both."),
 ("Assumption or context mismatch on a proof source", "P-D2 **or** E-D7", "P-D2 fires; indirectness is already what it encodes."),
 ("Evidence traced to a single group", "E-D8 **or** S-D3", "By source type. Both may fire only if two distinct sources each have the defect."),
 ("Small-sample inflated estimate", "E-D12 (flag) **plus at most one of** E-D4", "The flag carries no movement, so it never double-counts; imprecision still needs its own trigger."),
 ("Contested construct", "E-D10 **or** A-D4", "By source type. The construct contest itself is recorded as a tag under spec 25 either way."),
]

COMBINATION = [
 ("X-1", "Grade every retrieved source on its own checklist first and record the per-source tier. No claim-level move happens before this."),
 ("X-2", "The claim's starting tier is the highest per-source tier among sources that are **on-type** for the claim (A-F1, P-C1)."),
 ("X-3", "**Convergence upgrade, +1, once per claim.** Two or more sources of *different* evidence types each reach Low or better on their own checklist, agree in direction, and share no data source, author group, or code base. Spec 27: a proof plus a weak simulation is not convergence. The independence test is E-D8 and S-D3."),
 ("X-4", "**Conflict.** Sources disagreeing in direction, both at Low or better, send the claim to Contested (spec 34); they are not averaged into a middle tier. Disagreement in magnitude only: report both estimates and take the more conservative tier (spec 29)."),
 ("X-5", "**Weighting.** Replications, registered reports, and bias-corrected syntheses outweigh originals. A reanalysis under different analytic choices is not a replication (E-D11). Citation count is a retrieval signal only; journal prestige is neither (spec 29)."),
 ("X-6", "**Ceiling.** No claim exceeds the tier its best on-type source can reach alone, plus the single convergence upgrade."),
 ("X-7", "**Volume is not evidence.** Many sources with the same weakness do not lift a tier; they are logged as source count, which is not an input to the tier."),
 ("X-8", "**Floor and total movement.** Downgrades total at most -3 from baseline, floor Very Low. Upgrades total at most +2, and no upgrade applies while any -2 downgrade is live. Cannot Grade is never reached by accumulation, only by its spec-34 conditions."),
]

OVERLAY = [
 ("Proof of properties under stated assumptions", "Checklist C", "which assumptions, asymptotic or finite-sample"),
 ("Simulation coverage of realistic conditions", "Checklist B", "which parameter ranges, whether misspecification was tested"),
 ("Demonstrated performance on real data with known answers", "Checklist B (S-D6) or Checklist A", "which dataset, what the known answer was"),
]

ADVERSARIAL = [
 ("AP-1", "Argue for a different tier, citing extracted fields", "the tier argued for, and the fields cited"),
 ("AP-2", "Source overreach: does each cited source's retrieved text support what is attributed to it", "any source whose text falls short, and what it does support"),
 ("AP-3", "Double counting: is any single defect driving two downgrades", "the collision and the item that should stand"),
 ("AP-4", "Contested versus absent: is a 'contested' call really absent evidence, or a 'Cannot Grade' really Very Low", "which of the spec-34 conditions is met"),
 ("AP-5", "Alternative explanations: for each source, was the finding weighed against the obvious alternative account", "the alternative not considered"),
 ("AP-6", "On-type check: was an argument or consensus graded as though it were empirical evidence", "the source and its correct checklist"),
 ("AP-7", "Missing downgrade: any field recorded 'not reported (full text checked)' with no item fired", "the field and the item that should have fired"),
 ("AP-8", "Upgrade justification: is each upgrade's precondition actually met, including independence for X-3", "the upgrade and the unmet precondition"),
]

PARAMETERS = [
 ("E-D2, E-U4", "Pre-registration and registered reports reduce inflation and predict replicability", "Nosek", "verified"),
 ("E-D6, E-U2", "Uncorrected literatures inflate effects, and bias-correction methods differ materially in conservativeness", "Carter", "verified"),
 ("E-D5", "Heterogeneity is under-reported, and prediction intervals are materially wider than confidence intervals", "IntHout", "verified"),
 ("E-U3", "Analytic specification choices move estimates enough that robustness across them is informative", "Spec-curve", "verified"),
 ("E-D8, X-3", "Shared data, authors, or code inflate apparent convergence, and independent replication rates are lower than original literatures imply", "Camerer", "verified"),
 ("E-D3", "Undisclosed analytic flexibility produces false positives at rates that matter", "Forking paths", "verified"),
 ("E-D12", "Small-sample statistically significant estimates are systematically inflated", "Type M", "verified"),
 ("S-D3, S-U1", "Comparison studies run by a method's proponents favour that method", "Boulesteix", "verified"),
 ("S-D4, S-D5", "Simulation studies frequently omit repetition counts, Monte Carlo error, and estimand definitions", "ADEMP", "verified"),
 ("C-U1", "Structured elicitation with documented aggregation outperforms unstructured consensus, and expert calibration is measurable", "Fink", "**anchor incomplete** - Fink 1984 documents the methods, not their comparative accuracy. Needs a calibration or forecasting-accuracy source from the orientation reading."),
 ("Tier scale, test-retest tolerance (spec 37)", "Trained raters applying an evidence rubric agree within one tier often enough that a one-tier tolerance is meaningful, and disagreement beyond one tier signals a rubric defect", "-", "**no anchor** - needs a GRADE or RoB inter-rater reliability source. Until then the 10% and one-tier bar in spec 37 is a convention, not a calibrated threshold."),
]

DECISIONS = [
 "**Baseline tiers** (section 3). The empirical baselines follow GRADE's design-based starting points; the choice to start simulation at Low and consensus and argument at Very Low is mine, not inherited. If you would rather start every type at Moderate and let items do all the work, the item set does not need to change.",
 "**Total-movement bounds** (X-8): the -3 floor, +2 upgrade ceiling, and the no-upgrade-while--2-is-live rule are conventions chosen so the scale cannot be walked from High to Very Low by stacking mild items. They need first-run data to tune (spec 42 says the same about the cap of eight).",
 "**Spec-28 overlay with two of three standards met.** Spec 28 fixes only the one-of-three case (cap Moderate). I have left two-of-three at cap Moderate unless the missing standard is argued non-applicable, which is a judgement call worth your sign-off.",
 "**S-D7 (code availability).** Drafted so that unavailable code is a downgrade only when it makes the study unre-implementable, otherwise a transparency tag. The alternative is a flat downgrade, which penalises pre-2015 sources for a norm that did not exist.",
 "**Cannot Grade in test-retest** (spec 37). I have treated Cannot Grade as off-scale, so a Cannot-Grade-versus-rated disagreement counts as more than one tier and therefore against the 10% bar. This makes abstention decisions part of what validation tests.",
 "**Negligibility conventions** (spec 50) are *not* drafted here, and four items depend on them: E-D4, E-D6, E-U3, and the High tier definition. Until a first set exists, those items fire on direction and interval width only, which is weaker than intended.",
 "**Two rubric parameters lack anchors** (section 15): the calibration premise behind C-U1, and the rater-agreement premise behind the tier scale and the spec-37 tolerance. Both are gradeable questions inside the tool's own scope, which makes them good first-run inputs under spec 41's rule that centrality to rubric parameters ranks first.",
]

LOGGING = [
 ("per_source_tiers", "Tier reached by each source on its own checklist, before combination", "X-1 is otherwise unauditable"),
 ("items_fired", "IDs of every item that fired, with the extracted field that triggered each", "Spec 26 requires every move to cite its field"),
 ("double_count_decisions", "Each collision from section 10 and the item chosen", "AP-3 checks this"),
 ("overlay_result", "Which of the three method-validation standards are met, for statistical-method claims", "Spec 28 requires it in the output; spec 45 does not yet log it"),
 ("cap_applied", "Which cap bound the tier, if any", "Distinguishes 'graded Moderate' from 'capped at Moderate'"),
 ("on_type_sources", "Which sources were treated as on-type for the claim", "X-2 and AP-6"),
]

# ---------------------------------------------------------------- render
def anchor_cell(label):
    if not label:
        return "-"
    return f"[{label}](#references)"

def item_table(items):
    rows = ["| ID | Condition | Triggering field (spec 24) | Move | Notes | Anchor |",
            "|---|---|---|---|---|---|"]
    for iid, kind, cond, field, move, note, anch in items:
        rows.append(f"| **{iid}** | {cond} | {field} | {move} | {note or '-'} | {anchor_cell(anch)} |")
    return "\n".join(rows)

CORPORATE = {"OSC2015": "Open Science Collaboration"}

def refs_section(cited_labels):
    rows = ["| Anchor | Reference | DOI |", "|---|---|---|"]
    for label in sorted(cited_labels, key=str.lower):
        key = LABEL2KEY[label]
        r = ANCHORS[key][1]
        n = r.get("nauth", 0)
        if key in CORPORATE:
            auth = CORPORATE[key]
        elif n > 2:
            auth = f"{r['first']} et al."
        elif n:
            auth = r["first"]
        else:
            auth = ""
        auth = f"{auth} ({r['year']})" if auth else f"({r['year']})"
        venue = f". *{r['venue']}*" if r["venue"] else ""
        title = r["title"].rstrip(". ")
        rows.append(f"| {label} | {auth}. {title}{venue} | [{r['doi']}](https://doi.org/{r['doi']}) |")
    return "\n".join(rows)

md = []
W = md.append

W("""# Stage 1 grading checklists - draft v0.1

**Rubric version:** `stage1-checklists-v0.1` (draft; not yet adopted)
**Drafts:** spec 26 checklist contents, and spec 49 in the open-questions list
**Status:** every tier produced under these checklists is labeled **provisional** until Stage 2 validation passes (specs 5, 8, 38). The post-retrieval checkpoint stays on (spec 4).

This document is the grading layer's operating content: a tier scale, a starting tier per evidence type, five per-type checklists whose every move cites an extracted field from spec 24, an explicit combination rule, and the three run-level guards Stage 1 adds (adversarial pass, sealed-prior comparison, citation audit).

**What it does not do.** It does not set negligibility conventions (spec 50), source the validation set (spec 51), estimate a field base rate (spec 48), or produce probabilities (spec 40). Four items depend on the negligibility conventions and are marked where they do. Two rubric parameters currently rest on claims with no verified anchor; section 15 names them rather than hiding them.

**Provenance of the items.** Items adapted from an existing framework name it in the Anchor column, and every anchor reference in section 17 was resolved against Crossref rather than recalled. Items for proofs and arguments are written fresh, as spec 26 requires, and carry no anchor. Items marked *anchor incomplete* in section 15 need the orientation reading (spec 11) before adoption.

---

## 1. How a Stage 1 run uses this document

1. Record the **sealed prior** (spec 14) before any retrieval; do not open it again until step 8.
2. Run retrieval and extraction (sections C-E of the spec). Tag each source **full text**, **extracted fields**, or **abstract only**.
3. Run the **citation audit** (spec 33) as a gate. An audit failure invalidates the run before grading, not after.
4. Classify each source by **evidence type** (spec 23), then extract that type's fields (spec 24). Record every missing field as *not reported (full text checked)* or *not observable (abstract only)*. Only the first can trigger a downgrade.
5. Grade **each source** on its own checklist (sections 4-8): start at the baseline tier for its type (section 3), fire items, respect caps, and record every item ID with the field that triggered it.
6. Apply the **double-count register** (section 10) before totalling movement.
7. Combine sources into a claim tier with the **combination rule** (section 9), then apply the **statistical-method overlay** (section 11) where the claim is about a method.
8. Run the **adversarial pass** (section 12), then the **sealed-prior comparison** (section 13).
9. Emit with every tier labeled provisional; log the fields in section 14 alongside the spec 45 set.

Cap of eight graded claims (spec 42); claims past the cap are surfaced with one-line reasons (spec 43).

---

## 2. Tier scale

The scale is ordinal over four rated tiers. Definitions are in terms of *evidence state and what would move it*, not likelihood: spec 40 removed the probability output, and a probabilistic tier definition would reintroduce it unscored.

| Tier | The claim's evidence state | What would move it |
|---|---|---|""")
for t, state, mover in TIERS:
    W(f"| **{t}** | {state} | {mover} |")

W("""
**Adjacency, for spec 37.** High-Moderate-Low-Very Low are adjacent in that order, so "within one tier" is defined. **Cannot Grade is off-scale**: a Cannot-Grade-versus-rated-tier disagreement between two runs counts as more than one tier and therefore against the 10% bar. This is a choice (section 16) and it makes abstention behaviour part of what validation tests.

---

## 3. Starting tier by evidence type

Each source starts here, then moves by its checklist. Starting tiers are design-based, following GRADE's practice of letting the design set the starting point and the checklist do the rest.

| Evidence type | Start | Applies to |
|---|---|---|""")
for etype, start, applies in BASELINES:
    W(f"| {etype} | {start} | {applies} |")

W("""
---""")

for letter, name, scope, items in CHECKLISTS:
    n = 3 + "ABCDE".index(letter) + 1
    W(f"\n## {n}. Checklist {letter} - {name}\n")
    W(f"*Scope: {scope}.*\n")
    W(item_table(items))
    W("")

W("""---

## 9. Combination rule

Spec 27 requires convergence to mean something; this is the rule that makes it operational.

| ID | Rule |
|---|---|""")
for cid, rule in COMBINATION:
    W(f"| **{cid}** | {rule} |")

W("""
---

## 10. Double-count register

Spec 31 makes the adversarial pass check specifically for the same weakness being downgraded twice. This register decides those collisions in advance so the check has something to verify against. **At most one downgrade per underlying defect**; record the item chosen and the field that triggered it.

| Underlying defect | Item that may fire | Rule |
|---|---|---|""")
for defect, items_, rule in DOUBLE_COUNT:
    W(f"| {defect} | {items_} | {rule} |")

W("""
---

## 11. Statistical-method overlay (spec 28)

For claims about a statistical method, "empirically validated" is graded against three standards. The overlay reports which are present and caps the tier; it does not replace the per-source checklists.

| Standard | Supplied by | Reported as |
|---|---|---|""")
for std, supplier, reported in OVERLAY:
    W(f"| {std} | {supplier} | {reported} |")

W("""
**Output line, required for every method claim:** `proof: yes/no | simulation: yes/no | real data: yes/no -> cap <tier>`.

**Caps.** One of three met: cap Moderate (spec 28). Two of three met: cap Moderate, unless the missing standard is argued non-applicable and the argument is recorded. Three met: no overlay cap. The two-of-three rule is a draft decision (section 16).

---

## 12. Adversarial pass checklist (spec 31)

A separate call with a different role prompt receives the extracted fields, the items fired, and the provisional tier. It must argue for a different tier. **The original tier stands only if every point below fails on the evidence**; a point that succeeds either moves the tier or is recorded with the reason it does not.

| ID | Check | Must report |
|---|---|---|""")
for aid, check, must in ADVERSARIAL:
    W(f"| **{aid}** | {check} | {must} |")

W("""
The adversarial call sees extracted fields and retrieved text only, never the sealed prior (spec 14).

---

## 13. Sealed-prior comparison (spec 32)

**Recorded before retrieval, and not shown to the grading or adversarial calls:** the claims the model expects to find, the direction of each, and a tier for each on the section 2 scale.

**Reported per run:** how many prior claims appeared in the retrieved set; how many matched in direction; how many matched in tier; and how many graded claims were absent from the prior.

**Not computable in Stage 1.** The prior-dominance check compares the agreement rate against the prior's own accuracy, which is only measurable on the validation set (specs 32, 35). Stage 1 logs the per-run numbers so the check can be run once Stage 2 exists; it does not attempt the comparison. The interim base-rate approximation in spec 48 also waits on that set.

---

## 14. Logging additions these checklists require

The spec 45 field list predates the checklists and cannot reconstruct a grade. Six additions:

| Field | Contents | Why |
|---|---|---|""")
for f, contents, why in LOGGING:
    W(f"| `{f}` | {contents} | {why} |")

W("""
---

## 15. Rubric parameters and the claims they rest on (specs 6, 44)

Every parameter below is a methodology claim the rubric assumes. Spec 6 requires that when the tool grades one of these at Low or below, the run flags a rubric-revision trigger. Two have no adequate anchor yet.

| Item(s) | Assumed claim | Anchor | Status |
|---|---|---|---|""")
for items_, claim, anch, status in PARAMETERS:
    W(f"| {items_} | {claim} | {anchor_cell(anch) if anch != '-' else '-'} | {status} |")

W("""
The two incomplete rows are gradeable questions inside the tool's own scope. Spec 41 ranks centrality to rubric parameters first when the question is about improving the tool, which makes them natural first-run inputs.

---

## 16. Draft decisions that need your sign-off
""")
for i, d in enumerate(DECISIONS, 1):
    W(f"{i}. {d}")

W("""
---

## 17. References

Every entry resolved against Crossref. Anchor labels are the ones used in the checklist tables.

<a name="references"></a>
""")
import re
cited = set(re.findall(r"\[([^\]]+)\]\(#references\)", "\n".join(md)))
assert cited <= set(LABEL2KEY), cited - set(LABEL2KEY)
W(refs_section(cited))

W("""
The Cochrane Handbook and the GRADE Handbook are named in spec 11 as orientation reading and are not itemised here; RoB 2 and ROBINS-I are the tool papers the empirical items draw on. Anchors appear only where an item or a rubric parameter cites them.
""")

open("stage1-grading-checklists-v0.1.md", "w").write("\n".join(md))

# ---------------------------------------------------------------- CSV
with open("stage1-checklist-items-v0.1.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["item_id", "checklist", "evidence_type", "kind", "condition",
                "trigger_field", "move", "notes", "anchor_label", "anchor_doi",
                "rubric_version"])
    for letter, name, scope, items in CHECKLISTS:
        for iid, kind, cond, field, move, note, anch in items:
            doi = ANCHORS[LABEL2KEY[anch]][1]["doi"] if anch else ""
            w.writerow([iid, letter, name, kind, cond, field, move, note, anch, doi,
                        "stage1-checklists-v0.1"])
    for aid, check, must in ADVERSARIAL:
        w.writerow([aid, "AP", "adversarial pass", "check", check, "-", "-", must, "", "", "stage1-checklists-v0.1"])
    for cid, rule in COMBINATION:
        w.writerow([cid, "X", "combination rule", "rule", rule, "-", "-", "", "", "", "stage1-checklists-v0.1"])

print(sum(len(i[3]) for i in CHECKLISTS), "type items;",
      len(ADVERSARIAL), "adversarial;", len(COMBINATION), "combination")
print(len(open("stage1-grading-checklists-v0.1.md").read().split("\n")), "md lines")
