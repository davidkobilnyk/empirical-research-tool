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
def query_sets(question, disconfirming):
    """spec 16: the disconfirming set is worded for the opposite conclusion.

    The disconfirming query is REQUIRED and has no template default, because a
    template does not produce one. This was measured: an earlier default of
    "Evidence that the following does not hold, or fails to replicate: <question>"
    embeds the question verbatim, and semantic search returns largely the same
    papers. Against a hand-written opposite query on the same day and channels,
    the template doubled the number of sources appearing in BOTH query sets (26 vs 12)
    and cut unique sources from 93 to 80. Spec 16 was satisfied in form and not
    in substance.

    Write the disconfirming set as the negated *claim*, not as a meta-request
    about the claim: "pre-registration does not reduce publication bias", never
    "evidence that pre-registration does not improve replication".

    Returned verbatim in the manifest, because spec 15 requires the strategy to
    be recorded as executed rather than described.
    """
    if not disconfirming or not str(disconfirming).strip():
        raise ValueError(
            "a disconfirming query is required (spec 16) and must be written, not "
            "derived from the question: templates that embed the question retrieve "
            "the same literature. Word it as the negated claim.")
    return {"supporting": question, "disconfirming": disconfirming}


def query_set_overlap(per_set):
    """How much the two query sets return the same sources, per channel.

    A disconfirming query set that returns the supporting set's results is not a
    disconfirming channel, however it was worded. Measured every run so the
    failure is visible rather than assumed away.
    """
    out = {}
    channels = {k.partition("/")[0] for k in per_set}
    for ch in channels:
        sets = {k.partition("/")[2]: v for k, v in per_set.items()
                if k.partition("/")[0] == ch}
        if len(sets) < 2:
            continue
        (a, ra), (b, rb) = sorted(sets.items())[:2]
        ka = {(r.get("doi") or r.get("title") or "").lower() for r in ra} - {""}
        kb = {(r.get("doi") or r.get("title") or "").lower() for r in rb} - {""}
        union = ka | kb
        out[ch] = {"shared": len(ka & kb),
                   "jaccard": round(len(ka & kb) / len(union), 3) if union else None}
    return out


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
        elif rs.get("registry") == "not_in_crossref":
            # A valid DOI from another registration agency (DataCite covers arXiv,
            # Zenodo, PsychArchives). Crossref cannot speak to its retraction
            # status, so this is a coverage limit, not a defect in the source.
            out[d] = {"status": "not in crossref", "reason": "another registration agency"}
        elif rs["retracted"]:
            out[d] = {"status": "retracted", "notices": rs["notices"]}
        elif rs["corrected"]:
            out[d] = {"status": "corrected", "notices": rs["notices"]}
        else:
            out[d] = {"status": "clean"}
    return out


# ------------------------------------------------------------------- core
def collate(per_set):
    """per_set: {'channel/query set': [records]} -> unique sources + coverage stats."""
    ident = load_identity()
    tagged = []
    for key, recs in per_set.items():
        channel, _, qset = key.partition("/")
        for r in recs:
            tagged.append(dict(r, channel=channel, query_set=qset))

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
        "per_channel_query_set": {k: len(v) for k, v in per_set.items()},
        "query_set_overlap_records": query_set_overlap(per_set),
        "access_mix": {},
    }
    for r in unique.values():
        a = r.get("access") or "unknown"
        stats["access_mix"][a] = stats["access_mix"].get(a, 0) + 1
    return unique, stats


