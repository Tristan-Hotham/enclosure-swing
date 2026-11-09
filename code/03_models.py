"""Step 3: the planned models (NOTES.md, analysis plan) and every robustness check. Output: SCR/models.json, data/models_*.csv.

Main: linear probability model, any Swing incident on recent enclosure (Act 1790 to 1830) and old-only enclosure (Acts
before 1790 only), reference never enclosed by Act before 1831; CV controls, threshing machine, soils; county fixed
effects; standard errors clustered by county. Effects in percentage points with 95% confidence intervals.
"""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy import stats
from common import *

P = pd.read_pickle(f"{SCR}/panel.pkl").copy()
S0 = P[P["sample"] == 1].copy()
CT = " + ".join(CTRL)
S = S0.dropna(subset=CTRL).copy()
OUT = {}
rng = np.random.default_rng(SEED)


def fit(formula, data, xs, cluster="GAZ_CNTY", kind="ols", name=None):
    d = data.dropna(subset=[c for c in CTRL if c in formula]).copy()
    if kind == "ols":
        m = smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d[cluster])[0]})
    elif kind == "logit":
        m = smf.logit(formula, data=d).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(d[cluster])[0]}, maxiter=200)
    elif kind == "poisson":
        m = smf.poisson(formula, data=d).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(d[cluster])[0]}, maxiter=200)
    yv = formula.split("~")[0].strip()
    res = dict(name=name, n=int(m.nobs), ymean=float(d[yv].mean()), clusters=int(d[cluster].nunique()), coefs={})
    for x in xs:
        b, se = float(m.params[x]), float(m.bse[x])
        res["coefs"][x] = dict(b=b, se=se, lo=b - 1.96 * se, hi=b + 1.96 * se, p=float(m.pvalues[x]))
    if kind == "ols":
        res["r2"] = float(m.rsquared)
    if kind == "logit":
        me = m.get_margeff(at="overall")
        i = list(m.params.index[1:])
        for x in xs:
            j = i.index(x)
            res["coefs"][x].update(ame=float(me.margeff[j]), ame_se=float(me.margeff_se[j]), ame_lo=float(me.conf_int()[j][0]), ame_hi=float(me.conf_int()[j][1]))
    if kind == "poisson":
        for x in xs:
            c = res["coefs"][x]; c.update(irr=math.exp(c["b"]), irr_lo=math.exp(c["lo"]), irr_hi=math.exp(c["hi"]))
    res["all"] = {k: dict(b=float(m.params[k]), se=float(m.bse[k]), p=float(m.pvalues[k])) for k in m.params.index if not k.startswith("C(")}
    res["_model"] = m
    return res


def pp(r, x="recent"):
    c = r["coefs"][x]
    return f'{r["name"]}: {100*c["b"]:+.2f} pp [{100*c["lo"]:+.2f}, {100*c["hi"]:+.2f}] p={c["p"]:.3f} N={r["n"]}'


Y = "any_swing"
FE = " + C(GAZ_CNTY)"
main_f = f"{Y} ~ recent + old_only + {CT}{FE}"
M = {}
M["main"] = fit(main_f, S, ["recent", "old_only"], name="Main: LPM, county FE")
print(pp(M["main"])); print(pp(M["main"], "old_only"))
M["raw"] = fit(f"{Y} ~ recent + old_only", S0, ["recent", "old_only"], name="No controls, no FE")
M["ctrl_nofe"] = fit(f"{Y} ~ recent + old_only + {CT}", S, ["recent", "old_only"], name="Controls, no FE")
M["fe_noctrl"] = fit(f"{Y} ~ recent + old_only{FE}", S0, ["recent", "old_only"], name="County FE, no controls")
M["region_fe"] = fit(f"{Y} ~ recent + old_only + {CT} + C(REGION)", S, ["recent", "old_only"], name="Region FE")
M["market_fe"] = fit(f"{Y} ~ recent + old_only + {CT} + C(MARKETTOWN)", S, ["recent", "old_only"], name="Market-town FE", cluster="GAZ_CNTY")
M["grid_se"] = fit(main_f, S, ["recent", "old_only"], cluster="grid50", name="Clusters: 50 km grid cells")
M["logit"] = fit(main_f, S, ["recent", "old_only"], kind="logit", name="Logit, county FE (AME)")
M["poisson"] = fit(f"SWING ~ recent + old_only + {CT}{FE}", S, ["recent", "old_only"], kind="poisson", name="Poisson, incidents")
M["machine"] = fit(f"any_machine_attack ~ recent + old_only + {CT}{FE}", S, ["recent", "old_only"], name="Outcome: machine attack")
M["other"] = fit(f"any_other ~ recent + old_only + {CT}{FE}", S, ["recent", "old_only"], name="Outcome: other unrest")
M["count_ols"] = fit(f"SWING ~ recent + old_only + {CT}{FE}", S, ["recent", "old_only"], name="OLS, incidents")
for w in ("w10", "w20", "w40"):
    S[f"earlier_{w}"] = ((S.n_acts > 0) & (S.last_pre.notna()) & (S[w] == 0)).astype(int)
    M[w] = fit(f"{Y} ~ {w} + earlier_{w} + {CT}{FE}", S, [w, f"earlier_{w}"], name=f"Window {w[1:]} years")
