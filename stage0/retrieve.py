#!/usr/bin/env python3
"""Stage 0 retrieval: search, parse, deduplicate, report coverage. No grading.

Specification references are to specs/research-methodology-tool-specs-v3.md.

  spec 7   Stage 0 produces a structured evidence table with no grades
  spec 15  the search strategy is written before searching and recorded verbatim
  spec 16  parallel supporting and disconfirming query sets
  spec 18  each source tagged full text / extracted fields / abstract only
  spec 33  every cited source exists and is not retracted
  spec 47  coverage note reports what was searched and what was missed
  spec 57  multi-hop routes are verified, never allowed to degrade silently
  spec 58  a channel's output is a lead generator until characterised

Two entry points:

    run_live(question, mcp, servers, ...)   # needs the MCP-capable kernel
    run_replay(payload_path, ...)           # offline, from records/*.json

`run_live` takes the MCP callable and a {channel: server_name} mapping as
arguments rather than importing either. Connector server identifiers are
specific to one environment's connector attachments, so hardcoding them makes
the script unrunnable elsewhere; resolve them at the call site.
"""
import argparse
import datetime
import importlib.util
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_KERNEL = os.path.join(REPO_ROOT, "skills", "doi-source-identity", "kernel.py")


def load_identity():
    """Load the DOI/dedupe helpers from the skill, so there is one implementation."""
    spec = importlib.util.spec_from_file_location("doi_source_identity", SKILL_KERNEL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------- query sets
def query_sets(question, disconfirming=None):
    """spec 16: the disconfirming arm is worded for the opposite conclusion.

    Returned verbatim in the manifest, because spec 15 requires the strategy to
    be recorded as executed rather than described.
    """
    if disconfirming is None:
        disconfirming = ("Evidence that the following does not hold, or fails to "
                         "replicate: " + question)
    return {"supporting": question, "disconfirming": disconfirming}


# ----------------------------------------------------------------- parsers
# One parser per channel: connector payload -> [{doi, title, access, extra}].
# Shapes differ materially: two return dicts with a results array, one returns
# passages that must be collapsed to articles, and two return prose.

def parse_records_array(payload):
    out = []
    for r in (payload or {}).get("results", []):
        oa = r.get("oa")
        out.append({"doi": r.get("doi"), "title": r.get("title"),
                    "access": "full text" if oa else "abstract only",
                    "extra": {k: r.get(k) for k in ("year", "venue", "cited_by_count", "url")}})
    return out


def parse_passages(payload):
    """Passage-level hits collapsed to one record per article."""
    seen, out = set(), []
    for r in (payload or {}).get("results", []):
        md = r.get("metadata") or {}
        key = (r.get("doi") or md.get("title") or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append({"doi": r.get("doi"), "title": md.get("title"),
                    "access": "extracted fields",   # passages, not whole text
                    "extra": {"year": md.get("year"), "passages": 1}})
    return out


def parse_numbered_with_doi(payload):
    """Prose blocks: `N. Title ... DOI: x`. Blocks without a DOI are skipped;
    numbered lines inside abstracts would otherwise be counted as records."""
    text = payload if isinstance(payload, str) else json.dumps(payload)
    out = []
    for title, doi in re.findall(r"\n\s*\d+\.\s*(.+?)\n.*?DOI:\s*(\S+)", text, re.S):
        out.append({"doi": doi, "title": title.split("\n")[0].strip(),
                    "access": "abstract only", "extra": {}})
    return out


def parse_numbered_links(payload):
    """Prose with `[n] [Title](url)` and no DOIs — title is the only identity."""
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return [{"doi": None, "title": t.strip(), "access": "abstract only", "extra": {}}
            for t in re.findall(r"\[\d+\]\s*\[([^\]]+)\]", text)]


# channel -> (method, kwargs builder, parser, default limit)
CHANNELS = {
    "fasttrack": ("search_papers", lambda q, n: {"query": q, "limit": n},
                  parse_records_array, 20),
    "scholargw": ("semanticSearch", lambda q, n: {"query": q, "topN": n},
                  parse_passages, 15),
    "scispace":  ("search-papers", lambda q, n: {"searchQuestion": q},
                  parse_numbered_with_doi, None),
    "consensus": ("search", lambda q, n: {"query": q},
                  parse_numbered_links, None),
}


# -------------------------------------------------------------- integrity
def integrity_check(dois, email=None, cap=None):
    """spec 33: existence and retraction status per DOI, from one Crossref record.

    'unknown' is kept distinct from 'clean' — a failed lookup must never be
    recordable as a passing check.
    """
    ident = load_identity()
    out = {}
    for i, d in enumerate(dois):
        if cap is not None and i >= cap:
            out[d] = {"status": "not checked (cap reached)"}
            continue
        rs = ident.retraction_status(d, email=email)
        if rs is None:
            out[d] = {"status": "unknown", "reason": "lookup failed"}
        elif rs["retracted"]:
            out[d] = {"status": "retracted", "notices": rs["notices"]}
        elif rs["corrected"]:
            out[d] = {"status": "corrected", "notices": rs["notices"]}
        else:
            out[d] = {"status": "clean"}
    return out


# ------------------------------------------------------------------- core
def collate(per_arm):
    """per_arm: {'channel/arm': [records]} -> unique sources + coverage stats."""
    ident = load_identity()
    tagged = []
    for key, recs in per_arm.items():
        channel, _, arm = key.partition("/")
        for r in recs:
            tagged.append(dict(r, channel=channel, arm=arm))

    unique, index = ident.dedupe_sources(tagged)
    for k, rec in unique.items():
        rec["channels"] = sorted(index[k])
        # Take the DOI from the canonical key, not from the first record seen: a
        # source first returned by a channel that supplies no DOIs, then merged by
        # title with a DOI-bearing record, does have a resolvable DOI. Reading the
        # first record instead undercounts those and drops them from the spec 33
        # integrity check.
        rec["doi_normalised"] = None if k.startswith("title:") else k

    stats = {
        "records_returned": len(tagged),
        "unique_sources": len(unique),
        "duplicate_rate": round(1 - len(unique) / len(tagged), 3) if tagged else None,
        "with_doi": sum(1 for r in unique.values() if r["doi_normalised"]),
        "multi_channel": sum(1 for ch in index.values() if len(ch) > 1),
        "per_channel_arm": {k: len(v) for k, v in per_arm.items()},
        "access_mix": {},
    }
    for r in unique.values():
        a = r.get("access") or "unknown"
        stats["access_mix"][a] = stats["access_mix"].get(a, 0) + 1
    return unique, stats


def coverage_note(question, queries, stats, integrity, channels_used, unavailable):
    """spec 47: what was searched, what it yielded, and what was not reachable."""
    L = [f"# Coverage note — {question}", "",
         f"Run {datetime.date.today().isoformat()}. Stage 0: retrieval only, no grades.", "",
         "## Query sets (spec 15, recorded as executed)", ""]
    for arm, q in queries.items():
        L += [f"- **{arm}**: {q}"]
    L += ["", "## Channels and yield", "", "| Channel / arm | Records |", "|---|---|"]
    for k, n in sorted(stats["per_channel_arm"].items()):
        L += [f"| {k} | {n} |"]
    L += ["",
          f"{stats['records_returned']} records returned, **{stats['unique_sources']} unique "
          f"sources** after deduplication ({int(100 * (stats['duplicate_rate'] or 0))}% duplicates); "
          f"{stats['with_doi']} carry a resolvable DOI.",
          "",
          f"{stats['multi_channel']} source(s) were returned by more than one channel. Channels "
          "drawing on overlapping upstream corpora can still return near-disjoint sets, so this "
          "figure is measured per run rather than assumed (spec 58).",
          "", "## Access mix (spec 18)", ""]
    for a, n in sorted(stats["access_mix"].items()):
        L += [f"- {a}: {n}"]
    if integrity:
        tally = {}
        for v in integrity.values():
            tally[v["status"]] = tally.get(v["status"], 0) + 1
        L += ["", "## Integrity (spec 33)", ""]
        for s, n in sorted(tally.items()):
            L += [f"- {s}: {n}"]
        if tally.get("retracted"):
            L += ["", "**A retracted source is present. Any run citing it fails the "
                  "citation audit** — it is not sufficient to note it."]
        if tally.get("unknown"):
            L += ["", "Sources with status *unknown* had a failed lookup. Unknown is not clean; "
                  "re-check before the audit gate."]
    if unavailable:
        L += ["", "## Not reachable this run", ""]
        for name, why in sorted(unavailable.items()):
            L += [f"- **{name}**: {why}"]
    L += ["", "## Limits that hold regardless of this run", "",
          "- No licensed index (Scopus, Web of Science, Dimensions) and no Google Scholar.",
          "- No book-length literature; the Cochrane and GRADE handbooks are reachable, monographs are not.",
          "- PubPeer refuses automated clients, so that channel is a manual check.", ""]
    return "\n".join(L)


def write_run(outdir, question, queries, unique, stats, integrity, note, manifest):
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "sources.json"), "w") as fh:
        json.dump(list(unique.values()), fh, indent=1)
    with open(os.path.join(outdir, "coverage.json"), "w") as fh:
        json.dump({"question": question, "queries": queries, "stats": stats,
                   "integrity": integrity, "manifest": manifest}, fh, indent=1)
    with open(os.path.join(outdir, "coverage-note.md"), "w") as fh:
        fh.write(note)
    return outdir


