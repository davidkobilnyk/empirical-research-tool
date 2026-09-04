# Scholarly source coverage — gaps against the spec

**Version:** v0.4, September 4, 2026. v0.4 corrects the granted-domain count, replaces the stale spec 18 amendment in section 6 (which still said OSF preprints were unretrievable, contradicting G3), and records the handbook fetches in section 3b. v0.2 corrected two untested Scite claims (section 3b). v0.3 records the outcome of the access requests: fourteen domains granted and tested, four gaps closed outright, two sources unavailable for reasons no grant can fix.
**Question addressed:** what scholarly sources the retrieval layer still needs, beyond the connectors now attached
**Bearing on:** specs 15–18 (retrieval), 24 (extracted fields), 33 (citation audit), 35 and 51 (validation set), 47 (coverage note), 53 (known limits)

**Short answer.** You do not need another paper index. Five of the attached connectors search overlapping corpora built on the same three or four upstream sources, and a sixth returns passages from them. Every gap identified here is a source that is *not* a paper index: replication-outcome databases, study registries, post-publication commentary, code and data deposits, and handbooks.

**State as of v0.3.** Retraction status turned out to need no new access at all (section 3). Of the rest, four gaps are now closed by granted and tested access — OSF content and datasets (G3), study registries for OSF-registered work (G2), code and data deposits (G5), and the two named handbooks (G6) — leaving the replication-outcome *assembly* work (G1), which spec 35 assigns to you rather than to the model. Two things stay unavailable for reasons no grant fixes: PubPeer, whose origin refuses automated clients, and book-length literature, which no index here carries. One earlier claim about Scite's citing-stance coverage was withdrawn after testing (section 3b), which makes spec 16's disconfirmation channel thinner than v0.1 implied.

---

## 1. What the attached connectors already cover

| Function the spec needs | Connectors that supply it | Redundancy |
|---|---|---|
| Paper discovery by question | FastTrack, Consensus, SciSpace, Scholar Gateway, alphaXiv, and the platform literature server (OpenAlex, arXiv) | Five-deep. All draw on OpenAlex, Semantic Scholar, PubMed, Scopus metadata, or arXiv |
| Retrieved *passages* rather than records | Scholar Gateway only | None |
| Full text | Scite `read_fulltext` (verified, any DOI, with an explicit access flag), alphaXiv (arXiv), PubMed server (PMC), Europe PMC (verified, OA and in-EPMC articles) | Four, complementary rather than redundant |
| Citation topology and citing-paper stance | Scite `citation_graph` with `include_intent` | None — and stance labels are sparse; see section 3b |
| Citation chaining and co-citation (spec 17) | FastTrack (`recommend_similar`, `map_topic_debate`), platform literature server (OpenAlex citations) | Two |
| Saturation evidence (spec 17) | FastTrack (`check_gap_saturation`) | None, and unassessed |
| Structured logging (spec 45) | Airtable | Not applicable |

The redundancy is not waste — spec 15 requires a reported search strategy, and running parallel query sets across two or three indexes is how you evidence coverage. But adding a sixth index buys nothing that spec 47's coverage note can claim.

---

## 2. Reachability, tested rather than assumed

Two columns: what the first probe found before any access request, and the status now that the requests in section 5 have been granted and exercised. Blocked entries were allowlist decisions, not outages — which is why most of them moved.

| Source | First probe | Now | What it serves |
|---|---|---|---|
| Crossref main API | reachable | reachable | Retraction and correction relations, DOI metadata, reference lists |
| bioRxiv / medRxiv API | reachable | reachable | Preprint metadata, spec 18 |
| GitHub raw | reachable | reachable | Code availability for simulation sources (S-D7) |
| Europe PMC | blocked | **works** | Records, and full text for the OA and in-EPMC subset (spec 18) |
| OSF API and file hosts | blocked | **works** | Preprints (PsyArXiv, MetaArXiv), registrations, dataset downloads |
| Zenodo | blocked | **works** | Code and data deposits with DOIs |
| Crossref Labs (Retraction Watch bulk) | blocked | **works** | Bulk retraction dataset, 72,389 rows |
| Cochrane Handbook, GRADE Handbook | blocked | **works** | Spec 11 orientation reading |
| PROSPERO | blocked | HTML only | Review-protocol registry; JSON endpoint rejects requests, so manual |
| PhilPapers | blocked | OAI only | Philosophy of science and statistics, spec 2 scope |
| PubPeer | blocked | **unavailable** | Named in spec 16; origin refuses automated clients regardless of grant |
| Semantic Scholar direct | rate-limited | rate-limited | Redundant with three connectors that wrap it |

