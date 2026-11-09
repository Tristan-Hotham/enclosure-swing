"""Step 1: link every place named in a parliamentary enclosure Act to a parish of Caprettini and Voth's 1851 parish data.

Rule (fixed in NOTES.md before any outcome model):
  name tier   the place's name (as written, any alternative spelling, or the gazetteer's name) has the same key as a CV
              parish in the county named in the title (or the gazetteer county); then the same against a component of
              a compound CV parish name ("Stow cum Quy" -> stow, quy); then simple variants of the place name ("Woodend in
              Blakesley" -> blakesley; "Speen Moor" -> speen). Several parishes with the key in the county: the one
              nearest the gazetteer point if there is one, otherwise left ambiguous.
  conflict    a name match more than 10 km from the gazetteer point is not used (rule added after reading the
              disagreements by eye, before any outcome model): the point is used if it falls in a parish.
  ambiguous   a unique CV name match for a place the gazetteer found several of in the county (and could not place)
              is not used in the main link (same rule, same time).
  spatial     otherwise, if the enclosure study located the place, the CV parish whose centroid is nearest, if within
              max(2 km, 1.2 x that parish's equivalent radius).
For every located place the spatial candidate is also kept, so that name and point can be compared.
Output: data/act_parish_links.csv (one row per place named in an Act), SCR/links.pkl.
"""
import pandas as pd, numpy as np
from collections import defaultdict
from common import *

P = pd.read_csv(f"{SWING}/parishes.csv")
E = pd.read_csv(f"{ENC}/enclosed_places.csv")
A = pd.read_csv(f"{ENC}/enclosure_acts.csv")
P["r_km"] = np.sqrt(P.AREA_m2 / np.pi) / 1000

full = defaultdict(lambda: defaultdict(set))
part = defaultdict(lambda: defaultdict(set))
for r in P.itertuples():
    c = r.GAZ_CNTY
    full[c][key(r.PARISH)].add(r.PARISH_ID)
    alts = re.findall(r"\[(.*?)\]", r.PARISH)
    for a in alts:
        full[c][key(a)].add(r.PARISH_ID)
    base = re.sub(r"\[.*?\]", "", r.PARISH)
    comps = re.split(r",| WITH | CUM | AND ", base)
    if len(comps) > 1:
        for x in comps:
            if key(x):
                part[c][key(x)].add(r.PARISH_ID)
ALLC = sorted(P.GAZ_CNTY.unique())
pidx = P.set_index("PARISH_ID")
FAR_KM = 10.0
plat, plon, prad, pids = P.lat.values, P.lon.values, P.r_km.values, P.PARISH_ID.values


def nearest(lat, lon):
    d = haversine(lat, lon, plat, plon)
    i = int(np.argmin(d))
    return int(pids[i]), float(d[i]), bool(d[i] <= max(2.0, 1.2 * prad[i]))


def variants(n):
    out = []
    k = key(n)
    m = re.match(r"^(.*?) (in|within|near|next) (.+)$", k)
    if m:
        out += [m.group(3), m.group(1)]
    w = k.split()
    while len(w) > 1 and w[-1] in LANDWORDS:
        w = w[:-1]
        out.append(" ".join(w))
    w = k.split()
    while len(w) > 1 and w[0] in LANDWORDS:
        w = w[1:]
        out.append(" ".join(w))
    return [x for x in out if x and x != k]


def pick(cands, lat, lon):
    cands = sorted(cands)
    if len(cands) == 1:
        return cands[0], "unique"
    if lat == lat and lat is not None:
        d = [haversine(lat, lon, pidx.loc[c, "lat"], pidx.loc[c, "lon"]) for c in cands]
        return cands[int(np.argmin(d))], "by point"
    return None, "ambiguous"