def slug(s, n=40):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")[:n]


# ------------------------------------------------------------- entry points
def run_live(question, mcp, servers, disconfirming=None, limits=None, email=None,
             outdir=None, check_integrity=True, integrity_cap=None):
    """servers: {'fasttrack': '<server name>', ...}. Missing or failing channels are
    recorded as unavailable rather than skipped silently (specs 47, 57)."""
    queries = query_sets(question, disconfirming)
    limits = limits or {}
    per_arm, unavailable = {}, {}
    for ch, (method, build, parser, default_n) in CHANNELS.items():
        server = servers.get(ch)
        if not server:
            unavailable[ch] = "no server configured for this channel"
            continue
        for arm, q in queries.items():
            try:
                payload = mcp(server, method, **build(q, limits.get(ch, default_n)))
                per_arm[f"{ch}/{arm}"] = parser(payload)
            except Exception as e:                      # spec 57: never silent
                unavailable[f"{ch}/{arm}"] = f"{type(e).__name__}: {e}"[:200]
    if not per_arm:
        raise RuntimeError("no channel returned records; retrieval layer failed")

    unique, stats = collate(per_arm)
    integrity = {}
    if check_integrity:
        dois = [r["doi_normalised"] for r in unique.values() if r["doi_normalised"]]
        integrity = integrity_check(dois, email=email, cap=integrity_cap)
    manifest = {"mode": "live", "date": datetime.date.today().isoformat(),
                "limits": {ch: limits.get(ch, CHANNELS[ch][3]) for ch in CHANNELS},
                "channels_configured": sorted(servers)}
    note = coverage_note(question, queries, stats, integrity, sorted(per_arm), unavailable)
    outdir = outdir or os.path.join(REPO_ROOT, "runs",
                                    datetime.date.today().isoformat() + "-" + slug(question))
    return write_run(outdir, question, queries, unique, stats, integrity, note, manifest), stats


