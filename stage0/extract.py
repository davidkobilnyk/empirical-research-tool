#!/usr/bin/env python3
"""Per-source descriptive extraction. No grading, no scoring, no ranking.

What this does: read the text a channel actually returned about a source and
record what the source IS, what it EXAMINED, and what it REPORTS -- in the
source's own terms. What it deliberately does not do: judge quality, assign a
tier, or order sources by merit. Those are the reader's job.

The field list is the trigger-field list from the Stage 1 checklist draft with
the moves removed. That is not a coincidence: the fields a rubric would need in
order to downgrade a source are the same fields a reader needs in order to
evaluate it. Keeping the fields and dropping the verdicts is the whole design.

Two rules make machine extraction checkable without a validation set:

  1. Every field is either a value the text states, or the literal string
     "not stated". Nothing is inferred, and absence is recorded as absence --
     "not stated" is a finding about the source, not a gap in the extraction.
  2. Any field asserting what the source found carries a verbatim quote from
     the retrieved text. A reader can then check the claim against the source
     without leaving the page, which is what spec 33's citation audit asks for.

Extraction is model-produced and therefore fallible. The quotes are the audit
surface; the output says so.
"""
import argparse
import json
import unicodedata
import os
import re
import sys

NOT_STATED = "not stated"

FIELDS = {
    "source_type": 'one of "empirical comparison", "replication study", '
                   '"meta-analysis or synthesis", "simulation", "proof or analytic result", '
                   '"review", "guideline or consensus statement", "argument or commentary", "other"',
    "unit_and_n": "what was studied and how many of it, as stated (e.g. '193 preregistered vs "
                  "193 matched studies', '15,992 tests')",
    "own_preregistration": '"yes", "no", or "not stated" -- whether THIS source\'s own study '
                           "was preregistered",
    "original_or_replication": 'one of "original", "direct replication", "conceptual replication", '
                               '"reanalysis of existing data", "not applicable"',
    "reported_direction": 'how the source\'s own reported findings bear on the question: '
                          '"supports", "contradicts", "mixed", or "background" (does not bear '
                          "on it directly). This describes the source's reported result, not "
                          "its quality.",
    "key_finding": "one sentence in the source's own terms, or \"not stated\"",
    "heterogeneity_or_precision": "any interval, heterogeneity or precision statement, as stated",
    "bias_correction": "name of any publication-bias correction method used, else \"not stated\"",
    "data_or_code": "any statement about data or code availability, else \"not stated\"",
    "scope": "the field, era, population or task the source's claims are scoped to, as stated",
}

QUOTED = ("reported_direction", "key_finding")


def prompt_for(question, title, text):
    spec = "\n".join(f" {k}: {v}" for k, v in FIELDS.items())
    return (f"QUESTION UNDER STUDY: {question}\n\n"
            f"SOURCE TITLE: {title or '(no title supplied)'}\n"
            f"RETRIEVED TEXT (this is all you may use):\n{text[:3500]}\n\n"
            "Return ONLY a JSON object with these keys:\n" + spec +
            '\n quote: a verbatim span of at most 30 words, copied exactly from the retrieved '
            'text, that supports your reported_direction and key_finding. Use null ONLY if the '
            'text contains no such span.\n'
            '\nRules: use the exact string "not stated" for anything the text does not say. Do '
            "not infer, do not use knowledge from outside the retrieved text, and do not "
            "evaluate the source's quality.")


def _norm(s):
    """Fold case, unicode punctuation and spacing; keep letters, digits, spaces.

    Needed because abstracts arrive with em dashes, curly quotes and parentheses
    that survive differently through four channels' formatting.
    """
    s = unicodedata.normalize("NFKD", s or "").lower()
    for a, b in (("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"'),
                 ("\u2013", "-"), ("\u2014", "-")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9 ]+", " ", re.sub(r"\s+", " ", s)).strip()


def verify_quote(quote, text):
    """Three states, because the distinction is the whole point of quoting.

      verified              -- the span appears in the retrieved text
      verified (elided)     -- every word appears in order, with material
                               omitted in between: the model dropped
                               parentheticals such as "(Hypothesis 1)" rather
                               than inventing anything. Measured: this was 5 of
                               7 apparent failures on the first real run.
      NOT FOUND             -- the words do not appear in order. Reported, never
                               dropped: a model producing plausible unsourced
                               quotes is precisely what the reader must see.

    An elided quote is still a quote a reader can locate; a NOT FOUND one is a
    reason to distrust every field on that source.
    """
    if not quote:
        return "no quote offered"
    nq, nt = _norm(quote), _norm(text)
    if not nq:
        return "no quote offered"
    if nq in nt:
        return "verified"
    words, pos = nq.split(), 0
    for w in words:
        found = nt.find(" " + w + " ", pos)
        if found == -1:
            found = nt.find(w, pos)
        if found == -1:
            return "NOT FOUND in retrieved text"
        pos = found + len(w)
    span = pos - nt.find(words[0])
    return ("verified (elided)" if span <= 3 * len(nq) + 60
            else "NOT FOUND in retrieved text")


def extract(question, sources, llm, max_concurrency=8, char_cap=3500):
    """sources: [{work_id, title, text, ...}] -> [{...fields, quote, quote_status}]"""
    reqs = [{"prompt": prompt_for(question, s.get("display_title") or s.get("title"),
                                  s.get("text") or "")} for s in sources]
    results = llm(reqs, max_concurrency=max_concurrency) if len(reqs) > 1 else [llm(reqs[0])]
    out = []
    for s, r in zip(sources, results):
        rec = {k: NOT_STATED for k in FIELDS}
        rec.update({"work_id": s.get("work_id"), "doi": s.get("doi_normalised") or s.get("doi"),
                    "title": s.get("display_title") or s.get("title"),
                    "access": s.get("access"), "channels": s.get("channels"),
                    "text_chars": len(s.get("text") or "")})
        if isinstance(r, dict) and "error" in r:
            rec["extraction_error"] = str(r["error"])[:200]
            rec["quote"], rec["quote_status"] = None, "extraction failed"
            out.append(rec)
            continue
        m = re.search(r"\{.*\}", r.get("text", ""), re.S)
        try:
            parsed = json.loads(m.group(0)) if m else {}
        except json.JSONDecodeError:
            parsed = {}
            rec["extraction_error"] = "model output was not parseable JSON"
        for k in FIELDS:
            v = parsed.get(k)
            rec[k] = NOT_STATED if v in (None, "", "null") else v
        rec["quote"] = parsed.get("quote") or None
        rec["quote_status"] = verify_quote(rec["quote"], s.get("text") or "")
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser(description="descriptive extraction over a run's sources")
    ap.add_argument("rundir")
    ap.add_argument("--question", help="defaults to the run's own question")
    a = ap.parse_args()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit("extraction needs a kernel with host.llm; import extract() and pass it in")


if __name__ == "__main__":
    main()