rows = []
for i, r in enumerate(E.itertuples()):
    names = [r.place] + ([x.strip() for x in str(r.alternative_spellings).split(";")] if isinstance(r.alternative_spellings, str) else [])
    if isinstance(r.gazetteer_name, str):
        names.append(r.gazetteer_name)
    counties = list(dict.fromkeys(cv_counties(r.county_given) + cv_counties(r.gazetteer_county)))
    nocounty = not counties
    if nocounty:
        counties = ALLC
    lat, lon = (r.lat, r.lon) if r.lat == r.lat else (float("nan"), float("nan"))
    name_pid, tier, how = None, None, None
    for t, idx, keys in (("name", full, [key(n) for n in names]), ("name_part", part, [key(n) for n in names]),
                         ("name_variant", full, [v for n in names for v in variants(n)]),
                         ("name_variant_part", part, [v for n in names for v in variants(n)])):
        for k in keys:
            if not k:
                continue
            cands = set()
            for c in counties:
                cands |= idx[c].get(k, set())
            if nocounty and len(cands) > 1:
                cands = set()      # a name found in several counties with no county given: not used
            if cands:
                pid, how = pick(cands, lat, lon)
                if pid is not None:
                    name_pid, tier = pid, t
                    break
                how = "ambiguous"
        if name_pid is not None:
            break
    sp_pid, sp_d, sp_ok = (None, None, False)
    if lat == lat:
        sp_pid, sp_d, sp_ok = nearest(lat, lon)
    d_name = float(haversine(lat, lon, pidx.loc[name_pid, "lat"], pidx.loc[name_pid, "lon"])) if (name_pid is not None and lat == lat) else None
    if name_pid is not None and d_name is not None and d_name > FAR_KM:
        # the name points to a parish far from where the gazetteer put the place (e.g. one of many Carltons in
        # Yorkshire): trust neither the name nor, alone, the point; use the point only if it falls in a parish
        pid, method = (sp_pid, "spatial_conflict") if sp_ok else (None, "conflict")
    elif name_pid is not None and r.match == "ambiguous" and lat != lat and how == "unique" and nocounty is False and len(names) == 1:
        # the gazetteer found several places of this name in the county and could not place it; a single CV parish
        # of the name may be the wrong one of them (e.g. one of many Thorntons in Yorkshire): not used in the main link
        pid, method = None, "ambiguous_name"
    elif name_pid is not None:
        pid, method = name_pid, tier
    elif sp_ok:
        pid, method = sp_pid, "spatial"
    else:
        pid, method = None, "unmatched"
    rows.append(dict(row=i, source=r.source, year=int(r.year), chapter=r.chapter, title=r.title, place=r.place,
                     county_given=r.county_given if isinstance(r.county_given, str) else "", gaz_match=r.match,
                     gaz_lat=r.lat, gaz_lon=r.lon, method=method, tie=how if name_pid is not None else "",
                     parish_id=pid, name_pid=name_pid, spatial_pid=sp_pid if sp_ok else None, spatial_km=sp_d,
                     name_point_km=d_name))
L = pd.DataFrame(rows)
# extended variant (sensitivity only, not in the main exposure): close spellings within the stated county
import difflib
fz = []
for r in L.itertuples():
    out = None
    if r.method in ("unmatched", "conflict", "ambiguous_name") and r.county_given:
        counties = cv_counties(r.county_given)
        keys = {k: c for c in counties for k in full[c]}
        best = []
        for n in [r.place]:
            k = key(n)
            for m in difflib.get_close_matches(k, list(keys), n=3, cutoff=0.85):
                best.append((difflib.SequenceMatcher(None, k, m).ratio(), m))
        best.sort(reverse=True)
        if best and (len(best) == 1 or best[0][0] - best[1][0] >= 0.05):
            ids = full[keys[best[0][1]]][best[0][1]]
            if len(ids) == 1:
                out = next(iter(ids))
    fz.append(out)
L["fuzzy_pid"] = fz
for c in ("parish_id", "name_pid", "spatial_pid", "fuzzy_pid"):
    L[c] = L[c].astype("Int64")
L["parish"] = L.parish_id.map(lambda x: None if pd.isna(x) else pidx.loc[int(x), "PARISH"])
L["parish_county"] = L.parish_id.map(lambda x: None if pd.isna(x) else pidx.loc[int(x), "GAZ_CNTY"])
L["in_sample"] = L.parish_id.map(lambda x: False if pd.isna(x) else bool(pidx.loc[int(x), "sample"] == 1))
L["agree"] = (L.name_pid.notna() & L.spatial_pid.notna() & (L.name_pid == L.spatial_pid))
L.to_pickle(f"{SCR}/links.pkl")
L.drop(columns=["row"]).to_csv(f"{DATA}/act_parish_links.csv", index=False)
W = L[(L.year >= RECENT[0]) & (L.year <= RECENT[1])]
print("fuzzy rescues", L.fuzzy_pid.notna().sum(), L[L.fuzzy_pid.notna()].assign(fp=lambda d: d.fuzzy_pid.map(lambda x: pidx.loc[int(x), "PARISH"]))[["place", "fp"]].sample(25, random_state=1).values.tolist())
print("all rows", len(L), L.method.value_counts().to_dict())
print("1790-1830 rows", len(W), W.method.value_counts().to_dict(), "matched share", round((W.method != 'unmatched').mean(), 3))
both = L[L.name_pid.notna() & L.spatial_pid.notna()]
print("name & spatial both present", len(both), "agree", round(both.agree.mean(), 3))
print("name-to-point distance median", L.name_point_km.median(), "p90", L.name_point_km.quantile(.9))
