# Rebuilding Still Cited

Written for an LLM with a shell, starting from nothing but this file. Follow it in order.
The numbers in **Verification** are the real ones — if yours disagree, something is wrong.

---

## 1. What you are building

A single self-contained HTML page: a faceted research bench over **every retraction notice
Retraction Watch has catalogued**, joined by DOI to **OpenAlex citation histories**, so a reader
can see what the literature did *after* each paper was withdrawn.

The thesis the page exists to demonstrate: **retraction does not stop citation.**

---

## 2. Get the data

### Retraction Watch, via Crossref (CC0, free, complete)

```bash
curl -L --compressed -o retractionwatch.csv \
  "https://api.labs.crossref.org/data/retractionwatch?YOUR@EMAIL"
```

~66 MB, ~72,400 rows. Columns used: `Title`, `Journal`, `Publisher`, `Country`, `Subject`,
`RetractionDate`, `OriginalPaperDate`, `OriginalPaperDOI`, `RetractionNature`, `Reason`.

Quirks that will bite you:
- Dates are `M/D/YYYY H:MM`. Naive slicing silently mangles them — parse properly.
- `Reason` is `;`-delimited, **multi-valued**, and there are 112 distinct codes. Facet counts
  therefore sum to more than the number of records. That is correct, not a bug.
- The most common "reason" is `Investigation by Journal/Publisher` (~32k). It is a *process*
  marker, not a cause. Any chart that presents it as a reason for retraction is lying.

### OpenAlex citation histories (CC0, no key)

Cursor-page every work flagged retracted, ~135k records, about 3 minutes:

```
https://api.openalex.org/works
  ?filter=is_retracted:true
  &per-page=200
  &select=doi,publication_year,cited_by_count,counts_by_year,type
  &cursor=*        (then meta.next_cursor)
  &mailto=YOUR@EMAIL
```

The per-year field is `counts_by_year`, and each entry's count key is **`cited_by_count`**, not
`count`. It runs 2012→present only.

### Join

Normalise DOIs to lowercase, strip the `https://doi.org/` prefix, join on the original paper DOI.

---

## 3. The measurement, and the trap in it

"Cited after retraction" = citations in a calendar year **strictly later** than the year the
notice appeared. A paper retracted in December gets all of that December credited to its life,
not its afterlife. This under-counts deliberately; say so on the page.

**The trap.** Eligibility for the afterlife statistic must depend on the **observation window
alone** — never on whether the paper was actually cited afterwards. The first version of this
build required a paper to have citations both well before and well after retraction, which
selects for exactly the behaviour it claims to detect. It cut the eligible set from 39,030 to
9,075 and inflated every figure.

The correct rule: **published 2012 or later, retracted 2014–2024.** A paper cited zero times
after retraction qualifies and counts as a zero.

---

## 4. Encode the payload

The page carries all 72,389 records. Ship parallel typed arrays as base64, not JSON objects:

| array | type | notes |
|---|---|---|
| `pubM`, `retM` | Int16 | months since 1900; `-1` unknown |
| `nature`, `subjTop`, `ctry`, `flags` | Uint8 | `flags` bit 0 = matched to OpenAlex, bit 1 = afterlife-eligible |
| `jour`, `pubr`, `rmask`, `cites`, `post` | Uint16 | `rmask` is a bitmask over 15 reason groups |
| `off` | Uint8 | 11 per record: citations in retraction year −4 … +6, clamped at 255 |
| `rIdx`/`rCnt`, `sIdx`/`sCnt` | Uint8 | flat index arrays + per-record counts; prefix-sum to offsets in JS |

Titles and DOIs go as newline-joined strings, split once on load. Trim titles to 110 chars and
strip the redundant `RETRACTED:` prefix publishers add.

Budget: ~12.7 MB total, ~7 MB of it titles. It first came out at 15.2 MB — counts instead of
offsets, Uint8 subject codes, and dropping retraction-notice DOIs got it under the cap.

Splice the payload into the template with an injector script (`src/inject.py`) rather than
emitting it inline. A 12 MB blob must never pass through the authoring conversation.

---

## 5. The page

Full-bleed, desktop-first — a narrow centred column is the wrong default for a tool.

- **Bench**: three columns — filter rail (262px) | field | record panel (344px). Below it a
  four-column facet row. Both collapse to one column on mobile.
- **The field**: 72k marks, x = publication date (1980–2027, clamped), y = years-to-retraction
  on a log scale. Draw the whole corpus faint, then the current selection stamped in the accent.
  Do **not** colour by reason — 15 categories is a mess.
- Overlay a median-survival curve **stopping at papers published in 2018**, and draw the
  censoring diagonal as a dashed line. Beyond 2018 the curve slopes down for arithmetic reasons,
  not editorial ones.
- **Afterlife chart**: mean citations per paper per year, offsets −4…+6, shaded after year 0.
  It must respond to the filters, which is why `off` is per-record rather than precomputed.
- Facets: reason group, journal, publisher, country — counts recomputed from the selection.
- Every record links to `https://doi.org/<doi>`. Non-negotiable: the point is traceability.
- Auto/Light/Dark switch applied before first paint from `localStorage`.
- A methods panel, laid out as a grid of intact blocks so it fills the width.

---

## 6. Verification

| Check | Expected |
|---|---|
| Retraction Watch rows | 72,389 |
| OpenAlex flagged retracted | 135,192 |
| Matched on DOI | 59,971 |
| Flagged by OpenAlex, absent from RW | 75,221 |
| Afterlife-eligible | 39,030 |
| Cited at least once after retraction | 69% |
| Citations arriving after retraction | 214,480 — 34% of all their citations |
| Median time to retraction | 1.33 years (p95 10 years, max 81) |
| Paper-mill share of 2023 retractions | ~50% (6,782 of 13,564) |
| Default record | Raoult hydroxychloroquine paper — withdrawn after 1 month, 4,968 citations, 2,099 after |

If "cited after retraction" lands near 90%, you have re-introduced the eligibility trap.

---

## 7. Say these things on the page

- A citation is not an endorsement; some post-retraction citations are *about* the retraction.
- The 2023 peak is largely one publisher's bulk purge of compromised special issues.
- Retraction is not fraud — expressions of concern, corrections and honest-error withdrawals are
  all in the file. Retraction Watch even codes a reason called *Doing the Right Thing*.
- The two sources disagree on 75,221 works, and neither is simply wrong: OpenAlex flags from
  publisher metadata, Retraction Watch curates notices by hand.