def linkage_section(lk):
    """Report records and works separately: retrieval is counted in records,
    independence in works (spec 27 / X-3)."""
    mode = lk.get("enrichment_mode", "network")
    L = ["", "## Source identity (linkage)", "",
         f"Linkage ran with registry enrichment **{mode}**."
         + ("" if mode == "network" else " Offline linkage is strictly weaker: without"
            " canonical titles, authors and relations, links that exist are not found."),
         "",
         f"{lk['records']} source records resolve to **{lk['works']} distinct works** "
         f"({lk['redundant_records']} redundant records across {lk['clusters']} clusters; "
         f"largest cluster {lk['largest_cluster']}).",
         "",
         "Counts of *sources* above describe retrieval. Any statement about independent "
         "support must count works: copies of one study share its data, authors and "
         "analysis, and the error from counting records is one-directional — duplicates "
         "only ever add.",
         "",
         f"- linked by version/identity relation: {lk['links_by_relation']}",
         f"- linked by title with an author or year guard: {lk['links_by_title_guarded']}",
         f"- linked by title with no guard available: {lk['links_by_title_unguarded']}",
         f"- title collisions rejected by the guard: {lk['title_collisions_rejected']}",
         f"- records with no DOI: {lk['records_no_doi']}; records with neither DOI nor "
         f"title, so unlinkable: {lk['records_unlinkable']}"]
    if lk.get("works_with_mixed_access"):
        L += ["",
              f"**{lk['works_with_mixed_access']} work(s) carry more than one access level** "
              "across their copies. Under spec 24 an abstract-only source cannot be "
              "downgraded while X-2 takes the maximum per-source tier, so the least "
              "readable copy can set the tier. Grade these at work level."]
    ovw = lk.get("query_set_overlap_works") or {}
    if ovw and "unavailable" not in ovw:
        L += ["", "### Query set overlap, per work (spec 16)", "",
              "| Channel | Shared works | Jaccard |", "|---|---|---|"]
        for ch, v in sorted(ovw.items()):
            L += [f"| {ch} | {v['shared']} | {v['jaccard']} |"]
        named = [(ch, sw) for ch, v in sorted(ovw.items()) for sw in v.get("shared_works", [])]
        if named:
            L += ["", "Works returned by both query sets:", ""]
            seen = set()
            for ch, sw in named:
                if sw["work_id"] in seen:
                    continue
                seen.add(sw["work_id"])
                L += [f"- {(sw['title'] or sw['work_id'])[:70]} "
                      f"({len(sw['dois'])} DOI{'s' if len(sw['dois']) != 1 else ''})"]
        L += ["",
              "No cutoff is applied to these figures, deliberately. A threshold exists to "
              "trigger an action, and there is no validated action here: the only remedy "
              "previously prescribed — re-word the disconfirming query — is measurably "
              "ineffective on channels whose search is weakly sensitive to negation, where "
              "a correctly negated claim still retrieves the supporting set's results. The "
              "index is also coarse at these set sizes: with ten sources per query set one "
              "shared work moves it by about 0.07, so a two-decimal cutoff claims precision "
              "the measurement does not have. Read the named works above, compare the "
              "figure across runs of the same question, and treat a channel that keeps "
              "returning the same works for opposite queries as needing a different "
              "disconfirmation mechanism rather than a better sentence. Whether a gate "
              "belongs here at all is a spec 44 rubric-parameter question, and answering it "
              "needs evidence that high-overlap runs actually miss disconfirming evidence."]
    elif ovw.get("unavailable"):
        L += ["", f"Work-level query set overlap not computed: {ovw['unavailable']}"]
    L += ["",
          "Not covered: work identity is narrower than independence. Two different papers "
          "from one group on one dataset share data and authors and are not independent; "
          "no title-or-DOI linkage detects that."]
    return L


