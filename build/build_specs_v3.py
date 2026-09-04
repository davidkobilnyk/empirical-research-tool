"""Produces research-methodology-tool-specs-v3.md from the v2 artifact by applying
the amendments agreed in this session. Spec numbers 1-56 keep their v2 meaning so
prior references stay valid; new requirements are appended as 57-60.

Every anchor is asserted to match exactly once, so a silent no-op edit cannot happen.
"""
src = open(host.artifact_path("210e8899-0011-4d78-b406-2449a824ddf6")).read()
lines = src.split("\n")

# ---- line-keyed replacements: prefix -> full replacement line -------------
REPL = {}

REPL["4. **Environment.**"] = (
 "4. **Environment.** Runs in a Claude project using skills and connectors. Retrieval and extraction: "
 "FastTrack Literature, Consensus, SciSpace, Scholar Gateway, alphaXiv, Scite, and platform servers for "
 "PubMed, OpenAlex/arXiv, and ClinicalTrials.gov. Logging: Airtable. Direct API access is additionally "
 "granted for Europe PMC, the OSF API and its file hosts, Zenodo, Crossref including the bulk Retraction "
 "Watch dataset at Crossref Labs, PROSPERO (page access only), PhilPapers (OAI-PMH only), and the Cochrane "
 "and GRADE handbooks. Per-tool routes and measured reliability are held in the source-coverage companion "
 "document, not here, because they change without the specification changing. A post-retrieval checkpoint "
 "— a pause showing retrieved sources and candidate claims before grading — is **on by default** and is "
 "removed only after Stage 2 validation passes.")

REPL["11. **Orientation reading before Stage 1:**"] = (
 "11. **Orientation reading before Stage 1:** a handful of foundational metascience reviews plus the GRADE "
 "and Cochrane handbooks, read as sources of checklist items rather than as the rubric itself. Both handbooks "
 "are directly reachable (`training.cochrane.org`, `gdt.gradepro.org`). The Stage 1 checklists were drafted "
 "from the GRADE journal series and the named tool papers rather than the handbooks themselves; two items "
 "still need the handbooks' own wording, and two rubric parameters need an anchor that this reading is "
 "expected to supply (spec 49). This reading also produces the development set (spec 39).")

REPL["16. **Balanced channels.**"] = (
 "16. **Balanced channels.** Literature search, including debate mapping, is run for both supporting and "
 "disconfirming evidence with parallel query sets. Those parallel sets are the load-bearing part of this "
 "requirement; the per-claim checks below supplement them and do not replace them. The targeted "
 "disconfirmation check runs, for each candidate claim: **retraction and correction status** from the "
 "Crossref `updated-by` field, which distinguishes a retraction from a correction and names the notice DOI "
 "(reliable, and also a spec 33 gate); **replication outcomes** from the databases named in spec 51; "
 "**citing-paper stance** from Scite citation intent, used as a lead generator only, because measured intent "
 "labels are sparse and skewed toward 'mentioning' (spec 53); and **PubPeer** as a manual check, its origin "
 "refusing automated clients. This is a check, not a weighted channel; disconfirming sources are graded by "
 "the same standards as any other source.")

REPL["18. **Access level.**"] = (
 "18. **Access level.** Full text where legally available: Europe PMC for its open-access and in-EPMC subset; "
 "OSF for OSF-hosted preprints, which much of the metascience literature uses; alphaXiv for arXiv; PMC via "
 "the PubMed server; and Scite's full-text read, which returns an explicit flag separating served full text "
 "from a fallback abstract. Each source is tagged **full text**, **extracted fields**, or **abstract only**, "
 "and the tag is taken from that flag or from the retrieval route actually used — never inferred from the "
 "publisher or from whether a paywall was expected. This tag governs spec 24.")

REPL["26. **Rubric.**"] = (
 "26. **Rubric.** Versioned. Four tiers plus abstain: **High, Moderate, Low, Very Low, Cannot Grade.** The "
 "tier scale is defined operationally in terms of evidence state and what would move it, not in terms of "
 "likelihood, so that spec 40's removal of the probability output is not undone by the tier definitions; "
 "tier adjacency is fixed so that spec 37's tolerance is meaningful. Each evidence type has a short checklist "
 "of named downgrade and upgrade conditions; every downgrade or upgrade cites the extracted field that "
 "triggered it. The checklists are adapted from GRADE, RoB 2, and ROBINS-I where those apply and written "
 "fresh for proofs, simulations, and arguments where they don't. **The checklist contents are a versioned "
 "companion document** (current rubric version `stage1-checklists-v0.1`), holding the tier scale, a starting "
 "tier per evidence type, items across the five evidence types, an explicit combination rule, a double-count "
 "register, and the adversarial-pass and sealed-prior checklists. Amending the checklists is a rubric version "
 "change under spec 44; amending this specification is not.")

