"""How often is the bridge the capital of the answer country? Reproduces the dev/test split.
Usage: python3 -I checks/bridge_capital_check.py data/twohopfact/twohopfact_slim.csv
(slim CSV made by streaming soheeyang/TwoHopFact and dropping the alias columns)."""
import csv, collections, hashlib, re, unicodedata, sys
def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9]+"," ",s).split())
def split_of(e2, dev_frac=0.3, seed=0):
    h = int(hashlib.md5(f"{seed}-{norm(e2)}".encode()).hexdigest(),16) % 10_000
    return "dev" if h < dev_frac*10_000 else "test"
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
cap = {}
for r in rows:
    if r["category"] in ("anthem-cntry-capital","president-cntry-capital"):
        cap[norm(r["e2.value"])] = norm(r["e3.value"])
print("countries with a capital in TwoHopFact:", len(cap))
for cat in ["person-birthcity-cntry","univ-hqcity-cntry"]:
    rs = [r for r in rows if r["category"]==cat]
    have = [r for r in rs if norm(r["e3.value"]) in cap]
    iscap = [r for r in have if norm(r["e2.value"]) == cap[norm(r["e3.value"])]]
    # most frequent bridge per answer country
    by = collections.defaultdict(collections.Counter)
    for r in rs: by[norm(r["e3.value"])][norm(r["e2.value"])] += 1
    top1 = [r for r in rs if by[norm(r["e3.value"])].most_common(1)[0][0] == norm(r["e2.value"])]
    print(f"== {cat}: {len(rs)} facts; answer country has known capital: {len(have)}; bridge == capital: {len(iscap)} ({len(iscap)/len(have):.0%} of those)")
    print(f"   bridge is the most frequent bridge of its answer country: {len(top1)} ({len(top1)/len(rs):.0%})")
    for sp in ("dev","test"):
        s = [r for r in rs if split_of(r["e2.value"])==sp]
        sc = [r for r in s if norm(r["e3.value"]) in cap and norm(r["e2.value"])==cap[norm(r["e3.value"])]]
        b = collections.Counter(r["e2.value"] for r in s)
        print(f"   {sp}: {len(s)} facts, {len(b)} bridges, bridge==capital {len(sc)} ({len(sc)/len(s):.0%}); top bridges {b.most_common(6)}")