def coverage_note(question, queries, stats, integrity, channels_used, unavailable,
                  linkage=None):
    """spec 47: what was searched, what it yielded, and what was not reachable."""
    L = [f"# Coverage note — {question}", "",
         f"Run {datetime.date.today().isoformat()}. Stage 0: retrieval only, no grades.", "",
         "## Query sets (spec 15, recorded as executed)", ""]
    for qset, q in queries.items():
        L += [f"- **{qset}**: {q}"]
    L += ["", "## Channels and yield", "", "| Channel / query set | Records |", "|---|---|"]
    # runs written before "arm" became "query set" carry the old key; data files
    # outlive code renames
    per_cs = stats.get("per_channel_query_set") or stats.get("per_channel_arm") or {}
    for k, n in sorted(per_cs.items()):
        L += [f"| {k} | {n} |"]
    L += ["",
          f"{stats['records_returned']} records returned, **{stats['unique_sources']} unique "
          f"sources** after deduplication ({int(100 * (stats['duplicate_rate'] or 0))}% duplicates); "
          f"{stats['with_doi']} carry a resolvable DOI.",
          "",
          f"{stats['multi_channel']} source(s) were returned by more than one channel. Channels "
          "drawing on overlapping upstream corpora can still return near-disjoint sets, so this "
          "figure is measured per run rather than assumed (spec 58).",
          ""]
    ov = (stats.get("query_set_overlap_records") or stats.get("query_set_overlap")
          or stats.get("arm_overlap") or {})
    if ov:
        L += ["## Query set overlap, per record (spec 16)", "",
              "How much of the disconfirming set's yield was the supporting set's own "
              "results. A high figure means the channel was searched twice for the same "
              "thing, whatever the query said.", "",
              "**Read the per-work table under Source identity instead where it is "
              "present.** These record-level figures are inflated wherever a channel "
              "returned several copies of one work; they are what is computable before "
              "linkage has run. No threshold is applied to either table: see the note at "
              "the end of the per-work table.", "",
              "| Channel | Shared sources | Jaccard |", "|---|---|---|"]
        for ch, v in sorted(ov.items()):
            L += [f"| {ch} | {v['shared']} | {v['jaccard']} |"]
        L += [""]
    L += ["## Access mix (spec 18)", ""]
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
    if linkage:
        L += linkage_section(linkage)
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
def run_integrity(rundir, email=None, cap=None):
    """spec 33, as a separate phase over a completed run's sources.json.

    Kept separate from retrieval on purpose. Retrieval needs connector access;
    this needs api.crossref.org, and the two are not necessarily reachable from
    the same place — in the environment this was built in they are not. Nesting
    the check inside retrieval made every lookup fail and report 'unknown',
    which is honest but useless. Run this where Crossref is reachable.
    """
    with open(os.path.join(rundir, "sources.json")) as fh:
        sources = json.load(fh)
    with open(os.path.join(rundir, "coverage.json")) as fh:
        cov = json.load(fh)
    dois = [s["doi_normalised"] for s in sources if s.get("doi_normalised")]
    integrity = integrity_check(dois, email=email, cap=cap)

    statuses = {v["status"] for v in integrity.values()}
    if statuses == {"unknown"} and dois:
        raise RuntimeError(
            f"all {len(dois)} lookups failed — check that api.crossref.org is reachable "
            "from this kernel before treating this as a fact about the DOIs")

    cov["integrity"] = integrity
    with open(os.path.join(rundir, "coverage.json"), "w") as fh:
        json.dump(cov, fh, indent=1)
    note = coverage_note(cov["question"], cov["queries"], cov["stats"], integrity,
                         sorted(cov["stats"]["per_channel_query_set"]), {})
    with open(os.path.join(rundir, "coverage-note.md"), "w") as fh:
        fh.write(note)
    tally = {}
    for v in integrity.values():
        tally[v["status"]] = tally.get(v["status"], 0) + 1
    return integrity, tally