REPL["28. **Statistical methods.**"] = (
 "28. **Statistical methods.** A method is \"empirically validated\" to the degree it has all three: proof of "
 "properties under stated assumptions; simulation coverage of realistic conditions; demonstrated performance "
 "on real data with known answers. The output reports which of the three are present. A method with only one "
 "cannot exceed Moderate. Where two are present the tier is also capped at Moderate, unless the missing "
 "standard is argued non-applicable and that argument is recorded; where all three are present no overlay "
 "cap applies.")

REPL["33. **Citation audit.**"] = (
 "33. **Citation audit.** Every cited source appears in a tool result, and its retrieved text supports the "
 "claim attributed to it. Every cited source is additionally checked for retraction and correction status via "
 "Crossref `updated-by`: a run citing a retracted source **fails** the audit rather than noting it, and a "
 "cited source carrying a correction is re-read against the corrected version before the claim stands. A run "
 "with an audit failure is marked invalid.")

REPL["35. **Validation set: 50 or more claims with external ground truth.**"] = (
 "35. **Validation set: 50 or more claims with external ground truth.** Sources: outcomes of large replication "
 "projects; statistical results with mathematical or simulation-established answers; claims documented as "
 "retracted or refuted; and a deliberate share of well-established claims to detect over-skepticism. Two "
 "routes reduce assembly to filtering rather than trawling: the bulk Retraction Watch dataset, one CSV of "
 "roughly 72,000 rows carrying subject, retraction nature, documented reason, and original-paper DOI, for the "
 "retracted and refuted share; and the replication databases in spec 51 for replication outcomes. The answer "
 "key is the documented outcome, not an opinion, and each key entry cites its source. The set is assembled by "
 "the user, not drafted by the model in the grading environment; the model may surface candidates with their "
 "citations but does not write the key.")

REPL["37. **Test-retest.**"] = (
 "37. **Test-retest.** Each validation claim runs three times independently with reasoning order varied. Any "
 "tier disagreement is recorded; a disagreement of more than one tier on more than 10% of claims fails "
 "validation. Tiers are adjacent in the order High–Moderate–Low–Very Low. **Cannot Grade is off-scale:** any "
 "disagreement between Cannot Grade and a rated tier counts as more than one tier, and therefore against the "
 "10% bar, which makes abstention behaviour part of what validation tests. Results are aggregated as in "
 "structured expert elicitation.")

REPL["45. **Logging to Airtable**"] = (
 "45. **Logging to Airtable** is required: claim ID, sharpened claim, tier, provisional flag, applicability "
 "tags, evidence-type mix, access-level mix, prior-match flag, abstain, rubric version, run date. Six further "
 "fields are required for a grade to be reconstructable from the log rather than re-derived: per-source tier "
 "before combination; the IDs of every checklist item that fired, each with the field that triggered it; the "
 "double-count decisions taken; which of the three method-validation standards were met; which cap bound the "
 "tier, if any; and which sources were treated as on-type for the claim. Supports follow-up batches, drift "
 "detection, and the prior-dominance check.")

REPL["49. **Checklist contents**"] = (
 "49. **Checklist contents** for proofs, simulations, and arguments (spec 26) — **drafted** as rubric version "
 "`stage1-checklists-v0.1`, generated from a single item table so the document and its machine-readable copy "
 "cannot drift. What remains: sign-off on the seven draft decisions recorded there (starting tiers, "
 "total-movement bounds, the two-of-three overlay cap, the code-availability item, Cannot Grade's treatment "
 "in test-retest, and the two unanchored parameters), and anchoring those two parameters — the "
 "expert-calibration premise behind the consensus upgrade, and the rater-agreement premise behind the tier "
 "scale and spec 37's tolerance. Until the second is anchored, the one-tier and 10% bars are conventions, not "
 "calibrated thresholds.")