# years since the last Act before 1831
S["ys_0_9"] = (S.years_since <= 9).astype(int); S["ys_10_19"] = S.years_since.between(10, 19).astype(int)
S["ys_20_39"] = S.years_since.between(20, 39).astype(int); S["ys_40p"] = (S.years_since >= 40).astype(int)
M["since"] = fit(f"{Y} ~ ys_0_9 + ys_10_19 + ys_20_39 + ys_40p + {CT}{FE}", S, ["ys_0_9", "ys_10_19", "ys_20_39", "ys_40p"], name="Years since last Act")
# spillovers
S["spill5_any"] = (S.spill5 > 0).astype(int); S["spill10_any"] = (S.spill10 > 0).astype(int)
M["spill"] = fit(f"{Y} ~ recent + old_only + spill5_any + spill10_any + {CT}{FE}", S, ["recent", "old_only", "spill5_any", "spill10_any"], name="With neighbours enclosed")
M["spill_n"] = fit(f"{Y} ~ recent + old_only + spill5 + spill10 + {CT}{FE}", S, ["recent", "old_only", "spill5", "spill10"], name="Neighbour counts")
# placebo: future enclosure among parishes not enclosed by Act before 1831
N0 = S[S.never == 1]
M["placebo_future"] = fit(f"{Y} ~ future + {CT}{FE}", N0, ["future"], name="Placebo: Act 1831 to 1870")
# Gonner district enclosure and poor-relief subsamples
S["log_poor_pc"] = np.log(S.POORRATE03 / S.POP01)
M["gonner"] = fit(f"{Y} ~ recent + old_only + enclosures + {CT}{FE}", S.dropna(subset=["enclosures"]), ["recent", "old_only", "enclosures"], name="With Gonner district enclosure")
M["gonner_base"] = fit(main_f, S.dropna(subset=["enclosures"]), ["recent", "old_only"], name="Gonner subsample, main")
M["poor"] = fit(f"{Y} ~ recent + old_only + log_poor_pc + {CT}{FE}", S.dropna(subset=["log_poor_pc"]), ["recent", "old_only", "log_poor_pc"], name="With poor relief per head 1803")
M["poor_base"] = fit(main_f, S.dropna(subset=["log_poor_pc"]), ["recent", "old_only"], name="Poor-rate subsample, main")
M["preriots"] = fit(f"{Y} ~ recent + old_only + I((preriots>0)*1) + {CT}{FE}", S, ["recent", "old_only"], name="With pre-1830 unrest")
# exploratory heterogeneity
S["recent_x_machine"] = S.recent * S.thresh1
S["se"] = (S.REGION == "South-East").astype(int); S["recent_x_se"] = S.recent * S.se
M["het_machine"] = fit(f"{Y} ~ recent + old_only + recent_x_machine + {CT}{FE}", S, ["recent", "recent_x_machine"], name="Exploratory: x machine")
M["het_se"] = fit(f"{Y} ~ recent + old_only + recent_x_se + {CT}{FE}", S, ["recent", "recent_x_se"], name="Exploratory: x South-East")
# equality of recent and old-only (planned H2 test)
mm = M["main"]["_model"]
wt = mm.t_test("recent - old_only = 0")
M["main"]["h2_diff"] = float(wt.effect[0]); M["main"]["h2_p"] = float(wt.pvalue)
M["main"]["h2_lo"], M["main"]["h2_hi"] = [float(x) for x in wt.conf_int()[0]]
M["anyact"] = fit(f"{Y} ~ I(recent + old_only) + {CT}{FE}", S, ["I(recent + old_only)"], name="Any Act before 1831")
# EXPLORATORY (added after the planned results were seen): parish area; a clean comparison that drops parishes whose
# exposure depends on the linking rule (treated by one rule, untreated by another)
S["log_area"] = np.log(S.AREA_m2 / 1e6)
M["x_area"] = fit(f"{Y} ~ recent + old_only + log_area + {CT}{FE}", S, ["recent", "old_only", "log_area"], name="Exploratory: with log area")
S["area_dec"] = pd.qcut(S.log_area, 10, labels=False)
M["x_area_dec"] = fit(f"{Y} ~ recent + old_only + C(area_dec) + {CT}{FE}", S, ["recent", "old_only"], name="Exploratory: area deciles")
M["x_area_logit"] = fit(f"{Y} ~ recent + old_only + log_area + {CT}{FE}", S, ["recent", "old_only"], kind="logit", name="Exploratory: logit with log area")
M["x_area_poisson"] = fit(f"SWING ~ recent + old_only + log_area + {CT}{FE}", S, ["recent", "old_only"], kind="poisson", name="Exploratory: Poisson with log area")
M["x_area_w10"] = fit(f"{Y} ~ w10 + earlier_w10 + log_area + {CT}{FE}", S, ["w10", "earlier_w10"], name="Exploratory: 10-year window with log area")
M["x_area_placebo"] = fit(f"{Y} ~ future + log_area + {CT}{FE}", S[S.never == 1], ["future"], name="Exploratory: placebo with log area")
M["x_area_other"] = fit(f"any_other ~ recent + old_only + log_area + {CT}{FE}", S, ["recent", "old_only"], name="Exploratory: other unrest with log area")
# how much bigger are enclosed parishes?
AREA = {k: float(np.exp(S[S[k] == 1].log_area.median())) for k in ("recent", "old_only", "never")}
unsure = (S[["recent", "recent_name", "recent_spatial", "recent_agree", "recent_ext"]].nunique(axis=1) > 1) | \
         (S[["old_only", "old_only_name", "old_only_spatial", "old_only_agree", "old_only_ext"]].nunique(axis=1) > 1)
