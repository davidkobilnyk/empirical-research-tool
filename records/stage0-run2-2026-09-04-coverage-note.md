# Coverage note — Does pre-registration of studies predict higher replication rates?

Run 2026-09-04. Stage 0: retrieval only, no grades.

## Query sets (spec 15, recorded as executed)

- **supporting**: Does pre-registration of studies predict higher replication rates?
- **disconfirming**: Pre-registration does not improve replicability and does not reduce publication bias

## Channels and yield

| Channel / query set | Records |
|---|---|
| consensus/disconfirming | 10 |
| consensus/supporting | 10 |
| fasttrack/disconfirming | 18 |
| fasttrack/supporting | 20 |
| scholargw/disconfirming | 14 |
| scholargw/supporting | 15 |
| scispace/disconfirming | 10 |
| scispace/supporting | 10 |

107 records returned, **89 unique sources** after deduplication (16% duplicates); 75 carry a resolvable DOI.

3 source(s) were returned by more than one channel. Channels drawing on overlapping upstream corpora can still return near-disjoint sets, so this figure is measured per run rather than assumed (spec 58).

## Query set overlap (spec 16)

How much of the disconfirming set's yield was the supporting set's own results. A high figure means the channel was searched twice for the same thing, whatever the query said.

| Channel | Shared sources | Jaccard |
|---|---|---|
| consensus | 3 | 0.176 |
| fasttrack | 5 | 0.152 |
| scholargw | 2 | 0.074 |
| scispace | 5 | 0.333 |

**Arm overlap at or above 0.30 on: scispace.** Re-word the disconfirming query as the negated claim and re-run before treating this run's disconfirmation channel as searched.

## Access mix (spec 18)

- abstract only: 29
- extracted fields: 27
- full text: 33

## Integrity (spec 33)

- clean: 64
- corrected: 3
- not in crossref: 7
- retracted: 1

**A retracted source is present. Any run citing it fails the citation audit** — it is not sufficient to note it.

## Source identity (linkage)

Linkage ran with registry enrichment **network**.

89 source records resolve to **80 distinct works** (9 redundant records across 4 clusters; largest cluster 6).

Counts of *sources* above describe retrieval. Any statement about independent support must count works: copies of one study share its data, authors and analysis, and the error from counting records is one-directional — duplicates only ever add.

- linked by version/identity relation: 4
- linked by title with an author or year guard: 20
- linked by title with no guard available: 0
- title collisions rejected by the guard: 0
- records with no DOI: 14; records with neither DOI nor title, so unlinkable: 0

Not covered: work identity is narrower than independence. Two different papers from one group on one dataset share data and authors and are not independent; no title-or-DOI linkage detects that.

## Limits that hold regardless of this run

- No licensed index (Scopus, Web of Science, Dimensions) and no Google Scholar.
- No book-length literature; the Cochrane and GRADE handbooks are reachable, monographs are not.
- PubPeer refuses automated clients, so that channel is a manual check.