REPL["51. **Validation set sourcing.**"] = (
 "51. **Validation set sourcing.** Concrete routes now exist and are reachable: the bulk Retraction Watch "
 "dataset for retracted and refuted claims; OSF for the FORRT Replication Database and for the project-level "
 "datasets of the large replication projects (Reproducibility Project: Psychology, Many Labs 1–5, the Social "
 "Sciences Replication Project, Reproducibility Project: Cancer Biology, ManyBabies); ReplicationWiki for "
 "economics; Curate Science if it proves still maintained. Open: how many of the 50 each source can fill, "
 "what share of well-established claims is needed to detect over-skepticism, and how claims whose documented "
 "outcome is mixed rather than pass or fail are handled.")

REPL["52. Abstract-only access for a substantial fraction of sources;"] = (
 "52. Abstract-only access for a fraction of sources — reduced but not eliminated. OSF-hosted preprints, "
 "arXiv, the Europe PMC open-access subset, and papers Scite serves as full text are now genuinely full text; "
 "paywalled sources outside those routes stay abstract-only. Spec 24 prevents this from becoming a penalty "
 "but cannot recover the missing fields.")

REPL["53. FastTrack's debate-mapping and saturation tools are unassessed;"] = (
 "53. FastTrack's debate-mapping and saturation tools remain unassessed, as does SciSpace's field extraction. "
 "Scite's citation intent is characterised and thin: on one 40-edge sample it returned 26 *mentioning*, 1 "
 "*supporting*, 14 unlabeled and no *contrasting* edge, and preprint DOIs resolved no edges at all — so it "
 "generates leads and does not evidence dissent. Consensus is loaded and reachable; the v2 statement that it "
 "was not is superseded. PubPeer is unavailable to automated access at its origin, so spec 16's PubPeer "
 "component is manual. No licensed index (Scopus, Web of Science, Dimensions) and no book-length literature "
 "is reachable, which bounds what spec 47's coverage note may claim.")

REPL["56. The validation set's ground truth is itself a judgment about the empirical record,"] = (
 "56. The validation set's ground truth is itself a judgment about the empirical record, though a far more "
 "constrained one than v1's. Documented outcomes can be revised; the set should be re-checked when the rubric "
 "parameters are. Where a key entry rests on a retraction, note that the documented reason is a publisher or "
 "journal determination — constrained and citable, but not a neutral adjudication.")

count = {k: 0 for k in REPL}
for i, ln in enumerate(lines):
    for k, v in REPL.items():
        if ln.startswith(k):
            lines[i] = v
            count[k] += 1
bad = {k: c for k, c in count.items() if c != 1}
assert not bad, f"anchors not matched exactly once: {bad}"

doc = "\n".join(lines)

# ---- insert two new extracted-field bullets into spec 24 -----------------
anchor24 = "    - *Consensus/argument:* who, on what basis, whether dissent is documented."
assert doc.count(anchor24) == 1
doc = doc.replace(anchor24, anchor24 + "\n"
 "    - *All types:* retraction and correction status, from Crossref `updated-by` — the type, the source, and "
 "the notice DOI.\n"
 "    - *Simulation and empirical:* code or data deposit, resolved by lookup (Zenodo, OSF, or the paper's "
 "repository) rather than taken from the source's own availability statement (spec 59).")

# ---- header ---------------------------------------------------------------
old_head = ("# Research Methodology Evidence Tool — Specifications v2\n\n"
            "Revised September 4, 2026. Supersedes the September 4 handoff document (v1).")
assert doc.count(old_head) == 1
doc = doc.replace(old_head,
 "# Research Methodology Evidence Tool — Specifications v3\n\n"
 "Revised September 4, 2026. Supersedes v2 of the same date, which superseded the v1 handoff document.\n\n"
 "**Numbering is stable.** Specs 1–56 keep the meaning they had in v2, so earlier references by number remain "
 "valid; amended specs are listed below and new requirements are appended as 57–60.")