M["x_clean"] = fit(main_f, S[~unsure], ["recent", "old_only"], name="Exploratory: parishes whose exposure all rules agree on")
M["x_clean"]["dropped"] = int(unsure.sum())
# linking variants
for suf, nm in (("_name", "Name matches only"), ("_spatial", "Gazetteer point only"), ("_agree", "Name and point agree"), ("_ext", "Extended (close spellings)")):
    d = S.copy(); d["recent"] = d["recent" + suf]; d["old_only"] = d["old_only" + suf]
    M["link" + suf] = fit(main_f, d, ["recent", "old_only"], name=nm)
# counties with a high match rate
L = pd.read_pickle(f"{SCR}/links.pkl")
W = L[(L.year >= RECENT[0]) & (L.year <= RECENT[1])].copy()
W["cty"] = W.county_given.map(lambda c: cv_counties(c)[0] if cv_counties(c) else None)
W["ok"] = W.parish_id.notna()
rate = W.dropna(subset=["cty"]).groupby("cty").ok.agg(["mean", "size"])
hi = [c for c in rate.index if rate.loc[c, "mean"] >= 0.8]
# Yorkshire is given as one county: apply its rate to the three ridings
for c in list(hi):
    pass
M["hi_match"] = fit(main_f, S[S.GAZ_CNTY.isin(hi)], ["recent", "old_only"], name="Counties with >= 80% matched")
for k in ("main", "raw", "machine", "other", "placebo_future", "logit", "poisson", "link_agree", "hi_match", "market_fe", "spill"):
    print(pp(M[k], list(M[k]["coefs"])[0]))

