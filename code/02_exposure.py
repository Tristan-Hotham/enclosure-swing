"""Step 2: parish-level enclosure exposure for each linking variant, joined to the CV parish data.

Variants: main (01_link rule), name (name tiers only), spatial (gazetteer point only), agree (name and point agree),
extended (main plus close spellings and the ambiguous names). For each: years of every Act naming the parish.
Exposure (main variant names have no suffix): recent (any Act 1790 to 1830), old_only (Acts before 1790 only),
w10/w20/w40 (any Act 1821/1811/1791 to 1830), future (first Act 1831 to 1870, none before 1831), last_act year,
spill5/spill10 (other parishes with a recent Act within 5/10 km). Output: data/parishes_enclosure.csv, SCR/panel.pkl.
"""
import pandas as pd, numpy as np
from scipy.spatial import cKDTree
from common import *
import warnings; warnings.filterwarnings("ignore")

P = pd.read_csv(f"{SWING}/parishes.csv")
L = pd.read_pickle(f"{SCR}/links.pkl")
L["ext_pid"] = L.parish_id.fillna(L.fuzzy_pid)
L.loc[L.method == "ambiguous_name", "ext_pid"] = L.loc[L.method == "ambiguous_name", "name_pid"]
VAR = {"": L.parish_id, "_name": L.parish_id.where(L.method.str.startswith("name")), "_spatial": L.spatial_pid,
       "_agree": L.parish_id.where(L.agree), "_ext": L.ext_pid}
lat0 = np.radians(52.5)
XY = np.c_[P.lon.values * 111.32 * np.cos(lat0), P.lat.values * 110.57]
tree = cKDTree(XY)
for suf, col in VAR.items():
    yrs = pd.DataFrame({"pid": col, "year": L.year}).dropna()
    yrs["pid"] = yrs.pid.astype(int)
    g = yrs.groupby("pid").year
    pre = yrs[yrs.year <= RECENT[1]].groupby("pid").year
    P["n_acts" + suf] = P.PARISH_ID.map(g.size()).fillna(0).astype(int)
    P["first_act" + suf] = P.PARISH_ID.map(g.min())
    P["last_pre" + suf] = P.PARISH_ID.map(pre.max())
    rec = yrs[(yrs.year >= RECENT[0]) & (yrs.year <= RECENT[1])].pid.unique()
    P["recent" + suf] = P.PARISH_ID.isin(rec).astype(int)
    old = yrs[yrs.year < RECENT[0]].pid.unique()
    P["old_only" + suf] = (P.PARISH_ID.isin(old) & ~P.PARISH_ID.isin(rec)).astype(int)
    P["never" + suf] = ((P["recent" + suf] == 0) & (P["old_only" + suf] == 0)).astype(int)
    for w, a in (("w10", 1821), ("w20", 1811), ("w40", 1791)):
        P[w + suf] = P.PARISH_ID.isin(yrs[(yrs.year >= a) & (yrs.year <= RECENT[1])].pid.unique()).astype(int)
    fut = yrs[(yrs.year >= FUTURE[0]) & (yrs.year <= FUTURE[1])].pid.unique()
    P["future" + suf] = (P.PARISH_ID.isin(fut) & P["last_pre" + suf].isna()).astype(int)
    for km in (5, 10):
        nb = tree.query_ball_point(XY, r=km)
        rv = P["recent" + suf].values
        P[f"spill{km}" + suf] = [int(rv[j].sum() - rv[i]) for i, j in enumerate(map(np.array, nb))]
P["years_since"] = (1830 - P.last_pre).where(P.last_pre.notna())
with np.errstate(divide="ignore"):
    P["log_density"] = np.log(P.density)
P["log_sex_ratio"] = np.log(P.sex_ratio.where(P.sex_ratio > 0))
P["log_distel"] = np.log(P.distel)
P["log_distnews"] = np.log(P.distnews)
P["any_swing"] = (P.SWING > 0).astype(int)
P["any_machine_attack"] = (P.BREAKTHRESH > 0).astype(int)
P["any_other"] = (P.REST > 0).astype(int)
P["grid50"] = (np.floor(XY[:, 0] / 50)).astype(int).astype(str) + "_" + (np.floor(XY[:, 1] / 50)).astype(int).astype(str)
P.to_pickle(f"{SCR}/panel.pkl")
keep = ["PARISH_ID", "GAZ_CNTY", "PARISH", "REGION", "sample", "lat", "lon", "SWING", "BREAKTHRESH", "REST", "thresh",
        "n_acts", "first_act", "last_pre", "recent", "old_only", "never", "w10", "w20", "w40", "future", "spill5", "spill10",
        "recent_name", "recent_spatial", "recent_agree", "recent_ext"]
P[keep].to_csv(f"{DATA}/parishes_enclosure.csv", index=False)
S = P[P["sample"] == 1]
print("sample", len(S), "recent", S.recent.sum(), "old_only", S.old_only.sum(), "never", S.never.sum(), "future", S.future.sum())
for suf in VAR:
    print(suf or "main", S["recent" + suf].sum())
