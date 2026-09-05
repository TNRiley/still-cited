import csv, json, base64, array, datetime, sys, collections, re
csv.field_size_limit(10**7)
norm = lambda d: (d or "").lower().replace("https://doi.org/", "").strip()
clean = lambda s: re.sub(r"\s+", " ", (s or "").replace("\n", " ").replace("\r", " ")).strip()

REASON_BUCKETS = [
 ("Paper mill", ["Paper Mill"]),
 ("Peer review manipulated", ["Compromised Peer Review","Concerns/Issues about Peer Review","Rogue Editor","Taken via Peer Review"]),
 ("Fabrication / manipulation", ["Falsification/Fabrication of Data","Falsification/Fabrication of Image","Falsification/Fabrication of Results","Manipulation of Data","Manipulation of Images","Manipulation of Results","Hoax Paper","Sabotage of Materials/Methods"]),
 ("Data problems", ["Concerns/Issues about Data","Unreliable Data","Error in Data","Original Data and/or Images not Provided and/or not Available","Duplication of Data","Results Not Reproducible","Error in Analyses","Contamination of Cell Lines/Tissues","Error in Cell Lines/Tissues","Contamination of Materials","Error in Materials","Error in Methods","Concerns/Issues about Methods"]),
 ("Image problems", ["Duplication of/in Image","Concerns/Issues about Image","Error in Image","Unreliable Image","Plagiarism of Image"]),
 ("Plagiarism / attribution", ["Concerns/Issues about Referencing/Attributions","Euphemisms for Plagiarism","Plagiarism of/in Article","Plagiarism of Text","Plagiarism of Data","Taken from Dissertation/Thesis","Copyright Claims","Taken via Translation"]),
 ("Duplicate publication", ["Duplication of/in Article","Euphemisms for Duplication","Duplication of Text","Duplication of Content through Error by Journal/Publisher","Salami Slicing"]),
 ("Authorship disputes", ["Concerns/Issues about Authorship/Affiliation","False/Forged Authorship","False/Forged Affiliation","Objections by Author(s)","Lack of Approval from Author","Author Unresponsive","Complaints about Author"]),
 ("AI / generated content", ["Computer-Aided Content or Computer-Generated Content"]),
 ("Ethics & consent", ["Lack of IRB/IACUC Approval and/or Compliance","Informed/Patient Consent - None/Withdrawn","Ethical Violations by Author","Concerns/Issues about Human Subject Welfare","Concerns/Issues about Animal Welfare","Ethical Violations by Company/Institution/Third Party","Conflict of Interest","Lack of Approval from Third Party","Lack of Approval from Company/Institution"]),
 ("Misconduct finding", ["Misconduct by Author","Misconduct - Official Investigation(s) and/or Finding(s)","Investigation by ORI","Misconduct by Third Party","Misconduct by Company/Institution","Euphemisms for Misconduct","Publishing Ban","Breach of Policy by Author"]),
 ("Unreliable conclusions", ["Unreliable Results and/or Conclusions","Concerns/Issues about Results and/or Conclusions","Error in Results and/or Conclusions","Error in Text","Concerns/Issues about Article","Bias Issues or Lack of Balance"]),
 ("Legal action", ["Legal Reasons and/or Threats","Civil Proceedings","Criminal Proceedings"]),
 ("Process / none given", ["Investigation by Journal/Publisher","Investigation by Third Party","Investigation by Company/Institution","Notice - Limited or No Information","Date of Article and/or Notice Unknown","Error by Journal/Publisher","Error by Third Party","Upgrade/Update of Prior Notice(s)","Updated to Retraction","Updated to Correction","Updated to Expression of Concern","Removed","Temporary Removal","Retract and Replace","Withdrawn as Out of Date","Withdrawn to Publish in Different Journal","Notice - Lack of","Notice - Unable to Access via current resources","Objections by Third Party","Objections by Company/Institution","Concerns/Issues about Third Party Involvement","Miscommunication with/by Author","Miscommunication with/by Journal/Publisher","Miscommunication with/by Third Party","Miscommunication with/by Company/Institution","Doing the Right Thing","No Further Action","Transfer of Copyright and/or Ownership","Nonpayment of Fees and/or Refusal to Pay","Not Presented at Conference","Complaints about Third Party","Complaints about Company/Institution","Cites Retracted Work","EOC Lifted"]),
]
R2B = {}
for i, (nm, lst) in enumerate(REASON_BUCKETS):
    for r in lst: R2B[r] = i
OTHER = len(REASON_BUCKETS)
BUCKET_NAMES = [b[0] for b in REASON_BUCKETS] + ["Other"]
NATURES = ["Retraction", "Expression of concern", "Correction", "Reinstatement", "Unspecified"]

def pdate(s):
    s = (s or "").strip()
    if not s: return None
    for f in ("%m/%d/%Y %H:%M", "%m/%d/%Y", "%Y-%m-%d"):
        try: return datetime.datetime.strptime(s.split("+")[0].strip(), f).date()
        except ValueError: pass
    return None
mon = lambda d: (d.year - 1900) * 12 + (d.month - 1) if d else -1

# ---- OpenAlex citation histories ----
oa = json.load(open("openalex_retracted.json"))
OA = {}
for w in oa:
    d = norm(w.get("doi"))
    if d: OA[d] = w

rows = list(csv.DictReader(open("retractionwatch.csv", newline="", encoding="utf-8", errors="replace")))

jourT, pubT, ctryT, subjT, reasonT = {}, {}, {}, {}, {}
def idx(tbl, s):
    s = clean(s) or "Unrecorded"
    if s not in tbl: tbl[s] = len(tbl)
    return tbl[s]

