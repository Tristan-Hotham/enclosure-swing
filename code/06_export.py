"""Step 6: page data. data/page.json: every CV parish (main sample and the rest) with Swing incidents, machines,
enclosure exposure, and the Acts linked to it; data/england_wales.geojson outline (from the enclosure study)."""
import pandas as pd, numpy as np, shutil
from common import *
import warnings; warnings.filterwarnings("ignore")

P = pd.read_pickle(f"{SCR}/panel.pkl")
L = pd.read_pickle(f"{SCR}/links.pkl")
Lm = L.dropna(subset=["parish_id"]).sort_values(["year", "chapter"])
acts, pa = [], {}
for r in Lm.itertuples():
    acts.append([int(r.year), r.title.strip(), r.place, {"name": "n", "name_part": "n", "name_variant": "n", "name_variant_part": "n"}.get(r.method, "p"), "L" if r.source == "local" else "P"])
    pa.setdefault(int(r.parish_id), []).append(len(acts) - 1)
rows = []
for r in P.itertuples():
    cat = 2 if r.recent else (1 if r.old_only else (3 if r.future else 0))
    rows.append([round(r.lat, 4), round(r.lon, 4), r.PARISH.title(), r.GAZ_CNTY.title(), int(r.SWING), int(r.BREAKTHRESH), int(r.REST),
                 int(r.thresh), cat, int(r.first_act) if r.first_act == r.first_act else 0, int(r.sample), pa.get(int(r.PARISH_ID), [])])
jsave(dict(cols=["lat", "lon", "name", "county", "swing", "attacks", "other", "machines", "cat", "first", "sample", "acts"],
           parishes=rows, acts=acts), f"{DATA}/page.json", keepdash=True)
shutil.copy(f"{ENC}/england_wales.geojson", f"{DATA}/england_wales.geojson")
print("page.json", os.path.getsize(f"{DATA}/page.json") // 1024, "KB", len(rows), len(acts))
