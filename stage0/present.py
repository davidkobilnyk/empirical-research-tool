#!/usr/bin/env python3
"""Render an evidence dossier: the sources, their metadata, and how the list was made.

No tiers, no scores, no ordering by merit. The reader evaluates; this presents.

The design rule that does the most work here: **a transparency tool smuggles
evaluation in through selection and ordering.** Deciding which 16 of 80 works
are "on-topic", and in what order, is a judgment -- so the rules that made the
list are printed above the list, every exclusion is named with its reason, and
the default order is neutral (by publication year, then title), never by
relevance score or by anything resembling quality.
"""
import json
import os
import re


def _row(v, cap=44):
    s = "—" if v in (None, "", "not stated") else str(v)
    s = re.sub(r"\s+", " ", s)
    return (s[:cap - 1] + "…") if len(s) > cap else s


def dossier(question, queries, extracted, selection, exclusions, integrity=None,
            linkage=None, run_id=None):
    integrity = integrity or {}
    L = [f"# Evidence dossier — {question}", ""]
    if run_id:
        L += [f"Run `{run_id}`. Sources and metadata only: **no grading, no scoring, and no "
              "ordering by quality.**", ""]

    L += ["## The question as searched", ""]
    for name, q in (queries or {}).items():
        L += [f"- **{name}**: {q}"]

    L += ["", "## How this list was made", "",
          "Read this before the table: which sources appear here is a set of decisions, and "
          "they are listed so you can disagree with them.", ""]
    for k, v in selection.items():
        L += [f"- **{k}**: {v}"]

    if exclusions:
        L += ["", "### Excluded, with reasons", "",
              "Nothing is dropped silently. Every source the search returned but this dossier "
              "does not show is here.", "",
              "| Reason | Count | Sources |", "|---|---|---|"]
        for reason, items in sorted(exclusions.items()):
            names = "; ".join(_row(i, 60) for i in items[:4]) + (" …" if len(items) > 4 else "")
            L += [f"| {reason} | {len(items)} | {names or '—'} |"]

    L += ["", f"## Sources ({len(extracted)})", "",
          "Ordered alphabetically by title. That order carries no judgment: it is not "
          "relevance, recency or citation count.", "",
          "| # | Source | Type | Reports | Unit and N | Prereg | Access | Integrity |",
          "|---|---|---|---|---|---|---|---|"]
    for i, e in enumerate(extracted, 1):
        st = (integrity.get(e.get("doi")) or {}).get("status", "not checked")
        L += [f"| {i} | {_row(e.get('title'), 46)} | {_row(e.get('source_type'), 24)} | "
              f"{_row(e.get('reported_direction'), 12)} | {_row(e.get('unit_and_n'), 30)} | "
              f"{_row(e.get('own_preregistration'), 11)} | {_row(e.get('access'), 16)} | {st} |"]

    L += ["", "## Each source in detail", ""]
    for i, e in enumerate(extracted, 1):
        L += [f"### {i}. {e.get('title') or '(no title)'}", ""]
        if e.get("doi"):
            L += [f"`{e['doi']}` · [doi.org/{e['doi']}](https://doi.org/{e['doi']})", ""]
        L += [f"- **What it is**: {_row(e.get('source_type'), 200)}",
              f"- **What it examined**: {_row(e.get('unit_and_n'), 240)}",
              f"- **What it reports**: {_row(e.get('key_finding'), 400)}",
              f"- **Direction relative to the question**: {_row(e.get('reported_direction'), 40)}",
              f"- **Original or replication**: {_row(e.get('original_or_replication'), 60)}",
              f"- **Its own pre-registration**: {_row(e.get('own_preregistration'), 40)}",
              f"- **Precision / heterogeneity as stated**: {_row(e.get('heterogeneity_or_precision'), 240)}",
              f"- **Publication-bias correction**: {_row(e.get('bias_correction'), 120)}",
              f"- **Data or code**: {_row(e.get('data_or_code'), 160)}",
              f"- **Scope the source claims**: {_row(e.get('scope'), 240)}"]
        st = (integrity.get(e.get("doi")) or {}).get("status")
        if st:
            L += [f"- **Retraction / correction status**: {st}"]
        if e.get("channels"):
            L += [f"- **Found via**: {', '.join(e['channels'])} "
                  f"({e.get('text_chars', 0)} characters of text retrieved)"]
        q, qs = e.get("quote"), e.get("quote_status")
        if q:
            L += ["", f"> {q}", "", f"Quote check: **{qs}**."]
        else:
            L += ["", f"No quote available — {qs}. The fields above are unsupported by a "
                  "verbatim span and should be checked against the source."]
        if e.get("extraction_error"):
            L += ["", f"Extraction problem: {e['extraction_error']}"]
        L += [""]

    unverified = [i for i, e in enumerate(extracted, 1) if e.get("quote_status") != "verified"]
    L += ["## What this dossier does not tell you", "",
          "- **No quality judgment.** Nothing here says a source is strong, weak, or better "
          "than another. Two sources reporting opposite findings appear side by side with equal "
          "weight, and reconciling them is your job.",
          "- **Direction is not agreement.** *Reports* describes what a source says about the "
          "question, not whether it is right.",
          "- **The metadata is machine-extracted** from the text each channel returned, which "
          "for most sources is an abstract or a passage rather than the full paper. A field "
          "reading “not stated” means the retrieved text did not say it — not that the paper "
          "does not report it.",
          f"- **Quote verification**: {len(extracted) - len(unverified)} of {len(extracted)} "
          f"sources carry a quote found verbatim in the retrieved text."
          + (f" Unverified: {', '.join('#' + str(i) for i in unverified)}." if unverified else ""),
          "- **Coverage is not completeness.** See the run's coverage note for what was "
          "searched, what each channel returned, and what was unreachable."]
    if linkage:
        L += [f"- **Duplicate copies**: {linkage.get('records')} retrieved records resolve to "
              f"{linkage.get('works')} distinct works; one study can hold a preprint, a "
              "repository copy and a journal DOI. Sources below are works, not records."]
    return "\n".join(L) + "\n"


def write(rundir, text, name="evidence-dossier.md"):
    path = os.path.join(rundir, name)
    with open(path, "w") as fh:
        fh.write(text)
    return path