# ---- new "what changed from v2" section -----------------------------------
v1_head = "## What changed from v1 and why"
assert doc.count(v1_head) == 1
doc = doc.replace(v1_head, """## What changed from v2 and why

Two things happened after v2 was written: the Stage 1 checklists were drafted, and the retrieval environment was tested rather than assumed. Both produced changes here.

**From drafting the checklists (spec 49, now closed).** The rubric needed things v2 named but did not define. Spec 26 now defines the tier scale operationally and points at the checklists as a *versioned companion document*, so that revising an item is a rubric version change rather than a specification change. Spec 37 now fixes tier adjacency and puts Cannot Grade off-scale, without which its own one-tier tolerance had nothing to measure. Spec 28 now covers the two-of-three case it left open. Spec 45 gains six logging fields, because the v2 field list could not reconstruct a grade.

**From testing the environment.** v2 assumed a retrieval environment; most of it is now measured, and three assumptions were wrong. Retraction status needs no new tooling — Crossref carries it per DOI and distinguishes retraction from correction — so spec 16 names it concretely and spec 33 makes it an audit gate, since a run citing a retracted source should fail rather than footnote it. Scite's citation intent turned out too sparse to evidence dissent, so spec 16 demotes it to a lead generator and spec 53 records the measurement. PubPeer refuses automated clients at its origin, so its component of spec 16 is manual. Conversely, OSF-hosted preprints are now retrievable as full text, which matters because spec 24 lets only full-text sources trigger a downgrade — while that route was closed, the tool was structurally unable to grade the metascience preprint literature at full strength.

**New requirements (57–60)** cover what those tests showed the specification had no rule for: verifying multi-hop retrieval routes instead of silently degrading to abstract-only; characterising a tool before trusting its output, which is spec 5's trust-layer logic applied to tools; preferring a lookup over a source's self-report where both exist; and recording that four checklist items are inert until the negligibility conventions of spec 50 exist.

**Also changed:** spec 4 lists the current connector and API set; spec 11 records that both handbooks are now directly reachable; spec 35 and spec 51 name the two sourcing routes that turn validation-set assembly into filtering, without weakening spec 35's rule that the user assembles it; spec 52 narrows the abstract-only limitation to what is actually still paywalled.

**Not changed:** the two-layer trust split (spec 5), the sealed prior (14), the removal of the probability output (40), the held-out discipline (36), the cap of eight (42), and the requirement that the user assemble the validation set (35). Nothing here makes grading less provisional; Stage 2 remains the only thing that can.

---

## What changed from v1 and why""")

# ---- new section N with specs 57-60 ---------------------------------------
doc = doc.rstrip("\n") + """

---

## N. Operating rules added in v3

57. **Route verification.** Retrieval routes with more than one hop or a signed URL are verified at the start of each run series rather than assumed. The OSF download chain is the current instance: the API's download link redirects twice, ending at a signed URL in a specific storage bucket, and the final URL must be rewritten to its bucket-qualified form. A route failure is a retrieval-layer failure — it invalidates the run under spec 7's criterion and is never allowed to degrade silently into an abstract-only tag, because that would convert a fixable access problem into a permanent evidence gap.

58. **Tool characterisation before trust.** A connector's output is used as evidence only after it has been characterised on a sample with a known answer; before that it is a lead generator whose output must be confirmed by a second route. This is spec 5's trust-layer rule applied to tools rather than to layers, and it currently binds FastTrack's debate-mapping and saturation tools, SciSpace's field extraction, and Scite's citation intent. Characterisation results are recorded in the source-coverage companion document with the sample they were measured on.

59. **Lookup over self-report.** Where a field can be resolved by lookup — code or data availability, retraction or correction status, pre-registration in a registry — the lookup takes precedence over the source's own statement about itself, and the output records which was used. A source claiming its code is available is evidence about the claim, not about the code.

60. **Dependency on the negligibility conventions.** Four checklist items — the imprecision downgrade, the bias-correction-failure downgrade, the robustness upgrade — and the High tier definition depend on spec 22 and the conventions still owed under spec 50. Until a first set exists, those items fire on direction and interval width alone, and the run output states that they did.
"""

open("research-methodology-tool-specs-v3.md", "w").write(doc)

# ---- verification --------------------------------------------------------
import re
nums = [int(m.group(1)) for m in re.finditer(r"^(\d{1,2})\. ", doc, re.M)]
missing = [n for n in range(1, 61) if n not in nums]
print("spec numbers present:", len(set(nums)), "| missing from 1-60:", missing)
print("dupes:", [n for n in set(nums) if nums.count(n) > 1])
print("v2 bytes:", len(src), "-> v3 bytes:", len(doc))
