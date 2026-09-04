"""DOI extraction, normalisation, validation, and cross-channel deduplication.

Stdlib + Crossref only. Loaded by the doi-source-identity skill.
"""
import re
import json
import unicodedata
import urllib.parse
import urllib.request

DOI_PATTERN = r"10\.\d{4,9}/\S+"
PREFIX_PATTERN = r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*|DOI:\s*)"
TRAILING_PUNCT = ".,;:'\"\u201d\u2019!?"


def normalize_doi(s):
    """Canonical lowercase DOI from a string, URL, doi: prefix, or sentence.

    Captures broadly then trims: DOI suffixes legitimately contain ( ) < > : ;
    [ ], so a restrictive character class truncates parenthesised Elsevier and
    SICI-style Wiley DOIs. Closing brackets are stripped only when unbalanced.
    """
    if not s:
        return None
    s = re.sub(PREFIX_PATTERN, "", str(s).strip(), flags=re.I).strip()
    m = re.search(DOI_PATTERN, s, re.I)
    if not m:
        return None
    d = m.group(0)
    while d:
        if d[-1] in TRAILING_PUNCT:
            d = d[:-1]
        elif d[-1] == ")" and d.count(")") > d.count("("):
            d = d[:-1]
        elif d[-1] == "]" and d.count("]") > d.count("["):
            d = d[:-1]
        elif d[-1] == ">" and d.count(">") > d.count("<"):
            d = d[:-1]
        else:
            break
    return d.lower() or None


def extract_dois(text):
    """Every distinct DOI in free text, normalised, order preserved."""
    out = []
    seen = set()
    for raw in re.findall(DOI_PATTERN, text or "", re.I):
        d = normalize_doi(raw)
        if d and d not in seen:
            seen.add(d)
            out.append(d)
    return out


def doi_exists(doi, email=None, timeout=25):
    """True / False / None. None means the check failed, NOT that the DOI is absent."""
    d = normalize_doi(doi)
    if not d:
        return False
    u = "https://api.crossref.org/works/" + urllib.parse.quote(d)
    if email:
        u += "?mailto=" + urllib.parse.quote(email)
    try:
        req = urllib.request.Request(u, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as fh:
            return fh.status == 200
    except urllib.error.HTTPError as e:
        return False if e.code == 404 else None
    except Exception:
        return None


def normalize_title(t):
    """Accent- and punctuation-stripped title, for use as a fallback identity."""
    t = unicodedata.normalize("NFKD", (t or "").lower())
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def dedupe_sources(records, doi_key="doi", title_key="title"):
    """Collapse retrieval records to unique sources across channels.

    DOI-first with a normalised-title fallback: a record lacking a DOI merges
    into a DOI-bearing record sharing its title. Keying on DOI alone reports
    false zero cross-channel overlap when a channel returns titles only.

    Returns (unique, index): canonical key -> first record seen, and
    canonical key -> set of channel labels (from an optional 'channel' field).
    """
    recs = list(records)
    title_to_doi = {}
    for r in recs:
        d = normalize_doi(r.get(doi_key))
        t = normalize_title(r.get(title_key))
        if d and t:
            title_to_doi.setdefault(t, d)
    unique = {}
    index = {}
    for r in recs:
        d = normalize_doi(r.get(doi_key))
        t = normalize_title(r.get(title_key))
        key = d or title_to_doi.get(t) or ("title:" + t if t else None)
        if not key:
            continue
        unique.setdefault(key, r)
        index.setdefault(key, set()).add(r.get("channel", "?"))
    return unique, index


def crossref_record(doi, email=None, timeout=30):
    """Full Crossref message for a DOI, or None if it could not be fetched."""
    d = normalize_doi(doi)
    if not d:
        return None
    u = "https://api.crossref.org/works/" + urllib.parse.quote(d)
    if email:
        u += "?mailto=" + urllib.parse.quote(email)
    try:
        with urllib.request.urlopen(u, timeout=timeout) as fh:
            return json.load(fh)["message"]
    except Exception:
        return None


def retraction_status(doi, email=None):
    """Retraction and correction notices from the Crossref 'updated-by' array.

    {'retracted': bool, 'corrected': bool, 'notices': [...]}, or None when the
    record could not be fetched -- unknown is not the same as clean.
    """
    m = crossref_record(doi, email=email)
    if m is None:
        return None
    notices = [{"type": u.get("type"), "source": u.get("source"), "doi": u.get("DOI")}
               for u in (m.get("updated-by") or [])]
    return {"retracted": any(n["type"] == "retraction" for n in notices),
            "corrected": any(n["type"] == "correction" for n in notices),
            "notices": notices}
