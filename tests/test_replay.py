#!/usr/bin/env python3
"""Pin the Stage 0 parsers to the dated payloads in records/.

The connectors are not reproducible — corpora and default limits change without
notice — so the payloads are the fixture and these numbers are the contract. A
failure here means a parser changed behaviour, not that the literature moved.

Run: python tests/test_replay.py     (stdlib only, no network)
"""
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAYLOADS = os.path.join(ROOT, "records", "stage0-retrieval-raw-2026-09-04.json")

# Measured 2026-09-04 on: "Does pre-registration of studies predict higher
# replication rates?" with the disconfirming set of spec 16, at each channel's
# default limit.
EXPECTED = {"records_returned": 107, "unique_sources": 93, "with_doi": 78,
            "multi_channel": 2}
EXPECTED_PER_QUERY_SET = {"fasttrack/sup": 20, "fasttrack/dis": 18,
                    "scholargw/sup": 15, "scholargw/dis": 14,
                    "scispace/sup": 10, "scispace/dis": 10,
                    "consensus/sup": 10, "consensus/dis": 10}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    r = load(os.path.join(ROOT, "stage0", "retrieve.py"), "retrieve")
    raw = json.load(open(PAYLOADS))
    per_set = {k: r.CHANNELS[k.partition("/")[0]][2](v) for k, v in raw.items()
               if k.partition("/")[0] in r.CHANNELS}
    unique, stats = r.collate(per_set)

    failures = []
    for k, want in EXPECTED.items():
        if stats[k] != want:
            failures.append(f"{k}: expected {want}, got {stats[k]}")
    if stats["per_channel_query_set"] != EXPECTED_PER_QUERY_SET:
        failures.append(f"per-channel yield changed: {stats['per_channel_query_set']}")

    # A source merged by title from a channel that returns no DOIs must still
    # carry its DOI, or it silently escapes the spec 33 integrity check.
    merged = [s for s in unique.values()
              if s["doi_normalised"] == "10.31222/osf.io/fhdbs"]
    if not merged:
        failures.append("title-merged OSF preprint lost its DOI")
    elif "consensus" not in merged[0]["channels"]:
        failures.append("title-merge across channels did not happen")

    # Every access tag must be one of the three spec 18 values.
    allowed = {"full text", "extracted fields", "abstract only"}
    bad = set(stats["access_mix"]) - allowed
    if bad:
        failures.append(f"access tags outside spec 18: {bad}")

    for f in failures:
        print("FAIL:", f)
    if failures:
        return 1
    print(f"ok — {stats['records_returned']} records, {stats['unique_sources']} unique, "
          f"{stats['with_doi']} with DOI, {stats['multi_channel']} multi-channel; "
          f"access mix {stats['access_mix']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
