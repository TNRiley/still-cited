# 📄 Still Cited

**What the literature did after each paper was withdrawn.**

→ **[Open it](https://tnriley.github.io/still-cited/)**

Every retraction Retraction Watch has catalogued — 72,389 notices — joined by DOI to OpenAlex citation histories. A field of 72,000 marks plots each paper's publication date against how long it survived; facets slice by reason, journal, publisher, country and field; any mark opens the paper, its original reason codes and its DOI. Of the 39,030 papers whose full citation history is observable, 69% were cited again after the year they were retracted, and 34% of every citation they ever collected arrived after the notice.

## Running it

One self-contained HTML file. No build step, no server, no network access at runtime — open `index.html` in a browser, or serve the directory with any static host.

```bash
python3 -m http.server 8000   # then visit http://localhost:8000
```

## Source

The full build pipeline is in [`src/`](src/), with a README describing how to regenerate the page from scratch.

## Data

- **[Retraction Watch database, distributed by Crossref](https://api.labs.crossref.org/data/retractionwatch)** — CC0
- **[OpenAlex](https://openalex.org)** — CC0

Every figure on the page is computed from the data shipped with it. Check the page's own methods panel for how each number is derived and where it should not be pushed.

## Built with

vanilla JS, canvas, typed-array payload.

## Licence

Code is MIT (see [LICENSE](LICENSE)). Data keeps the licence of its source, listed above.

---

Part of [Quick Projects](https://github.com/TNRiley/quick-projects) — one self-contained thing, built in one session. First published 2026-09-05.
