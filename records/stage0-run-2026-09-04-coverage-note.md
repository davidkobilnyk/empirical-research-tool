# Coverage note — Does pre-registration of studies predict higher replication rates?

Run 2026-09-04. Stage 0: retrieval only, no grades.

## Query sets (spec 15, recorded as executed)

- **supporting**: Does pre-registration of studies predict higher replication rates?
- **disconfirming**: Evidence that pre-registration does not improve replicability or reduce publication bias

## Channels and yield

| Channel / arm | Records |
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

## Arm independence (spec 16)

How much of the disconfirming arm's yield was the supporting arm's own results. A high figure means the channel was searched twice for the same thing, whatever the query said.

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

93 source records resolve to **85 distinct works** (8 redundant records across 5 clusters; largest cluster 4).

Counts of *sources* above describe retrieval. Any statement about independent support must count works: copies of one study share its data, authors and analysis, and the error from counting records is one-directional — duplicates only ever add.

- linked by version/identity relation: 5
- linked by title with an author or year guard: 10
- linked by title with no guard available: 0
- title collisions rejected by the guard: 2
- records with no DOI: 15; records with neither DOI nor title, so unlinkable: 0

Not covered: work identity is narrower than independence. Two different papers from one group on one dataset share data and authors and are not independent; no title-or-DOI linkage detects that.

## Limits that hold regardless of this run

- No licensed index (Scopus, Web of Science, Dimensions) and no Google Scholar.
- No book-length literature; the Cochrane and GRADE handbooks are reachable, monographs are not.
- PubPeer refuses automated clients, so that channel is a manual check.