# randomisation inference: permute (recent, old_only) jointly within county
m0 = M["main"]["_model"]
d = S.dropna(subset=CTRL).reset_index(drop=True)
Xc = pd.get_dummies(d.GAZ_CNTY, drop_first=True).astype(float).values
Xb = np.c_[np.ones(len(d)), d[CTRL].values, Xc]
y = d[Y].values.astype(float)
# FWL: residualise y and treatments on controls + FE
Q, _ = np.linalg.qr(Xb)
def resid(v): return v - Q @ (Q.T @ v)
yr = resid(y)
def coef(T):
    Tr = np.c_[resid(T[:, 0]), resid(T[:, 1])]
    return np.linalg.lstsq(Tr, yr, rcond=None)[0][0]
T0 = d[["recent", "old_only"]].values.astype(float)
b0 = coef(T0)
grp = d.GAZ_CNTY.values
idx = {g: np.where(grp == g)[0] for g in np.unique(grp)}
perm = []
for _ in range(1000):
    T = T0.copy()
    for g, ii in idx.items():
        T[ii] = T0[rng.permutation(ii)]
    perm.append(coef(T))
perm = np.array(perm)
RI = dict(b=float(b0), p=float((np.abs(perm) >= abs(b0)).mean()), reps=1000, perm_sd=float(perm.std()), perm_lo=float(np.quantile(perm, 0.025)), perm_hi=float(np.quantile(perm, 0.975)))
print("RI", RI)

# leave one county out
LOO = []
for c in sorted(S.GAZ_CNTY.unique()):
    r = fit(main_f, S[S.GAZ_CNTY != c], ["recent"], name=c)
    LOO.append(dict(county=c, b=r["coefs"]["recent"]["b"], lo=r["coefs"]["recent"]["lo"], hi=r["coefs"]["recent"]["hi"], p=r["coefs"]["recent"]["p"], n=r["n"]))
LOO = pd.DataFrame(LOO)
LOO.to_csv(f"{DATA}/models_leave_one_county_out.csv", index=False)
print("LOO range", LOO.b.min(), LOO.b.max(), (LOO.p < 0.05).sum())
# leave one region out
LOR = []
for g in sorted(S.REGION.unique()):
    r = fit(main_f, S[S.REGION != g], ["recent"], name=g)
    LOR.append(dict(region=g, b=r["coefs"]["recent"]["b"], lo=r["coefs"]["recent"]["lo"], hi=r["coefs"]["recent"]["hi"], p=r["coefs"]["recent"]["p"], n=r["n"]))
print(pd.DataFrame(LOR))

# matching-error simulation: move a share of linked Act places to a random parish within 5 km and rebuild exposure
lat0 = np.radians(52.5)
XY = np.c_[P.lon.values * 111.32 * np.cos(lat0), P.lat.values * 110.57]
from scipy.spatial import cKDTree
tree = cKDTree(XY)
pid_pos = {p: i for i, p in enumerate(P.PARISH_ID.values)}
nbrs = [np.array([j for j in tree.query_ball_point(XY[i], 5.0) if j != i]) for i in range(len(P))]
Lm = L.dropna(subset=["parish_id"])[["parish_id", "year"]].copy(); Lm["parish_id"] = Lm.parish_id.astype(int)
pid_arr = P.PARISH_ID.values
d_pids = d.PARISH_ID.values
SIM = {}
for share in (0.1, 0.25):
    bs = []
    for rep in range(200):
        ids = Lm.parish_id.values.copy()
        mv = rng.random(len(ids)) < share
        for k in np.where(mv)[0]:
            nb = nbrs[pid_pos[ids[k]]]
            if len(nb):
                ids[k] = pid_arr[rng.choice(nb)]
        yrs = Lm.year.values
        rec = set(ids[(yrs >= RECENT[0]) & (yrs <= RECENT[1])]); old = set(ids[yrs < RECENT[0]])
        T = np.c_[[1.0 if p in rec else 0.0 for p in d_pids], [1.0 if (p in old and p not in rec) else 0.0 for p in d_pids]]
        bs.append(coef(T))
    bs = np.array(bs)
    SIM[str(share)] = dict(mean=float(bs.mean()), lo=float(np.quantile(bs, 0.025)), hi=float(np.quantile(bs, 0.975)), reps=200)