---

## 3. Solved with access you already have: retraction status

Crossref's main API carries Retraction Watch data inline. For a retracted paper the record returns an `updated-by` array whose entries name the type, the source, and the retraction notice DOI:

```
10.1038/s41562-023-01749-9  ->  updated-by: [
    {type: "retraction", source: "retraction-watch", DOI: "10.1038/s41562-024-01997-3"},
    {type: "retraction", source: "publisher",        DOI: "10.1038/s41562-024-01997-3"} ]
```

Tested for false positives on three non-retracted papers: two return no `updated-by` at all, and the third returns `type: "correction"` for its corrigendum rather than a retraction. The field therefore discriminates retraction from correction without judgement.

**Consequences.** (a) The retraction half of spec 16's targeted disconfirmation check is a per-DOI Crossref lookup, needing no connector and no new domain. (b) It belongs in the spec 33 citation audit as a gate, not only in the disconfirmation channel: every cited source can be checked for retraction at audit time, cheaply. (c) The same call detects corrections and errata, which spec 24 does not currently ask for but which bear on whether a reported effect size is the current one. (d) Bulk access to the whole Retraction Watch dataset still needs the blocked Labs domain; per-DOI checks do not.

---

## 3b. What the granted access and the connectors actually deliver, tested

Every row below was exercised against a real record, not read off documentation. Two claims in v0.1 were asserted without this check and are corrected here.

| Capability | Verified result | Serves |
|---|---|---|
| **Scite `read_fulltext`** | Verbatim body text, 85,683 characters, for Morris et al. 2019 (`source: "fulltext"`, `contentDenied: false`). For IntHout et al. 2016 it returned `source: "abstract"`, `contentDenied: true`, with an access-restricted message | Specs 18 and 24. This is the strongest available route to the **full text checked** versus **not observable** distinction, because the flag is machine-readable rather than inferred. It was under-credited in v0.1 |
| **Scite `citation_graph`** with `include_intent` | 40 citing edges into Carter et al. 2019 resolved. Intent labels: 26 *mentioning*, 1 *supporting*, 14 unlabeled, **0 *contrasting***. The paper's own preprint DOI returned in `low_coverage_seeds` with zero resolved edges | Spec 17 chaining works well. Spec 16 disconfirmation does **not** rest on this: stance labels covered roughly two-thirds of edges in this sample, skewed to *mentioning*, with no contrasting edge at all. v0.1 claimed this covered published critical commentary; that claim was not tested and is withdrawn |
| **Europe PMC full text** | `fullTextXML` for an OA in-EPMC article returned 134,954 characters with a populated `<body>`, 30 sections, 64 references | Spec 18, for the OA subset |
| **Europe PMC preprint coverage** | The OSF preprint 10.31222/osf.io/fhdbs *is* indexed (PPR942063) but with `isOpenAccess: N`, `inEPMC: N`, `hasPDF: N` — record only, no text | Confirms G3: discovery of OSF preprints is solved several times over; content is not, except through OSF itself |
| **OSF API** | Preprint record retrievable (`fhdbs_v1`); file metadata gives *Preregistration in Practice IN.pdf*, 387 KB; registrations endpoint paginates; node search finds FORRT | G1, G2, G3. Note the download link resolves to `osf.io`, a second host, now also granted |
| **Zenodo** | 286,060 records queryable with `resource_type.type:software`, each with a DOI | G5, the S-D7 code-availability check |
| **PhilPapers** | OAI-PMH `Identify` and `ListRecords` both return valid records; the JSON API is Cloudflare-blocked | G7, via OAI harvesting rather than the API |
| **Cochrane and GRADE handbooks** | Both fetched: `training.cochrane.org/handbook/current` and `gdt.gradepro.org/app/handbook/handbook.html` each returned HTTP 200 with an HTML body (re-checked after the access grants) | Spec 11 orientation reading, and the source of the handbooks' own wording for the GRADE-derived items |
| **PubPeer** | Domain granted, but the site returns Cloudflare Error 1010 on both endpoints tried: it blocks automated clients at the origin | **G4 stays open.** The block is the site's policy, not the allowlist, and the correct response is a manual browser check by you — not evading the check with a spoofed client |

