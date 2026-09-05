# Still Cited — build pipeline

The published page is `../index.html`: one self-contained file, ~12.8 MB, no build step and no
network access at runtime. These are the scripts that produced it.

## Rebuild

```bash
# 1. Retraction Watch, free and complete, distributed by Crossref (CC0). ~66 MB.
curl -L --compressed -o retractionwatch.csv \
  "https://api.labs.crossref.org/data/retractionwatch?YOUR@EMAIL"

# 2. OpenAlex citation histories for every work flagged retracted (~135k, ~3 min).
python3 pull_openalex.py            # -> openalex_retracted.json

# 3. Join on normalised DOI, encode to typed arrays -> payload.json (~12.7 MB)
python3 build_payload.py

# 4. Splice the payload into the templates -> index.html
python3 inject.py
```

`build_payload.py` also needs `oa_only_top.json` (titles for the twelve most-cited works that
OpenAlex flags and Retraction Watch does not list); it is produced by a short one-off query
against the same OpenAlex endpoint, filtering `doi:` to a pipe-joined batch.

## Why it is built this way

A published Artifact cannot fetch anything at runtime (CSP blocks fetch/XHR/websocket), so all
data is gathered at build time and baked in. The payload is spliced by `inject.py` rather than
written by hand, which keeps a 12 MB blob out of the authoring loop.

## Sources and licence

- Retraction Watch database, distributed by Crossref — **CC0**.
- OpenAlex — **CC0**.

Both are public-domain dedications, so this is redistributable. Attribution is still the decent
thing to do, and the page carries it in the footer and the methods panel.
