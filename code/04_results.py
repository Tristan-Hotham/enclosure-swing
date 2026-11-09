"""Step 4: every number used anywhere (page, paper, blog, collage, post, README) into data/results.json.
Effects are stored in percentage points (pp) rounded to 2 decimals; shares in per cent."""
import pandas as pd, numpy as np
from common import *
import warnings; warnings.filterwarnings("ignore")

MJ = jload(f"{SCR}/models.json")
P = pd.read_pickle(f"{SCR}/panel.pkl")
L = pd.read_pickle(f"{SCR}/links.pkl")
A = pd.read_csv(f"{ENC}/enclosure_acts.csv")
S = P[P["sample"] == 1]
M = MJ["models"]
r2 = lambda x, d=2: round(float(x), d)


def eff(k, x):
    c = M[k]["coefs"][x]
    use_ame = "ame" in c
    b, lo, hi = (c["ame"], c["ame_lo"], c["ame_hi"]) if use_ame else (c["b"], c["lo"], c["hi"])
    out = dict(b=r2(100 * b), lo=r2(100 * lo), hi=r2(100 * hi), p=r2(c["p"], 3), n=M[k]["n"], clusters=M[k]["clusters"],
               ymean=r2(100 * M[k]["ymean"], 1))
    if "irr" in c:
        out.update(irr=r2(c["irr"]), irr_lo=r2(c["irr_lo"]), irr_hi=r2(c["irr_hi"]))
    return out


R = {}
win = L[(L.year >= RECENT[0]) & (L.year <= RECENT[1])]
acts_win = A[(A.year >= RECENT[0]) & (A.year <= RECENT[1])]
lk = MJ["link"]
R["n"] = dict(parishes_all=int(len(P)), sample=int(len(S)), main=M["main"]["n"], counties=M["main"]["clusters"],
              recent=int(S.recent.sum()), old_only=int(S.old_only.sum()), never=int(S.never.sum()), future=int(S.future.sum()),
              recent_pc=r2(100 * S.recent.mean(), 1), anyact_pc=r2(100 * (1 - S.never.mean()), 1),
              acts_all=int(len(A)), acts_window=int(len(acts_win)), places_all=lk["places_all"], places_window=lk["places_window"],
              matched_window=lk["matched_window"], matched_window_pc=r2(100 * lk["matched_window_share"], 1),
              matched_all_pc=r2(100 * lk["matched_all_share"], 1),
              acts_window_linked=lk["acts_window_any"], acts_window_linked_pc=r2(100 * lk["acts_window_any_share"], 1),
              name_window=int(win.method.str.startswith("name").sum()), spatial_window=int(win.method.str.startswith("spatial").sum()),
              unmatched_window=int((~win.method.isin(["name", "name_part", "name_variant", "name_variant_part", "spatial", "spatial_conflict"])).sum()),
              name_point_both=lk["name_point_both"], name_point_agree_pc=r2(100 * lk["name_point_agree"], 1),
              name_point_median_km=r2(lk["name_point_median_km"], 2), in_sample_pc=r2(100 * lk["in_sample_share"], 1),
              hi_counties=lk["hi_counties"], fuzzy=lk["fuzzy"], audit_n=100, audit_ok=97,
              conflict=int(lk["method_all"].get("spatial_conflict", 0) + lk["method_all"].get("conflict", 0)),
              ambiguous=int(lk["method_all"].get("ambiguous_name", 0)),
              incidents=int(S.SWING.sum()), riot_parishes=int(S.any_swing.sum()), riot_pc=r2(100 * S.any_swing.mean(), 1),
              machine_attack_parishes=int(S.any_machine_attack.sum()), other_parishes=int(S.any_other.sum()),
              machines=int(S.thresh1.sum()),
              first_act=int(A.year.min()), last_act=int(A.year.max()))
R["n"]["acts_window_named"] = int(len(win.groupby(["source", "year", "chapter"])))
R["n"]["area_ratio_95_5"] = r2(S.AREA_m2.quantile(.95) / S.AREA_m2.quantile(.05), 1)
R["n"]["acts_peak_year"] = int(A.groupby("year").size().idxmax())
R["n"]["acts_1793_1815"] = int(A.year.between(1793, 1815).sum())
D = MJ["desc"]
R["desc"] = {k: dict(n=v["n"], riot=r2(100 * v["riot"], 1), incidents=v["incidents"], machines=r2(100 * v["machines"], 1),
                     machine_attack=r2(100 * v["machine_attack"], 1), other=r2(100 * v["other"], 1)) for k, v in D.items()}
R["desc"]["gap_raw"] = r2(R["desc"]["recent"]["riot"] - R["desc"]["never"]["riot"], 1)
R["main"] = dict(recent=eff("main", "recent"), old=eff("main", "old_only"), r2=r2(M["main"]["r2"], 3),
                 h2_diff=r2(100 * M["main"]["h2_diff"]), h2_lo=r2(100 * M["main"]["h2_lo"]), h2_hi=r2(100 * M["main"]["h2_hi"]), h2_p=r2(M["main"]["h2_p"], 2))
