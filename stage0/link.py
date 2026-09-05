#!/usr/bin/env python3
"""Source identity: stable record ids, canonical metadata, same-work linkage.

Retrieval identifies sources by DOI, but a DOI names a *publication artifact*,
not a *work*. One study can hold a preprint DOI, a repository-copy DOI, another
preprint-server DOI and a journal DOI; distinct DOIs never collide, so
DOI-keyed deduplication leaves them as four independent-looking sources.

What that costs, concretely:

  spec 27 / X-3  independence is a property of the underlying study. A test that
                 reads "different identifier" as "different source" counts four
                 copies of one paper as four sources. The error is
                 one-directional — duplicates only ever add.
  spec 24 / X-2  the claim tier is the MAXIMUM per-source tier, and an
                 abstract-only source cannot be downgraded. Copies of one study
                 retrieved by different routes carry different access levels, so
                 duplication multiplies the chance that one leniently-scored
                 copy sets the tier.
  spec 31        the adversarial pass checks for "the same weakness downgraded
                 twice" and cannot see that copies are one study.
  spec 17 / 47   yields and saturation are counted on records, so a channel that
                 starts returning preprint copies looks like it found more.

Design choices, and why:

  Records are never merged. Each carries its own access level and retrieval
  route, which spec 24 depends on. Linkage attaches a `work_id`; counting then
  happens at whichever level the question is about — records for retrieval,
  works for independence.

  Ids are derived, not random. A content hash re-derives identically on replay,
  so runs can be diffed and payloads re-linked after the rules change. Linkage
  rules always change.

  A title match alone never links. "Corrigendum", "Reply to …" and conference
  front matter collide constantly, and distinct works do share titles. A title
  match must be seconded by the first-author surname or a close year. Where
  neither registry supplies authors, the link is still made but recorded as
  `unguarded` so it is auditable rather than invisible.

  Relations are filtered by type. Registries return `is-referenced-by` and
  `has-review` alongside identity relations; only version/identity types say
  anything about being the same work.

Not covered, and it matters: work identity is narrower than independence. Two
genuinely different papers from one lab on one cohort share data and authors and
are not independent. No title-or-DOI linkage detects that; the spec 27 test also
needs author-overlap and dataset-identifier comparison.

Usage:
    python stage0/link.py --link runs/<run-dir>          # enrich, link, report
    python stage0/link.py --link runs/<run-dir> --no-net # link on retrieved data only
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
from collections import defaultdict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_KERNEL = os.path.join(REPO_ROOT, "skills", "doi-source-identity", "kernel.py")

# Only these say "same work". Registries return plenty of relations that do not.
VERSION_RELATIONS = {
    # Crossref
    "has-preprint", "is-preprint-of", "is-version-of", "has-version",
    "is-identical-to", "is-same-as", "is-translation-of", "has-translation",
    # DataCite
    "IsVersionOf", "HasVersion", "IsPreviousVersionOf", "IsNewVersionOf",
    "IsIdenticalTo", "IsVariantFormOf", "IsOriginalFormOf", "IsTranslationOf",
}
YEAR_WINDOW = 2


def surname(name):
    """Comparable surname from either registry's format.

    Crossref supplies a parsed `family` ("Johnson"); DataCite often supplies only
    a display name ("Valen E. Johnson"). Comparing the raw strings makes those
    unequal, which silently REJECTS genuine same-work pairs — the guard then
    looks like it is discriminating when it is failing. Compare last tokens.
    """
    if not name:
        return None
    toks = [t for t in "".join(c if (c.isalpha() or c.isspace() or c == "-") else " "
                              for c in str(name).lower()).split() if t]
    return toks[-1] if toks else None


def strip_doi_version(doi):
    """figshare and Zenodo mint per-version DOIs as <base>.v1, <base>.v2 …

    Same base, same work. This is deterministic and needs no metadata, so it
    runs before any title or author reasoning.
    """
    return re.sub(r"\.v\d+$", "", doi or "")


def identity():
    spec = importlib.util.spec_from_file_location("doi_source_identity", SKILL_KERNEL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def record_id(rec, D):
    """Stable surrogate key: same inputs, same id, on any replay."""
    basis = "|".join([
        ",".join(rec.get("channels") or []),
        (D.normalize_doi(rec.get("doi_normalised") or rec.get("doi")) or ""),
        D.normalize_title(rec.get("title")) or "",
    ])
    return "rec_" + hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]


def work_id(members):
    """Derived from the member set, so it is stable but changes when the
    cluster does — a changed work_id is a signal, not noise."""
    return "wrk_" + hashlib.sha1("|".join(sorted(members)).encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------- enrichment
def enrich(sources, D, email=None, net=True):
    """Canonical title, first author, year and relations per DOI.

    This is also what rescues records whose channel returned no title at all:
    a DOI lookup supplies one, so they become linkable instead of invisible.
    """
    meta, counts = {}, {"crossref": 0, "datacite": 0, "absent": 0, "error": 0, "skipped": 0}
    for s in sources:
        d = s.get("doi_normalised") or D.normalize_doi(s.get("doi"))
        if not d or d in meta:
            continue
        if not net:
            counts["skipped"] += 1
            continue
        state, m = D.crossref_status(d, email=email)
        if state == "found":
            fams = [a.get("family", "") for a in (m.get("author") or []) if a.get("family")]
            rels = [(k, (v or {}).get("id"))
                    for k, vs in (m.get("relation") or {}).items()
                    for v in (vs if isinstance(vs, list) else [vs])]
            meta[d] = {"title": D.normalize_title((m.get("title") or [""])[0]),
                       "first": fams[0].lower() if fams else None,
                       "authors": [f.lower() for f in fams],
                       "year": ((m.get("issued", {}).get("date-parts") or [[None]])[0] or [None])[0],
                       "relations": rels, "registry": "crossref"}
            counts["crossref"] += 1
        elif state == "not_in_crossref":
            dc = D.datacite_record(d)
            if dc and dc.get("exists"):
                fams = [f.lower() for f in (dc.get("creators") or [])]
                meta[d] = {"title": D.normalize_title(dc.get("title")),
                           "first": fams[0] if fams else None, "authors": fams,
                           "year": dc.get("year"), "relations": dc.get("relations") or [],
                           "registry": "datacite"}
                counts["datacite"] += 1
            else:
                meta[d] = {"title": None, "first": None, "authors": [], "year": None,
                           "relations": [], "registry": "absent" if dc else "error"}
                counts["absent" if dc else "error"] += 1
        else:
            meta[d] = {"title": None, "first": None, "authors": [], "year": None,
                       "relations": [], "registry": "error"}
            counts["error"] += 1
    return meta, counts


# ------------------------------------------------------------------ linkage
def link(sources, meta, D):
    """Union-find over version relations and guarded title matches."""
    for s in sources:
        s["record_id"] = record_id(s, D)
        d = s.get("doi_normalised")
        m = meta.get(d) if d else None
        # canonical title where the channel gave none — the reason enrichment exists
        s["title_canonical"] = (m or {}).get("title") or D.normalize_title(s.get("title")) or None

    keys = {s["record_id"]: s for s in sources}
    parent = {k: k for k in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    doi_to_rec = defaultdict(list)
    for s in sources:
        if s.get("doi_normalised"):
            doi_to_rec[s["doi_normalised"]].append(s["record_id"])

    evidence = {"relation": [], "title_guarded": [], "title_unguarded": [],
                "doi_version": [], "rejected": []}

    # 1. same DOI across channels (retrieval may already have merged these)
    for d, recs in doi_to_rec.items():
        for r in recs[1:]:
            union(recs[0], r)

    # 2. per-version DOIs of one deposit: <base>, <base>.v1, <base>.v3
    by_base = defaultdict(list)
    for d in doi_to_rec:
        by_base[strip_doi_version(d)].append(d)
    for base, ds in by_base.items():
        if len(ds) > 1:
            for other in sorted(ds)[1:]:
                union(doi_to_rec[sorted(ds)[0]][0], doi_to_rec[other][0])
                evidence["doi_version"].append({"base": base, "a": sorted(ds)[0], "b": other})

    # 2. version/identity relations, where both ends are in this run
    for d, m in meta.items():
        for rtype, rid in m.get("relations") or []:
            if rtype not in VERSION_RELATIONS or not rid:
                continue
            other = D.normalize_doi(rid)
            if other and other in doi_to_rec and other != d:
                union(doi_to_rec[d][0], doi_to_rec[other][0])
                evidence["relation"].append({"a": d, "b": other, "type": rtype})

    # 3. identical canonical title, seconded by author or year
    by_title = defaultdict(list)
    for s in sources:
        if s.get("title_canonical"):
            by_title[s["title_canonical"]].append(s)
    for title, group in by_title.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                ma = meta.get(a.get("doi_normalised")) or {}
                mb = meta.get(b.get("doi_normalised")) or {}
                sa, sb = surname(ma.get("first")), surname(mb.get("first"))
                shared_any = ({surname(x) for x in (ma.get("authors") or [])} &
                              {surname(x) for x in (mb.get("authors") or [])}) - {None}
                same_author = bool((sa and sb and sa == sb) or shared_any)
                close_year = (ma.get("year") and mb.get("year")
                              and abs(ma["year"] - mb["year"]) <= YEAR_WINDOW)
                no_guard_available = not (ma.get("first") and mb.get("first")) and \
                                     not (ma.get("year") and mb.get("year"))
                pair = {"a": a["record_id"], "b": b["record_id"], "title": title[:80],
                        "a_doi": a.get("doi_normalised"), "b_doi": b.get("doi_normalised")}
                if same_author or close_year:
                    union(a["record_id"], b["record_id"])
                    evidence["title_guarded"].append(
                        dict(pair, guard="author" if same_author else "year"))
                elif no_guard_available:
                    union(a["record_id"], b["record_id"])
                    evidence["title_unguarded"].append(pair)
                else:
                    evidence["rejected"].append(
                        dict(pair, a_first=ma.get("first"), b_first=mb.get("first"),
                             a_year=ma.get("year"), b_year=mb.get("year")))

    groups = defaultdict(list)
    for k in keys:
        groups[find(k)].append(k)
    works = {}
    for members in groups.values():
        wid = work_id(members)
        for rid in members:
            keys[rid]["work_id"] = wid
        dois = sorted({keys[r]["doi_normalised"] for r in members if keys[r].get("doi_normalised")})
        works[wid] = {"work_id": wid, "records": sorted(members), "dois": dois,
                      "title": keys[members[0]].get("title_canonical"),
                      "access_levels": sorted({keys[r].get("access") for r in members
                                               if keys[r].get("access")}),
                      "channels": sorted({c for r in members for c in (keys[r].get("channels") or [])})}
    return sources, works, evidence


def query_set_overlap_works(rundir, works, D):
    """Cross-query-set overlap counted in WORKS, not records (spec 16).

    The record-level figure computed during retrieval is inflated wherever a
    channel returns several copies of one work: in one measured run SciSpace
    showed 5 shared records at Jaccard 0.333, but four of those five were the
    same study under arXiv, Authorea, repository and journal DOIs — 2 shared
    works at 0.286. The record figure is what is computable before linkage; this
    is the one to read.

    Needs the run's payloads.json, so it is skipped for runs written before
    payloads were persisted rather than silently reported as zero.
    """
    path = os.path.join(rundir, "payloads.json")
    if not os.path.exists(path):
        return {"unavailable": "no payloads.json in this run; cannot recount by work"}
    spec = importlib.util.spec_from_file_location(
        "retrieve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "retrieve.py"))
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    with open(path) as fh:
        raw = json.load(fh)

    doi2work, title2work = {}, {}
    for wid, v in works.items():
        for d in v["dois"]:
            doi2work[d] = wid
        if v.get("title"):
            title2work[v["title"]] = wid

    def works_of(recs):
        out = set()
        for r in recs:
            d = D.normalize_doi(r.get("doi"))
            t = D.normalize_title(r.get("title"))
            wid = (doi2work.get(d) if d else None) or (title2work.get(t) if t else None)
            out.add(wid or ("unmatched:" + (d or t or "")))
        return out - {"unmatched:"}

    parsed = {}
    for key, payload in raw.items():
        ch = key.partition("/")[0]
        if ch in R.CHANNELS and "__error__" not in str(payload)[:40]:
            parsed[key] = R.CHANNELS[ch][2](payload)

    out = {}
    for ch in {k.partition("/")[0] for k in parsed}:
        sets = {k.partition("/")[2]: v for k, v in parsed.items() if k.partition("/")[0] == ch}
        if len(sets) < 2:
            continue
        (_, ra), (_, rb) = sorted(sets.items())[:2]
        wa, wb = works_of(ra), works_of(rb)
        union = wa | wb
        shared = sorted(wa & wb)
        out[ch] = {"shared": len(shared),
                   "jaccard": round(len(shared) / len(union), 3) if union else None,
                   "shared_works": [{"work_id": s,
                                     "title": (works.get(s) or {}).get("title"),
                                     "dois": (works.get(s) or {}).get("dois", [])}
                                    for s in shared]}
    return out


def summarise(sources, works, evidence, enrich_counts, mode="network"):
    """`mode` is recorded because offline linkage is strictly weaker, not merely
    faster: without registry enrichment there are no canonical titles, no authors
    and no relations, so links that exist are not found. An offline result
    overwriting a networked one in a run directory, with nothing saying so, is
    exactly the silent degradation spec 57 forbids."""
    multi = {w: v for w, v in works.items() if len(v["records"]) > 1}
    unlinkable = [s["record_id"] for s in sources
                  if not s.get("doi_normalised") and not s.get("title_canonical")]
    return {
        "enrichment_mode": mode,
        "records": len(sources),
        "works": len(works),
        "redundant_records": len(sources) - len(works),
        "clusters": len(multi),
        "largest_cluster": max((len(v["records"]) for v in works.values()), default=0),
        "links_by_relation": len(evidence["relation"]),
        "links_by_title_guarded": len(evidence["title_guarded"]),
        "links_by_title_unguarded": len(evidence["title_unguarded"]),
        "title_collisions_rejected": len(evidence["rejected"]),
        "records_no_doi": sum(1 for s in sources if not s.get("doi_normalised")),
        "records_unlinkable": len(unlinkable),
        "enrichment": enrich_counts,
        "works_with_mixed_access": sum(1 for v in works.values() if len(v["access_levels"]) > 1),
    }


def run_link(rundir, email=None, net=True):
    D = identity()
    with open(os.path.join(rundir, "sources.json")) as fh:
        sources = json.load(fh)
    meta, counts = enrich(sources, D, email=email, net=net)
    sources, works, evidence = link(sources, meta, D)
    stats = summarise(sources, works, evidence, counts, mode="network" if net else "offline")
    stats["query_set_overlap_works"] = query_set_overlap_works(rundir, works, D)

    with open(os.path.join(rundir, "sources.json"), "w") as fh:
        json.dump(sources, fh, indent=1)
    with open(os.path.join(rundir, "works.json"), "w") as fh:
        json.dump({"works": works, "link_evidence": evidence, "stats": stats}, fh, indent=1)
    cov_path = os.path.join(rundir, "coverage.json")
    with open(cov_path) as fh:
        cov = json.load(fh)
    cov["linkage"] = stats
    with open(cov_path, "w") as fh:
        json.dump(cov, fh, indent=1)

    # regenerate the coverage note so the reported counts include works, not
    # records alone (spec 47)
    spec = importlib.util.spec_from_file_location(
        "retrieve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "retrieve.py"))
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    note = R.coverage_note(cov["question"], cov["queries"], cov["stats"],
                           cov.get("integrity") or {},
                           # data files outlive code renames: runs written before
                           # "arm" became "query set" carry the old key
                           sorted(cov["stats"].get("per_channel_query_set")
                                  or cov["stats"].get("per_channel_arm") or {}),
                           {}, linkage=stats)
    with open(os.path.join(rundir, "coverage-note.md"), "w") as fh:
        fh.write(note)
    return stats, works, evidence


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--link", metavar="RUNDIR", required=True)
    ap.add_argument("--no-net", action="store_true",
                    help="skip registry enrichment; link on retrieved fields only")
    a = ap.parse_args()
    stats, works, evidence = run_link(a.link, net=not a.no_net)
    print(json.dumps(stats, indent=1))
    for w in works.values():
        if len(w["records"]) > 1:
            print(f"\n{w['work_id']}  {(w['title'] or '')[:60]}")
            for d in w["dois"] or ["(no doi)"]:
                print("   ", d)
            if len(w["access_levels"]) > 1:
                print("    mixed access levels:", w["access_levels"], "<- spec 24 / X-2 exposure")
    if evidence["title_unguarded"]:
        print("\nunguarded title links (no author or year available on either side):")
        for p in evidence["title_unguarded"]:
            print("   ", p["a_doi"], "<->", p["b_doi"])
    if evidence["rejected"]:
        print("\ntitle collisions rejected by the guard:")
        for p in evidence["rejected"]:
            print("   ", p["a_doi"], "vs", p["b_doi"], "|", p["title"][:50])
    sys.exit(0)
