"""DOI extraction, normalisation, validation, and cross-channel deduplication.

Stdlib + Crossref only. Loaded by the doi-source-identity skill.
"""
import re
import json
import time
import unicodedata
import urllib.parse
import urllib.request

DOI_PATTERN = r"10\.\d{4,9}/\S+"
PREFIX_PATTERN = r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*|DOI:\s*)"
TRAILING_PUNCT = ".,;:'\"\u201d\u2019!?"
CROSSREF_PACE = {"last": 0.0, "interval": 0.25}
DATACITE_PACE = {"last": 0.0, "interval": 0.2}


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


def crossref_record(doi, email=None, timeout=30, attempts=3):
    """Full Crossref message for a DOI, or None if it could not be fetched.

    Paced and identified: Crossref advertises a 5 requests/second limit via
    x-rate-limit-limit, so calls are spaced and 429/503 is retried honouring
    Retry-After. A contact address, where available, goes in both the User-Agent
    and mailto as the service asks.

    Note on where this runs: api.crossref.org is not reachable from every
    kernel. If every lookup returns None, check reachability before concluding
    anything about the DOIs -- an unreachable host and an absent record must not
    look the same.
    """
    d = normalize_doi(doi)
    if not d:
        return None
    u = "https://api.crossref.org/works/" + urllib.parse.quote(d)
    if email:
        u += "?mailto=" + urllib.parse.quote(email)
    ua = "doi-source-identity/0.1"
    if email:
        ua += " (mailto:" + email + ")"
    for attempt in range(attempts):
        gap = CROSSREF_PACE["interval"] - (time.time() - CROSSREF_PACE["last"])
        if gap > 0:
            time.sleep(gap)
        CROSSREF_PACE["last"] = time.time()
        try:
            req = urllib.request.Request(u, headers={"Accept": "application/json",
                                                     "User-Agent": ua})
            with urllib.request.urlopen(req, timeout=timeout) as fh:
                return json.load(fh)["message"]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503) and attempt < attempts - 1:
                wait = e.headers.get("retry-after")
                time.sleep(float(wait) if wait and str(wait).isdigit() else 2 ** attempt)
                continue
            return None
        except Exception:
            if attempt < attempts - 1:
                time.sleep(2 ** attempt)
                continue
            return None
    return None


def crossref_status(doi, email=None, timeout=30, attempts=3):
    """('found', message) | ('not_in_crossref', None) | ('error', reason).

    Distinguishing these three matters: a DOI registered with another agency
    (DataCite covers arXiv, Zenodo, PsychArchives and most repository DOIs) is a
    perfectly valid DOI that Crossref simply does not hold. Collapsing it into
    the same bucket as a failed lookup makes a permanent flag out of a
    registration detail.
    """
    d = normalize_doi(doi)
    if not d:
        return ("error", "not a DOI")
    u = "https://api.crossref.org/works/" + urllib.parse.quote(d)
    if email:
        u += "?mailto=" + urllib.parse.quote(email)
    ua = "doi-source-identity/0.1" + (" (mailto:" + email + ")" if email else "")
    for attempt in range(attempts):
        gap = CROSSREF_PACE["interval"] - (time.time() - CROSSREF_PACE["last"])
        if gap > 0:
            time.sleep(gap)
        CROSSREF_PACE["last"] = time.time()
        try:
            req = urllib.request.Request(u, headers={"Accept": "application/json",
                                                     "User-Agent": ua})
            with urllib.request.urlopen(req, timeout=timeout) as fh:
                return ("found", json.load(fh)["message"])
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_in_crossref", None)
            if e.code in (429, 500, 502, 503) and attempt < attempts - 1:
                wait = e.headers.get("retry-after")
                time.sleep(float(wait) if wait and str(wait).isdigit() else 2 ** attempt)
                continue
            return ("error", "HTTP " + str(e.code))
        except Exception as e:
            if attempt < attempts - 1:
                time.sleep(2 ** attempt)
                continue
            return ("error", type(e).__name__)
    return ("error", "exhausted attempts")


def datacite_record(doi, timeout=30, attempts=3):
    """Normalised DataCite record for a DOI, or None.

    DataCite is the registration agency for arXiv, Zenodo, PsychArchives and most
    repository DOIs — the ones Crossref returns 404 for. Creators and publication
    year are returned because same-work linkage needs an author or year guard on
    a title match; without them a title collision has nothing holding it back.

    Returns {exists, state, type, version, title, creators, year, relations} where
    relations is [(relationType, relatedIdentifier), ...].
    """
    d = normalize_doi(doi)
    if not d:
        return None
    u = "https://api.datacite.org/dois/" + urllib.parse.quote(d)
    for attempt in range(attempts):
        gap = DATACITE_PACE["interval"] - (time.time() - DATACITE_PACE["last"])
        if gap > 0:
            time.sleep(gap)
        DATACITE_PACE["last"] = time.time()
        try:
            req = urllib.request.Request(u, headers={"Accept": "application/json",
                                                     "User-Agent": "doi-source-identity/0.1"})
            with urllib.request.urlopen(req, timeout=timeout) as fh:
                a = json.load(fh)["data"]["attributes"]
            fams = []
            for c in (a.get("creators") or []):
                fam = c.get("familyName")
                if not fam and c.get("name"):
                    fam = str(c["name"]).split(",")[0].strip()
                if fam:
                    fams.append(fam)
            return {"exists": True, "state": a.get("state"),
                    "type": (a.get("types") or {}).get("resourceTypeGeneral"),
                    "version": a.get("version"),
                    "title": (a.get("titles") or [{}])[0].get("title"),
                    "creators": fams, "year": a.get("publicationYear"),
                    "relations": [(r.get("relationType"), r.get("relatedIdentifier"))
                                  for r in (a.get("relatedIdentifiers") or [])]}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"exists": False}
            if e.code in (429, 500, 502, 503) and attempt < attempts - 1:
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            if attempt < attempts - 1:
                time.sleep(2 ** attempt)
                continue
            return None
    return None


def retraction_status(doi, email=None):
    """Retraction and correction notices from the Crossref 'updated-by' array.

    {'retracted': bool, 'corrected': bool, 'notices': [...]}, or None when the
    record could not be fetched -- unknown is not the same as clean.
    """
    state, m = crossref_status(doi, email=email)
    if state != "found":
        return None if state == "error" else {"retracted": False, "corrected": False,
                                              "notices": [], "registry": "not_in_crossref"}
    notices = [{"type": u.get("type"), "source": u.get("source"), "doi": u.get("DOI")}
               for u in (m.get("updated-by") or [])]
    return {"retracted": any(n["type"] == "retraction" for n in notices),
            "corrected": any(n["type"] == "correction" for n in notices),
            "notices": notices, "registry": "crossref"}