N = len(rows)
A = lambda t: array.array(t)
pubM, retM = A("h"), A("h")
nature, subjTop, ctry, flags = A("B"), A("B"), A("B"), A("B")
jour, pubr, rmask, cites, post = A("H"), A("H"), A("H"), A("H"), A("H")
OFFW = 11          # citation years, retraction year -4 .. +6
off = A("B")
rIdxFlat, rCnt = A("B"), A("B")
sIdxFlat, sCnt = A("B"), A("B")
titles, dois, rdois = [], [], []
TOPCODE = {}

for r in rows:
    d0, d1 = pdate(r.get("OriginalPaperDate")), pdate(r.get("RetractionDate"))
    pubM.append(mon(d0)); retM.append(mon(d1))
    nat = clean(r.get("RetractionNature"))
    nature.append(NATURES.index(nat) if nat in NATURES else 4)
    jour.append(min(65534, idx(jourT, r.get("Journal"))))
    pubr.append(min(65534, idx(pubT, r.get("Publisher"))))
    ctry.append(min(254, idx(ctryT, (clean(r.get("Country")) or "Unrecorded").split(";")[0])))

    _r0 = len(rIdxFlat); m = 0
    for x in (r.get("Reason") or "").split(";"):
        x = clean(x).strip("+").strip()
        if not x: continue
        rIdxFlat.append(min(254, idx(reasonT, x)))
        m |= 1 << R2B.get(x, OTHER)
    rmask.append(m); rCnt.append(min(255, len(rIdxFlat) - _r0))

    _s0 = len(sIdxFlat); top = 0
    for s in (r.get("Subject") or "").split(";"):
        s = clean(s)
        if not s: continue
        sIdxFlat.append(min(254, idx(subjT, s)))
        code = s[1:s.index(")")] if s.startswith("(") and ")" in s else "?"
        if code not in TOPCODE: TOPCODE[code] = len(TOPCODE)
        top |= 1 << min(7, TOPCODE[code])
    subjTop.append(top); sCnt.append(min(255, len(sIdxFlat) - _s0))

    doi = norm(r.get("OriginalPaperDOI"))
    titles.append(re.sub(r"^(RETRACTED ARTICLE|RETRACTED|WITHDRAWN|Retracted)\s*:\s*", "", clean(r.get("Title")))[:110]); dois.append(doi); rdois.append(norm(r.get("RetractionDOI")))

    w = OA.get(doi); f = 0; c = p = 0; ov = [0]*OFFW
    if w:
        f |= 1; c = min(65535, w.get("cited_by_count") or 0)
        cby = w.get("counts_by_year") or []
        if cby and d1:
            for x in cby:
                if x["year"] > d1.year: p += x["cited_by_count"]
                k = x["year"] - d1.year + 4
                if 0 <= k < OFFW: ov[k] = min(255, ov[k] + x["cited_by_count"])
        # Eligibility depends on the OBSERVATION WINDOW (OpenAlex counts run 2012-2026),
        # never on the paper's own citation pattern — otherwise the measure selects for
        # exactly the behaviour it claims to detect. A paper with zero post-retraction
        # citations must be able to qualify and count as a zero.
        if d0 and d1 and d0.year >= 2012 and 2014 <= d1.year <= 2024: f |= 2
    cites.append(c); post.append(min(65535, p)); flags.append(f); off.extend(ov)

if sys.byteorder == "big":
    for a in (pubM, retM, jour, pubr, rmask, cites, post): a.byteswap()
b64 = lambda a: base64.b64encode(a.tobytes()).decode()
inv = lambda t: [k for k, v in sorted(t.items(), key=lambda kv: kv[1])]

out = {
 "n": N, "built": datetime.date.today().isoformat(),
 "buckets": BUCKET_NAMES, "natures": NATURES,
 "topcodes": [k for k, v in sorted(TOPCODE.items(), key=lambda kv: kv[1])],
 "journals": inv(jourT), "publishers": inv(pubT), "countries": inv(ctryT),
 "subjects": inv(subjT), "reasons": inv(reasonT),
 "a": {k: b64(v) for k, v in dict(pubM=pubM, retM=retM, nature=nature, subjTop=subjTop, ctry=ctry,
      flags=flags, jour=jour, pubr=pubr, rmask=rmask, cites=cites, post=post, off=off,
      rIdx=rIdxFlat, rCnt=rCnt, sIdx=sIdxFlat, sCnt=sCnt).items()},
 "titles": "\n".join(titles), "dois": "\n".join(dois),
 "oaOnly": json.load(open("oa_only_top.json"))[:12],
 "offw": OFFW, "offBase": 4,
 "counts": {"rwRows": N, "oaFlagged": len(oa), "oaWithDoi": len(OA),
            "rwDistinctDoi": len({d for d in dois if d}),
            "matched": len({d for d in dois if d and d in OA})},
}
js = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
open("payload.json", "w", encoding="utf-8").write(js)
print(f"records {N}  journals {len(jourT)}  publishers {len(pubT)}  countries {len(ctryT)}  subjects {len(subjT)}  reasons {len(reasonT)}")
print("topcodes:", out["topcodes"])
print("matched:", out["counts"]["matched"], " afterlife-eligible:", sum(1 for f in flags if f & 2))
for k, v in out["a"].items(): print(f"   {k:8} {len(v)/1e6:6.2f} MB b64")
print(f"titles {len(out['titles'])/1e6:.2f} MB  dois {len(out['dois'])/1e6:.2f} MB")
print(f"TOTAL PAYLOAD {len(js)/1e6:.2f} MB")