print("SIM", SIM)

# descriptive riot rates by exposure
desc = {}
for k, q in (("recent", S0[S0.recent == 1]), ("old_only", S0[S0.old_only == 1]), ("never", S0[S0.never == 1]), ("future", S0[S0.future == 1]), ("all", S0)):
    desc[k] = dict(n=int(len(q)), riot=float(q.any_swing.mean()), incidents=int(q.SWING.sum()), machines=float(q.thresh1.mean()),
                   machine_attack=float(q.any_machine_attack.mean()), other=float(q.any_other.mean()))
# within-county descriptive: riot rate by exposure in the main Swing counties
byc = S0.groupby(["GAZ_CNTY"]).apply(lambda q: pd.Series(dict(n=len(q), recent=q.recent.sum(), riot_recent=q[q.recent == 1].any_swing.mean() if q.recent.sum() else np.nan,
                                                               riot_never=q[q.never == 1].any_swing.mean() if q.never.sum() else np.nan, riot=q.any_swing.mean(),
                                                               share_recent=q.recent.mean()))).reset_index()
byc.to_csv(f"{DATA}/county_summary.csv", index=False)
# validation against Gonner's district enclosure measure
g = S0.dropna(subset=["enclosures"])
val = dict(n=int(len(g)), r_any_act=float(np.corrcoef(g.enclosures, (g.n_acts > 0).astype(float))[0, 1]),
           r_recent=float(np.corrcoef(g.enclosures, g.recent)[0, 1]), spearman_district=None)
dist = g.groupby("MARKETTOWN").agg(gon=("enclosures", "mean"), act=("recent", "mean"), anyact=("n_acts", lambda v: (v > 0).mean()))
val["districts"] = int(len(dist)); val["spearman_district"] = float(stats.spearmanr(dist.gon, dist.anyact).correlation)

# link statistics
Wall = L[(L.year >= RECENT[0]) & (L.year <= RECENT[1])]
acts = Wall.groupby(["source", "year", "chapter"]).parish_id.apply(lambda v: v.notna().any())
link = dict(places_all=int(len(L)), places_window=int(len(Wall)), matched_window=int(Wall.parish_id.notna().sum()),
            matched_window_share=float(Wall.parish_id.notna().mean()), matched_all_share=float(L.parish_id.notna().mean()),
            acts_window=int(len(acts)), acts_window_any=int(acts.sum()), acts_window_any_share=float(acts.mean()),
            method_window={k: int(v) for k, v in Wall.method.value_counts().items()},
            method_all={k: int(v) for k, v in L.method.value_counts().items()},
            name_point_both=int((L.name_pid.notna() & L.spatial_pid.notna()).sum()),
            name_point_agree=float(L[L.name_pid.notna() & L.spatial_pid.notna()].agree.mean()),
            name_point_median_km=float(L.name_point_km.median()),
            in_sample_share=float(Wall[Wall.parish_id.notna()].in_sample.mean()),
            county_rate_min=float(rate["mean"].min()), county_rate_max=float(rate["mean"].max()), hi_counties=len(hi),
            fuzzy=int(L.fuzzy_pid.notna().sum()))
link["county_rates"] = {c: dict(rate=float(rate.loc[c, "mean"]), n=int(rate.loc[c, "size"])) for c in rate.index}
for k in M:
    M[k].pop("_model", None)
jsave(dict(area_median_km2=AREA, models=M, ri=RI, loo=LOO.to_dict("records"), lor=LOR, sim=SIM, desc=desc, validation=val, link=link,
           n=dict(sample=int(len(S0)), main=int(M["main"]["n"]), never=int(len(N0)))), f"{SCR}/models.json", keepdash=True)
print(desc); print(val); print({k: v for k, v in link.items() if k != "county_rates"})