def run_live(question, mcp, servers, disconfirming=None, limits=None, email=None,
             outdir=None, check_integrity=False, integrity_cap=None):
    """servers: {'fasttrack': '<server name>', ...}. Missing or failing channels are
    recorded as unavailable rather than skipped silently (specs 47, 57)."""
    queries = query_sets(question, disconfirming)
    limits = limits or {}
    per_set, unavailable, raw = {}, {}, {}
    for ch, (method, build, parser, default_n) in CHANNELS.items():
        server = servers.get(ch)
        if not server:
            unavailable[ch] = "no server configured for this channel"
            continue
        for qset, q in queries.items():
            try:
                payload = mcp(server, method, **build(q, limits.get(ch, default_n)))
                raw[f"{ch}/{qset}"] = payload
                per_set[f"{ch}/{qset}"] = parser(payload)
            except Exception as e:                      # spec 57: never silent
                unavailable[f"{ch}/{qset}"] = f"{type(e).__name__}: {e}"[:200]
    if not per_set:
        raise RuntimeError("no channel returned records; retrieval layer failed")

    unique, stats = collate(per_set)
    integrity = {}
    if check_integrity:
        dois = [r["doi_normalised"] for r in unique.values() if r["doi_normalised"]]
        integrity = integrity_check(dois, email=email, cap=integrity_cap)
    manifest = {"mode": "live", "date": datetime.date.today().isoformat(),
                "limits": {ch: limits.get(ch, CHANNELS[ch][3]) for ch in CHANNELS},
                "channels_configured": sorted(servers)}
    note = coverage_note(question, queries, stats, integrity, sorted(per_set), unavailable)
    outdir = outdir or os.path.join(REPO_ROOT, "runs",
                                    datetime.date.today().isoformat() + "-" + slug(question))
    write_run(outdir, question, queries, unique, stats, integrity, note, manifest)
    # Persist the raw payloads. Connector output is not reproducible, so without
    # them a later question about this run ("why did the counts change?") can only
    # be answered by a fresh experiment rather than a diff. They are also the
    # fixture a future parser change gets tested against.
    with open(os.path.join(outdir, "payloads.json"), "w") as fh:
        json.dump(raw, fh)
    return outdir, stats


def run_replay(payload_path, question="(replayed payloads)", outdir=None,
               check_integrity=False, email=None, queries=None):
    """Re-parse dated payloads from records/. Verifies the parsers and dedupe
    against evidence; the connectors themselves are not reproducible."""
    with open(payload_path) as fh:
        raw = json.load(fh)
    per_set, unavailable = {}, {}
    for key, payload in raw.items():
        ch = key.partition("/")[0]
        if ch not in CHANNELS:
            unavailable[key] = "no parser for this channel"
            continue
        if isinstance(payload, dict) and "__error__" in payload:
            unavailable[key] = payload["__error__"]
            continue
        per_set[key] = CHANNELS[ch][2](payload)
    unique, stats = collate(per_set)
    integrity = {}
    if check_integrity:
        dois = [r["doi_normalised"] for r in unique.values() if r["doi_normalised"]]
        integrity = integrity_check(dois, email=email)
    queries = queries or {"(replay)": "queries as executed on the payload date"}
    manifest = {"mode": "replay", "payloads": os.path.basename(payload_path),
                "date": datetime.date.today().isoformat()}
    note = coverage_note(question, queries, stats, integrity, sorted(per_set), unavailable)
    outdir = outdir or os.path.join(REPO_ROOT, "runs", "replay-" +
                                    os.path.basename(payload_path).replace(".json", ""))
    return write_run(outdir, question, queries, unique, stats, integrity, note, manifest), stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--replay", metavar="PAYLOAD_JSON",
                    help="re-parse dated connector payloads from records/")
    ap.add_argument("--check-integrity", action="store_true",
                    help="run the spec 33 existence and retraction check (needs network)")
    ap.add_argument("--integrity", metavar="RUNDIR",
                    help="run the spec 33 check over a completed run and update its coverage note")
    ap.add_argument("--outdir")
    a = ap.parse_args()
    if a.integrity:
        integrity, tally = run_integrity(a.integrity)
        print(json.dumps(tally, indent=1))
        for d, v in integrity.items():
            if v["status"] in ("retracted", "unknown"):
                print(v["status"], d)
        sys.exit(0)
    if not a.replay:
        sys.exit("live retrieval needs the MCP-capable kernel: import this module and call "
                 "run_live(question, mcp, servers). Use --replay for the offline path.")
    out, stats = run_replay(a.replay, outdir=a.outdir, check_integrity=a.check_integrity)
    print(json.dumps(stats, indent=1))
    print("written to", out)