R["main"]["rel_pc"] = r2(100 * R["main"]["recent"]["b"] / R["main"]["recent"]["ymean"], 0)
R["anyact"] = eff("anyact", "I(recent + old_only)")
# every specification for the coefficient table and plot: (key, label, group)
SPEC = [("main", "Main: LPM, county FE, controls", "planned"), ("raw", "No controls, no fixed effects", "planned"),
        ("ctrl_nofe", "Controls, no fixed effects", "planned"), ("fe_noctrl", "County FE, no controls", "planned"),
        ("region_fe", "Region FE instead of county FE", "planned"), ("market_fe", "Market-town FE instead of county FE", "planned"),
        ("grid_se", "Standard errors clustered on 50 km cells", "planned"), ("logit", "Logit (average marginal effect)", "planned"),
        ("spill", "With neighbouring enclosure (5 and 10 km)", "planned"), ("preriots", "With pre-1830 unrest", "planned"),
        ("gonner_base", "Subsample with Gonner district data", "planned"), ("gonner", "Same, adding Gonner district enclosure", "planned"),
        ("poor_base", "Subsample with 1803 poor relief", "planned"), ("poor", "Same, adding poor relief per head", "planned"),
        ("link_name", "Linking: name matches only", "linking"), ("link_spatial", "Linking: gazetteer point only", "linking"),
        ("link_agree", "Linking: name and point agree", "linking"), ("link_ext", "Linking: extended (close spellings)", "linking"),
        ("hi_match", "Counties with at least 80% of places linked", "linking"),
        ("x_clean", "Parishes whose exposure all rules agree on", "exploratory"),
        ("x_area", "Adding log parish area", "exploratory"), ("x_area_dec", "Adding parish area deciles", "exploratory"),
        ("x_area_logit", "Logit adding log parish area (AME)", "exploratory")]
R["spec"] = [dict(key=k, label=l, group=g, **eff(k, "recent"), old=eff(k, "old_only")["b"]) for k, l, g in SPEC]
R["s"] = {k: eff(k, "recent") for k, _, _ in SPEC}
R["s"]["machine"] = eff("machine", "recent"); R["s"]["other"] = eff("other", "recent")
R["s"]["machine_old"] = eff("machine", "old_only"); R["s"]["other_old"] = eff("other", "old_only")
R["s"]["poisson"] = eff("poisson", "recent"); R["s"]["poisson_old"] = eff("poisson", "old_only")
R["s"]["x_area_poisson"] = eff("x_area_poisson", "recent"); R["s"]["x_area_other"] = eff("x_area_other", "recent")
R["s"]["count_ols"] = eff("count_ols", "recent")
R["s"]["x_area_logarea"] = eff("x_area", "log_area")
R["s"]["x_area_old"] = eff("x_area", "old_only")
R["s"]["spill5"] = eff("spill", "spill5_any"); R["s"]["spill10"] = eff("spill", "spill10_any")
R["s"]["gonner_enc"] = eff("gonner", "enclosures"); R["s"]["poor_pc"] = eff("poor", "log_poor_pc")
R["s"]["het_machine"] = eff("het_machine", "recent_x_machine"); R["s"]["het_se"] = eff("het_se", "recent_x_se")
R["s"]["x_clean_dropped"] = M["x_clean"]["dropped"]
R["windows"] = {w: dict(win=eff(w, w), earlier=eff(w, f"earlier_{w}")) for w in ("w10", "w20", "w40")}
R["windows"]["w10_area"] = eff("x_area_w10", "w10")
R["since"] = {k: eff("since", k) for k in ("ys_0_9", "ys_10_19", "ys_20_39", "ys_40p")}
R["placebo"] = eff("placebo_future", "future")
R["placebo_area"] = eff("x_area_placebo", "future")
R["ri"] = dict(p=r2(MJ["ri"]["p"], 3), reps=MJ["ri"]["reps"], lo=r2(100 * MJ["ri"]["perm_lo"]), hi=r2(100 * MJ["ri"]["perm_hi"]))
lo = pd.DataFrame(MJ["loo"])
R["loo"] = dict(min=r2(100 * lo.b.min()), max=r2(100 * lo.b.max()), n=int(len(lo)), n_pos=int((lo.b > 0).sum()), n_sig=int((lo.p < 0.05).sum()),
                min_county=lo.loc[lo.b.idxmin(), "county"].title(), max_county=lo.loc[lo.b.idxmax(), "county"].title())