def run_replay(payload_path, question="(replayed payloads)", outdir=None,
               check_integrity=False, email=None):
    """Re-parse dated payloads from records/. Verifies the parsers and dedupe
    against evidence; the connectors themselves are not reproducible."""
    with open(payload_path) as fh:
        raw = json.load(fh)
    per_arm, unavailable = {}, {}
    for key, payload in raw.items():
        ch = key.partition("/")[0]
        if ch not in CHANNELS:
            unavailable[key] = "no parser for this channel"
            continue
        if isinstance(payload, dict) and "__error__" in payload:
            unavailable[key] = payload["__error__"]
            continue
        per_arm[key] = CHANNELS[ch][2](payload)
    unique, stats = collate(per_arm)
    integrity = {}
    if check_integrity:
        dois = [r["doi_normalised"] for r in unique.values() if r["doi_normalised"]]
        integrity = integrity_check(dois, email=email)
    queries = {"(replay)": "queries as executed on the payload date"}
    manifest = {"mode": "replay", "payloads": os.path.basename(payload_path),
                "date": datetime.date.today().isoformat()}
    note = coverage_note(question, queries, stats, integrity, sorted(per_arm), unavailable)
    outdir = outdir or os.path.join(REPO_ROOT, "runs", "replay-" +
                                    os.path.basename(payload_path).replace(".json", ""))
    return write_run(outdir, question, queries, unique, stats, integrity, note, manifest), stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--replay", metavar="PAYLOAD_JSON",
                    help="re-parse dated connector payloads from records/")
    ap.add_argument("--check-integrity", action="store_true",
                    help="run the spec 33 existence and retraction check (needs network)")
    ap.add_argument("--outdir")
    a = ap.parse_args()
    if not a.replay:
        sys.exit("live retrieval needs the MCP-capable kernel: import this module and call "
                 "run_live(question, mcp, servers). Use --replay for the offline path.")
    out, stats = run_replay(a.replay, outdir=a.outdir, check_integrity=a.check_integrity)
    print(json.dumps(stats, indent=1))
    print("written to", out)