---

## 4. The gaps that matter

Ordered by which build stage they block.

### G1. Replication-outcome databases — blocks Stage 2

Spec 35 requires 50 or more claims whose answer key is a documented outcome, and spec 51 asks which projects can fill how many. No attached connector indexes replication *outcomes*; they index papers about them. The distinction matters because an answer key needs the per-claim result, not the paper's abstract.

Candidate sources: the FORRT Replication Database (a curated, downloadable set of replication outcomes), ReplicationWiki (economics-weighted), Curate Science (status should be checked — it may be dormant), and the project-level datasets published alongside the Reproducibility Project: Psychology, Many Labs 1 through 5, the Social Sciences Replication Project, the Reproducibility Project: Cancer Biology, and ManyBabies. Most are deposited on OSF or GitHub.

**Access status: no longer blocked.** The OSF API and its full download chain are working (section 5b), and a title search there already returns FORRT's project. The refuted-claims share of the set has a second route: the bulk Retraction Watch dataset, 72,389 rows with reason codes and original-paper DOIs, is now fetchable in one request.

So this stops being an access gap and becomes assembly work — which, per spec 35, is yours: the model may surface candidate sources but must not draft the answer key. What the granted access buys is that your assembly is a download and a filter rather than a manual literature trawl. It remains the most consequential item on this list, because until the set exists, spec 9 cannot be reached and grading stays provisional indefinitely.

### G2. Registry lookup for pre-registration status — degrades E-D2 and E-U4

Spec 24 makes pre-registration status an extracted field and applies a silence rule to it. Right now that field can only be read off the paper's own text, which is precisely why the silence rule exists. A registry lookup would settle it directly, and would also let E-U4 check the adherence condition it currently asserts must be "observable".

Routes, updated: **OSF Registries works** — the `registrations` endpoint paginates and is the registry most methodology studies actually use, so this is the one that matters and it is now open. PROSPERO is reachable as HTML but its JSON endpoint rejects requests, so review protocols are a manual lookup. ClinicalTrials.gov is available as a connector but is rarely the relevant registry here. AsPredicted has no API at any access level — human-readable only, a structural limit no grant changes.

Net effect: E-D2 and E-U4 can be upgraded from "read the paper's own claim" to "check the registry" for OSF-registered work, which is the bulk of it. That is worth doing before the first Stage 1 run, since E-D2's own anchor is already under question.

### G3. OSF-hosted preprint content — spec 18

Much metascience lives on PsyArXiv and MetaArXiv, both OSF-hosted. Discovery already worked: SciSpace surfaced an OSF preprint (10.31222/osf.io/fhdbs) on the first query I ran.

**Closed.** Retrieval now works too, verified end to end on that same preprint — 387,370 bytes of PDF through the three-hop chain in section 5b. Europe PMC indexes the record but not its text (`isOpenAccess: N`, `inEPMC: N`), so OSF itself is the content route, and the three-hop rewrite is what makes it work.

This matters beyond convenience: under spec 24 an abstract-only source cannot trigger a downgrade, so while this was blocked the tool was systematically unable to grade the metascience preprint literature at full strength — a bias aimed squarely at the literature the tool is about. Two consequences for the retrieval procedure: OSF-hosted sources should now be tagged **full text**, not **abstract only**, and Stage 0 should confirm the chain still works rather than assuming it, since the final hop is a signed URL.

### G4. PubPeer, and the disconfirmation channel generally — spec 16

Named in the spec by name, and now confirmed unreachable programmatically: the domain is granted, but PubPeer's origin blocks automated clients (Cloudflare 1010). It stays a manual check.

The larger point, corrected from v0.1: spec 16's disconfirmation channel is **less covered than I first wrote**, not more. Retraction and correction status is solved (section 3). Published critical commentary is *partly* reachable through Scite's citation intent, but the measured labels were sparse and skewed — 1 supporting, 26 mentioning, 14 unlabeled and no contrasting edge across 40 citing papers — so a claim's critics cannot be found by filtering for `contrasting` and calling the channel covered. Until the intent coverage is characterised on a larger sample, the practical route to disconfirmation is a parallel query set worded for the opposite conclusion (spec 16's own "balanced channels" requirement), with citation intent used as a lead generator rather than a filter.

