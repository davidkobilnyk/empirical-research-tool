# Coverage note — Does pre-registration of studies predict higher replication rates?

Run 2026-09-04. Stage 0: retrieval only, no grades.

## Query sets (spec 15, recorded as executed)

- **supporting**: Does pre-registration of studies predict higher replication rates?
- **disconfirming**: Evidence that pre-registration does not improve replicability or reduce publication bias

## Channels and yield

| Channel / query set | Records |
|---|---|
| consensus/dis | 10 |
| consensus/sup | 10 |
| fasttrack/dis | 18 |
| fasttrack/sup | 20 |
| scholargw/dis | 14 |
| scholargw/sup | 15 |
| scispace/dis | 10 |
| scispace/sup | 10 |

107 records returned, **93 unique sources** after deduplication (13% duplicates); 78 carry a resolvable DOI.

2 source(s) were returned by more than one channel. Channels drawing on overlapping upstream corpora can still return near-disjoint sets, so this figure is measured per run rather than assumed (spec 58).

## Query set overlap, per record (spec 16)

How much of the disconfirming set's yield was the supporting set's own results. A high figure means the channel was searched twice for the same thing, whatever the query said.

**Read the per-work table under Source identity instead where it is present.** These record-level figures are inflated wherever a channel returned several copies of one work; they are what is computable before linkage has run. No threshold is applied to either table: see the note at the end of the per-work table.

| Channel | Shared sources | Jaccard |
|---|---|---|
| consensus | 3 | 0.176 |
| fasttrack | 5 | 0.152 |
| scholargw | 3 | 0.115 |
| scispace | 1 | 0.053 |

## Access mix (spec 18)

- abstract only: 34
- extracted fields: 26
- full text: 33

## Integrity (spec 33)

- clean: 66
- corrected: 3
- not in crossref: 8
- retracted: 1

**A retracted source is present. Any run citing it fails the citation audit** — it is not sufficient to note it.

## Source identity (linkage)

Linkage ran with registry enrichment **network**.

93 source records resolve to **85 distinct works** (8 redundant records across 5 clusters; largest cluster 4).

Counts of *sources* above describe retrieval. Any statement about independent support must count works: copies of one study share its data, authors and analysis, and the error from counting records is one-directional — duplicates only ever add.

- linked by version/identity relation: 5
- linked by title with an author or year guard: 12
- linked by title with no guard available: 0
- title collisions rejected by the guard: 0
- records with no DOI: 15; records with neither DOI nor title, so unlinkable: 0

### Query set overlap, per work (spec 16)

| Channel | Shared works | Jaccard |
|---|---|---|
| consensus | 3 | 0.176 |
| fasttrack | 5 | 0.156 |
| scholargw | 3 | 0.115 |
| scispace | 1 | 0.083 |

Works returned by both query sets:

- campbell s law explains the replication crisis pre registration badges (0 DOIs)
- pre analysis plans have limited upside especially where replications a (0 DOIs)
- preregistration in practice a comparison of preregistered and non prer (2 DOIs)
- replicability robustness and reproducibility in psychological science (1 DOI)
- evaluating the replicability of social science experiments in nature a (1 DOI)
- global burden of 369 diseases and injuries in 204 countries and territ (1 DOI)
- a review of point cloud registration algorithms for mobile robotics (1 DOI)
- small sample sizes reduce the replicability of task based fmri studies (1 DOI)
- brain association studies in 2024 a systematic review of sample sizes  (1 DOI)
- a framework for evaluating reproducibility and replicability in econom (1 DOI)
- assessing preregistration deviations a comparative analysis of psychol (1 DOI)
- does preregistration improve the credibility of research findings (4 DOIs)

No cutoff is applied to these figures, deliberately. A threshold exists to trigger an action, and there is no validated action here: the only remedy previously prescribed — re-word the disconfirming query — is measurably ineffective on channels whose search is weakly sensitive to negation, where a correctly negated claim still retrieves the supporting set's results. The index is also coarse at these set sizes: with ten sources per query set one shared work moves it by about 0.07, so a two-decimal cutoff claims precision the measurement does not have. Read the named works above, compare the figure across runs of the same question, and treat a channel that keeps returning the same works for opposite queries as needing a different disconfirmation mechanism rather than a better sentence. Whether a gate belongs here at all is a spec 44 rubric-parameter question, and answering it needs evidence that high-overlap runs actually miss disconfirming evidence.

Not covered: work identity is narrower than independence. Two different papers from one group on one dataset share data and authors and are not independent; no title-or-DOI linkage detects that.

## Limits that hold regardless of this run

- No licensed index (Scopus, Web of Science, Dimensions) and no Google Scholar.
- No book-length literature; the Cochrane and GRADE handbooks are reachable, monographs are not.
- PubPeer refuses automated clients, so that channel is a manual check.
