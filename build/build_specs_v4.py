#!/usr/bin/env python3
"""Produce specs v4 from v3: a transparency tool, not a grading tool.

v4 removes grading, scoring and evaluation from the tool's scope. It does NOT
delete the grading specs -- they are marked DEFERRED and kept in place, because
(a) spec numbers 1-56 carry their v2 meaning and prior references must keep
resolving, and (b) the grading design is real work that may return once the
retrieval and extraction layers have been used in anger.

The substantive argument for the change, recorded here because a spec should
carry its own reasoning: v3 already split trust two ways -- retrieval and
extraction trusted, grading provisional until validated against an external
set. Removing the grading layer makes everything the tool ships part of the
trusted layer. No provisional labels, no dependency on a validation set that
does not yet exist, no risk of the model sitting near its own answer key, and
the three stage gates that blocked all progress disappear. Nothing is lost that
cannot be added later, since grading consumes the evidence table rather than
producing it.

Numbers 1-60 keep their v3 meaning. New requirements are appended as 61-68.
Every anchor is asserted to match exactly once, so a silent no-op cannot occur.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "specs", "research-methodology-tool-specs-v3.md")
DST = os.path.join(ROOT, "specs", "research-methodology-tool-specs-v4.md")

# Specs whose subject is grading, scoring, validation of grades, or the stages
# that exist only to gate grading. Kept in place, marked deferred.
DEFERRED = [8, 9, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 32, 34, 36, 37, 38,
            39, 40, 41, 42, 43, 44, 49, 50, 51, 52, 54, 55, 56]

DEFER_MARK = ("**[DEFERRED in v4 — grading layer.** Retained for its numbering and its "
              "design, not in scope for the shipped tool. See Scope of v4.] ")

# Targeted rewrites: spec number -> (must appear in the v3 line, replacement line)
REWRITES = {
    7: ("**Stage 0 — retrieval layer.**",
        "7. **The tool: an evidence dossier.** Given a question, the tool searches, "
        "identifies and de-duplicates sources, extracts descriptive metadata from the text "
        "each channel returned, and presents the result for the reader to evaluate. It "
        "produces no grade, no score, no ranking and no synthesised answer. Passes when a "
        "run produces a dossier in which every source is accounted for and every extracted "
        "field is either traceable to a quoted span or marked not stated (specs 61-65)."),
    10: ("**Stage 3",
         "10. **Survey mode (later).** Many questions per run, with the same dossier output "
         "per question plus an evidence-gap map. Out of scope until single-question runs have "
         "been used enough to know what the output should contain."),
    33: ("Citation audit",
         "33. **Citation audit.** Every source shown appears in a tool result, carries the "
         "identifiers the tool reports for it, and — where a field asserts what the source "
         "found — a verbatim span from the retrieved text supporting that field. Retraction and "
         "correction status is checked for every source via Crossref `updated-by`. The audit is "
         "now a property of the dossier rather than a gate on grading: a field with no "
         "locatable span is displayed as unsupported, not suppressed."),
}

NEW = """
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
"""

SCOPE = """
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
"""


def main():
    with open(SRC) as fh:
        src = fh.read()
    lines = src.split("\n")

    # 1. rewrite the stage/audit specs
    for num, (needle, replacement) in REWRITES.items():
        idx = [i for i, l in enumerate(lines) if l.startswith(f"{num}. ")]
        assert len(idx) == 1, (num, len(idx))
        assert needle in lines[idx[0]], (num, needle, lines[idx[0]][:120])
        lines[idx[0]] = replacement

    # 2. mark the grading specs deferred, in place
    marked = 0
    for num in DEFERRED:
        idx = [i for i, l in enumerate(lines) if l.startswith(f"{num}. ")]
        assert len(idx) == 1, (num, len(idx))
        body = lines[idx[0]][len(f"{num}. "):]
        assert not body.startswith("**[DEFERRED"), num
        lines[idx[0]] = f"{num}. {DEFER_MARK}{body}"
        marked += 1

    doc = "\n".join(lines)

    # 3. scope section immediately after the title block
    m = re.search(r"\n## ", doc)
    assert m, "no section heading found in v3"
    doc = doc[:m.start()] + "\n" + SCOPE + doc[m.start():]

    # 4. append the new requirements
    doc = doc.rstrip() + "\n" + NEW

    doc = doc.replace("research-methodology-tool-specs-v3", "research-methodology-tool-specs-v4")
    with open(DST, "w") as fh:
        fh.write(doc)

    nums = [int(x.group(1)) for x in re.finditer(r"^(\d{1,2})\. ", doc, re.M)]
    missing = [n for n in range(1, 69) if n not in nums]
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    print(f"specs present: {len(set(nums))} | missing 1-68: {missing} | dupes: {dupes}")
    print(f"deferred marked: {marked} | rewritten: {sorted(REWRITES)}")
    print(f"v3 {len(src)} bytes -> v4 {len(doc)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