### G5. Code and data deposits — S-D7 and the spec 24 simulation fields

Checking whether simulation code exists is a lookup, not a reading task.

**Closed.** Zenodo is working — 286,060 records carry `resource_type.type:software`, each with a DOI, so a deposit can be resolved by DOI or found by search. OSF's file listing and download work too, and GitHub raw was always reachable, with alphaXiv able to read a paper's repository for arXiv papers. Between them the three main deposit routes journals require are all covered.

This makes S-D7 cheap to apply as drafted: unavailable code is a downgrade only when the mechanism cannot be re-implemented, and that judgement now rests on a lookup rather than on the paper's own claim about availability.

### G6. Handbooks and books — spec 11

The Cochrane Handbook and the GRADE Handbook are named as orientation reading and neither is a journal article, so no paper index returns them.

**Partly closed.** Both are now reachable directly: the Cochrane Handbook on `training.cochrane.org` (the `methods` and `www` hosts are redirect hops to it) and the GRADE Handbook on `gdt.gradepro.org`. That covers the two named in spec 11, and with them the source of the GRADE-derived items in the empirical checklist — which currently cite the journal series rather than the handbook's own wording.

**Still open:** books in general. Much of the measurement-theory and philosophy-of-statistics literature is monographs, and no paper index or connector here returns book content. That is structural, not a configuration gap; the practical route is supplying specific PDFs.

### G7. Philosophy of science and statistics — spec 2 scope

**Partly closed.** PhilPapers is reachable through its OAI-PMH interface, which returns valid records; its JSON API is blocked at the origin and in any case expects a key. OAI harvesting is therefore the route — adequate for enumerating and pulling metadata, more awkward than a search API for targeted queries. PhilSci-Archive was not probed and would need its own grant.

Bears on the philosophy-of-statistics part of spec 2's scope, and so on the argument checklist's conceptual-claim path, where A-C1 allows Moderate for conceptual claims and argument is the on-type evidence.

### G8. Licensed indexes and what spec 47 can honestly claim

There is no Scopus, Web of Science, or Dimensions access here, and Google Scholar has no API. Every attached index derives from OpenAlex, Semantic Scholar, PubMed, or arXiv. The coverage note in spec 47 should say so: this is adequate for a survey with a reported strategy, and short of what a systematic review's coverage claim conventionally requires.

### G9. Calibration and forecasting data — optional, bears on the C-U1 anchor gap

The consensus upgrade C-U1 rests on a claim about structured elicitation and expert calibration for which the checklist draft records no adequate anchor. The relevant evidence is partly in tournament and prediction-market data (forecasting tournaments, replication markets) rather than in papers. Low priority relative to G1 and G2, but it is the empirical route to closing that parameter rather than re-deriving it from position papers.

---

## 5. Access ledger

Fourteen domains requested and granted on September 4, 2026, each then exercised against the requirement it was requested for. The count is higher than the number of sources because three hosts are needed for OSF downloads and three for the Cochrane Handbook, each being a redirect hop in one chain.

| Domain | Buys | Tested outcome |
|---|---|---|
| `api.osf.io` | G1 datasets, G2 registrations, G3 preprint records | works |
| `osf.io`, `files.osf.io`, `cos-osf-prod-files-us-east1.storage.googleapis.com` | The file-download chain behind the OSF API | works — see 3c |
| `www.ebi.ac.uk` | Europe PMC records and full text | works for the OA and in-EPMC subset |
| `zenodo.org` | G5 code and data deposit lookup | works, 286,060 software records |
| `api.labs.crossref.org` | Bulk Retraction Watch dataset | works — see 3c |
| `www.crd.york.ac.uk` | PROSPERO protocol registry | HTML only; its JSON endpoint rejects requests with "header value undefined", so treat PROSPERO as a manual lookup |
| `methods.cochrane.org`, `www.cochrane.org`, `training.cochrane.org` | Cochrane Handbook, spec 11 | works — the handbook is on `training.cochrane.org`; the other two are redirect hops |
| `gdt.gradepro.org` | GRADE Handbook, spec 11 | works |
| `philpapers.org` | G7 philosophy scope | OAI-PMH works; the JSON API is blocked at the origin |
| `pubpeer.com` | G4 | **unavailable.** Cloudflare Error 1010 on three endpoints across two attempts: the origin refuses automated clients as policy. No grant fixes this, and the correct response is a manual browser check, not a client that misrepresents itself |

