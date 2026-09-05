#!/usr/bin/env python3
"""Turn a completed run into a dossier: select, extract, render.

This is the glue that decides which sources appear. It used to exist only as
hand-typed cells with keyword lists tuned to one question, which meant the
pipeline did not actually run on an arbitrary question. Two rules now govern it:

  1. **The default shows every source with usable text.** No relevance
     filtering, no ranking. Retrieval already restricted the corpus by issuing
     the query; filtering again here would be a second, unstated judgment about
     relevance layered on top of the channels' own.
  2. **A filter is optional, caller-supplied, and printed verbatim.** If you
     pass term groups, a source must match at least one term from EVERY group
     to appear, the groups are reproduced in the output, and everything filtered
     out is listed in the exclusions with its reason. A filter you cannot see is
     an evaluation you cannot audit (spec 62, spec 63).
"""
import importlib.util
import json
import os

ACCESS_RANK = {"full text": 0, "extracted fields": 1, "abstract only": 2}
MIN_TEXT_CHARS = 150


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def modules(here=None):
    if here is None:
        here = os.path.dirname(os.path.abspath(__file__))
    return {n: load_module(os.path.join(here, n + ".py"), n)
            for n in ("retrieve", "link", "extract", "present")}


def matches(blob, groups):
    """Every group must contribute at least one hit (AND across groups, OR within)."""
    low = blob.lower()
    return all(any(t.lower() in low for t in group) for group in groups)


def select(rundir, term_groups=None):
    """-> (sources to show, exclusions {reason: [labels]}, notes)

    One record per work, preferring the best access level, retracted excluded,
    unlinked sources INCLUDED and marked (spec 63: a metadata gap is not grounds
    for hiding a source).
    """
    with open(os.path.join(rundir, "sources.json")) as fh:
        sources = json.load(fh)
    works = {}
    wpath = os.path.join(rundir, "works.json")
    if os.path.exists(wpath):
        with open(wpath) as fh:
            works = json.load(fh).get("works", {})
    cov = {}
    cpath = os.path.join(rundir, "coverage.json")
    if os.path.exists(cpath):
        with open(cpath) as fh:
            cov = json.load(fh)
    integrity = cov.get("integrity") or {}
    retracted = {d for d, v in integrity.items() if v.get("status") == "retracted"}

    doi2work = {d: w for w, v in works.items() for d in v.get("dois", [])}
    titles = {w: v.get("title") for w, v in works.items()}

    excl, best = {}, {}
    def drop(reason, label):
        excl.setdefault(reason, []).append(label or "(unidentified)")

    for rec in sources:
        doi = (rec.get("doi_normalised") or "").lower()
        wid = doi2work.get(doi)
        label = (titles.get(wid) if wid else None) or rec.get("title") or doi
        # Retraction is checked FIRST, deliberately. It is the more informative
        # reason and spec 67 requires a retracted source to be excluded AND
        # named; checking text first silently relabels a retracted source as
        # "no usable text" whenever its snippet happens to be short, which is
        # exactly the disclosure the reader needs and would not get.
        if doi in retracted or (wid and set(works[wid].get("dois", [])) & retracted):
            drop("retracted (Crossref / Retraction Watch notice)", label)
            continue
        if len(rec.get("text") or "") < MIN_TEXT_CHARS:
            drop("channel returned no usable text to extract from", label)
            continue
        key = wid or ("unlinked:" + (rec.get("title") or doi or "")[:60].lower())
        cand = dict(rec)
        cand["work_id"] = key
        cand["display_title"] = (titles.get(wid) if wid else None) or rec.get("title")
        cand["linked"] = bool(wid)
        cur = best.get(key)
        if cur is None or ACCESS_RANK.get(cand.get("access"), 9) < ACCESS_RANK.get(cur.get("access"), 9):
            best[key] = cand

    shown = list(best.values())
    if term_groups:
        kept = []
        for c in shown:
            blob = (c.get("display_title") or "") + " " + (c.get("text") or "")
            if matches(blob, term_groups):
                kept.append(c)
            else:
                drop("did not match the caller-supplied filter (see filter above)",
                     c.get("display_title"))
        shown = kept
    shown.sort(key=lambda c: (c.get("display_title") or "").lower().lstrip("0123456789 ."))
    notes = {"integrity": integrity, "linkage": (json.load(open(wpath))["stats"]
                                                 if os.path.exists(wpath) else None),
             "question": cov.get("question"), "queries": cov.get("queries") or {},
             "unlinked_shown": sum(1 for c in shown if not c.get("linked"))}
    return shown, excl, notes


def selection_block(rundir, notes, shown, term_groups):
    channels = sorted({c for c in (notes.get("linkage") or {}).get("query_set_overlap_works", {})}) or None
    filt = ("none — every source with usable retrieved text is shown"
            if not term_groups else
            "a source is shown only if it matches at least one term from EVERY group: "
            + "; ".join("[" + ", ".join(g) + "]" for g in term_groups))
    return {
        "channels searched": ", ".join(channels) if channels else "see the run's coverage note",
        "unit shown": "distinct works where a DOI resolved (copies merged), otherwise the "
                      "retrieved record as returned",
        "filter applied after retrieval": filt,
        "minimum text": f"{MIN_TEXT_CHARS} characters of retrieved text, below which there is "
                        "nothing to extract from",
        "ordering": "alphabetical by title — not relevance, recency or citation count",
        "what was NOT done": "no grading, no scoring, no weighting, no synthesis, and no answer "
                             "to the question",
    }


def build(rundir, llm, term_groups=None, max_concurrency=8, mods=None):
    """Select, extract, render. Returns (dossier path, stats)."""
    mods = mods or modules()
    shown, excl, notes = select(rundir, term_groups)
    if not shown:
        raise RuntimeError("no sources with usable text; check the run's coverage note")
    extracted = mods["extract"].extract(notes["question"] or "", shown, llm,
                                        max_concurrency=max_concurrency)
    for e in extracted:
        if not e.get("doi"):
            e["integrity_note"] = ("no DOI in the retrieved record, so retraction status "
                                   "was not checkable")
    doc = mods["present"].dossier(notes["question"] or "", notes["queries"], extracted,
                                  selection_block(rundir, notes, shown, term_groups), excl,
                                  integrity=notes["integrity"], linkage=notes["linkage"],
                                  run_id=os.path.basename(rundir.rstrip("/")))
    path = mods["present"].write(rundir, doc)
    with open(os.path.join(rundir, "extracted.json"), "w") as fh:
        json.dump(extracted, fh, indent=1)
    counts = {}
    for e in extracted:
        counts[e.get("reported_direction")] = counts.get(e.get("reported_direction"), 0) + 1
    quotes = {}
    for e in extracted:
        quotes[e.get("quote_status")] = quotes.get(e.get("quote_status"), 0) + 1
    return path, {"sources_shown": len(extracted), "directions": counts, "quotes": quotes,
                  "excluded": {k: len(v) for k, v in excl.items()},
                  "unlinked_shown": notes["unlinked_shown"]}