R["lor"] = {d["region"]: dict(b=r2(100 * d["b"]), lo=r2(100 * d["lo"]), hi=r2(100 * d["hi"]), p=r2(d["p"], 3), n=d["n"]) for d in MJ["lor"]}
R["lor_range"] = dict(min=min(v["b"] for v in R["lor"].values()), max=max(v["b"] for v in R["lor"].values()))
R["sim"] = {("s10" if k == "0.1" else "s25"): dict(mean=r2(100 * v["mean"]), lo=r2(100 * v["lo"]), hi=r2(100 * v["hi"]), reps=v["reps"]) for k, v in MJ["sim"].items()}
R["area"] = {k: r2(v, 1) for k, v in MJ["area_median_km2"].items()}
R["validation"] = dict(n=MJ["validation"]["n"], r=r2(MJ["validation"]["r_any_act"], 2), districts=MJ["validation"]["districts"],
                       rho=r2(MJ["validation"]["spearman_district"], 2))
# riot share by parish-area quintile, enclosed by Act before 1831 or not (for the size figure and the blog)
S2 = S.assign(area=S.AREA_m2 / 1e6, enc=(S.never == 0).astype(int))
S2["aq"] = pd.qcut(S2.area, 5, labels=False)
aq = S2.groupby(["aq", "enc"]).any_swing.agg(["mean", "size"]).reset_index()
R["area_q"] = dict(edges=[r2(x, 1) for x in S2.area.quantile([0, .2, .4, .6, .8, 1]).values],
                   enc=[r2(100 * aq[(aq.aq == q) & (aq.enc == 1)]["mean"].iloc[0], 1) for q in range(5)],
                   not_enc=[r2(100 * aq[(aq.aq == q) & (aq.enc == 0)]["mean"].iloc[0], 1) for q in range(5)],
                   n_enc=[int(aq[(aq.aq == q) & (aq.enc == 1)]["size"].iloc[0]) for q in range(5)],
                   n_not=[int(aq[(aq.aq == q) & (aq.enc == 0)]["size"].iloc[0]) for q in range(5)],
                   enc_share=[r2(100 * S2[S2.aq == q].enc.mean(), 1) for q in range(5)])
R["area_q"]["top_bottom_riot"] = [r2(100 * S2[S2.aq == 0].any_swing.mean(), 1), r2(100 * S2[S2.aq == 4].any_swing.mean(), 1)]
# riot share by decade of the last Act before 1831
dec = S.assign(dec=(S.last_pre // 10 * 10)).dropna(subset=["dec"])
dd = dec.groupby("dec").any_swing.agg(["mean", "size"])
dd = dd[dd["size"] >= 30]
R["decade"] = dict(dec=[int(x) for x in dd.index], riot=[r2(100 * x, 1) for x in dd["mean"]], n=[int(x) for x in dd["size"]])
# county summary for the page and collage
cs = pd.read_csv(f"{DATA}/county_summary.csv")
R["counties_top"] = [dict(county=r.GAZ_CNTY.title(), n=int(r.n), riot=r2(100 * r.riot, 1), recent_pc=r2(100 * r.share_recent, 1)) for r in cs.sort_values("riot", ascending=False).head(8).itertuples()]
R["full"] = {k: dict(n=M[k]["n"], r2=r2(M[k].get("r2", float("nan")), 3), coefs={x: dict(b=r2(v["b"], 4), se=r2(v["se"], 4), p=r2(v["p"], 3)) for x, v in M[k]["all"].items()})
             for k in ("main", "x_area", "machine", "other", "placebo_future", "spill", "fe_noctrl", "raw")}
R["cty"] = {r.GAZ_CNTY: dict(recent_pc=r2(100 * r.share_recent, 1), riot=r2(100 * r.riot, 1)) for r in cs.itertuples() if r.GAZ_CNTY in ("KENT", "SUSSEX", "NORFOLK")}
R["T"] = dict(se_main=r2(100 * M["main"]["coefs"]["recent"]["se"], 2), mde=r2(2.8 * 100 * M["main"]["coefs"]["recent"]["se"], 1),
              implied_parishes=r2(R["main"]["recent"]["b"] / 100 * R["n"]["recent"], 0),
              implied_share=r2(100 * R["main"]["recent"]["b"] / 100 * R["n"]["recent"] / R["n"]["riot_parishes"], 0),
              implied_parishes_area_hi=r2(R["s"]["x_area"]["hi"] / 100 * R["n"]["recent"], 0))
R["F"] = dict(  # facts quoted in words, checked here
    recent_bigger_raw=R["desc"]["recent"]["riot"] > R["desc"]["never"]["riot"],
    main_sig=R["main"]["recent"]["p"] < 0.05, old_equal=R["main"]["h2_p"] > 0.5,
    area_kills=R["s"]["x_area"]["hi"] < 3 and R["s"]["x_area"]["b"] < 0.5,
    placebo_negative=R["placebo"]["b"] < 0, all_loo_pos=R["loo"]["n_pos"] == R["loo"]["n"])
for k, v in R["F"].items():
    assert v, k
jsave(R, f"{DATA}/results.json", indent=1, keepdash=True)
print(json.dumps({k: R[k] for k in ("n", "main", "placebo", "ri", "loo", "area", "area_q", "decade", "validation")}, indent=0)[:4000])