Two further items need no grant and remain uncovered for their own reasons: the direct Semantic Scholar API is rate-limited without a key (and is redundant with three connectors that wrap it), and `storage.googleapis.com` in bare form is denylisted — the bucket-qualified host above is the grantable equivalent.

Nothing needs requesting for retraction checking, citation chaining, full text, preprint discovery, or paper search.

---

## 5b. Two routes worth writing into the Stage 0 procedure

**OSF downloads take three hops.** `api.osf.io` gives file metadata with a download link; that link 302s to `files.osf.io`, which 302s again to a signed URL in the GCS bucket `cos-osf-prod-files-us-east1`. Bare `storage.googleapis.com` is denylisted, so the bucket-qualified hostname is what must be granted and the final URL rewritten to virtual-hosted form. Verified end to end on the OSF preprint from section 3b: 387,370 bytes retrieved, valid PDF header, byte count matching the size the API declared. Any script that fetches OSF datasets for the validation set needs this rewrite.

**The Retraction Watch dataset is directly filterable.** Crossref Labs serves it as a single CSV: 72,389 rows, 66.5 MB, no `Content-Length`, so stream it. Columns include `Subject`, `Journal`, `ArticleType`, `RetractionDate`, `RetractionNature`, `Reason`, `OriginalPaperDOI` and `OriginalPaperPubMedID`; 69,622 rows carry an original-paper DOI. The most frequent reasons are investigation by journal or publisher (32,063), unreliable results or conclusions (21,909), and investigation by a third party (17,935). For spec 35 this means the retracted-and-refuted share of the validation set can be assembled by filtering on `Subject` and `Reason` and then resolving DOIs, rather than by manual search — with the documented reason serving as the answer key's cited source. It is a plain re-fetch, so there is no need to keep a copy: the fetch takes about 20 seconds.

---

## 6. Suggested spec amendments

1. **Spec 16.** Replace "queries replication trackers, Retraction Watch, PubPeer" with the concrete routes and their measured reliability: retraction and correction status via Crossref `updated-by` (reliable, tested); replication outcomes via a named database from G1 (once assembled); citing-paper stance via Scite citation intent as a *lead generator only*, given the sparse labelling measured in section 3b; PubPeer as a manual browser check, since its origin refuses automated clients. The load-bearing part of the channel remains spec 16's own parallel disconfirming query sets.
2. **Spec 33.** Add a retraction and correction check to the citation audit gate, since it is now nearly free per DOI. A run citing a retracted source should fail the audit, not merely note it.
3. **Spec 24.** Consider adding a *retraction or correction status* field, and a *code or data deposit* field distinct from "whether code is available" as reported by the paper.
4. **Spec 18.** Add OSF as a full-text route: OSF-hosted preprints are both discoverable and retrievable (G3, verified end to end), so they are tagged **full text**, not abstract only. State that the access-level tag is taken from the retrieval route actually used — or from Scite's explicit full-text-versus-abstract flag — rather than inferred from the publisher or from an expectation of a paywall. Note the three-hop download chain in 5b, since a route failure would otherwise be mistaken for an access-level fact.
5. **Spec 53 (known limits).** Consensus is loaded and reachable; that clause is stale. The live limits are the absence of licensed indexes (G8), the book blind spot in G6 (the two named handbooks are now reachable; monographs are not), AsPredicted having no API at all, PubPeer refusing automated access, FastTrack's debate and saturation tools and SciSpace's field extraction remaining unassessed, and Scite's citation intent being characterised as too sparse to evidence dissent.
6. **Specs 35 and 51.** Name the two sourcing routes that turn validation-set assembly into filtering — the bulk Retraction Watch dataset and the OSF-hosted replication databases — without weakening spec 35's rule that the user assembles the set and the model does not write the key.

**Status: all six were adopted in specs v3**, which also amends 4, 11, 26, 28, 37, 45, 49, 52 and 56 and adds 57 through 60. This section is retained as the reasoning trail behind those edits.
