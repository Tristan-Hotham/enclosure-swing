"""Step 10: README.md, LICENSE and reddit/post.md, every number from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
N, M, S = R["n"], R["main"], R["s"]
f1 = lambda e: f"{e['b']:.1f} percentage points (95% CI {e['lo']:.1f} to {e['hi']:.1f})"
readme = f"""# Enclosure and the Swing riots

Did English and Welsh parishes enclosed by Act of Parliament shortly before 1830 riot more in the Swing rising of 1830 to 1831? A pre-specified parish-level test that links every parliamentary enclosure Act to the parish data of Caprettini and Voth (2020).

Interactive page: {PAGE}
Paper: {{https://doi.org/10.5281/zenodo.24091976}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/enclosure-swing/}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

## Headline results

- The analysis plan (hypotheses, main model, checks, and what would count against the idea) was written in `NOTES.md` before any model of the riots was run.
- Linkage: {N['matched_window_pc']:.1f}% of the {N['places_window']:,} places named in enclosure Acts of 1790 to 1830 were linked to a parish; name and map point agree on the parish in {N['name_point_agree_pc']:.1f}% of cases where both exist; a hand audit of 100 links found {N['audit_ok']} right.
- Planned model ({N['sample']:,} parishes, {N['counties']} county fixed effects, Caprettini and Voth's controls plus threshing machines and soils, county-clustered errors): parishes named in an Act of 1790 to 1830 were {f1(M['recent'])} more likely to see a Swing incident, against a mean of {M['recent']['ymean']:.1f}%.
- No timing gradient: parishes enclosed only before 1790 show {f1(M['old'])}; recent minus old {M['h2_diff']:.2f} points (p = {M['h2_p']:.2f}).
- Placebo: parishes first enclosed in 1831 to 1870 show {f1(R['placebo'])}. Leaving out each county: {R['loo']['min']:.2f} to {R['loo']['max']:.2f}, all positive.
- Fragile to linking: name and point agree only, {S['link_agree']['b']:.2f}; name only, {S['link_name']['b']:.2f}; counties at least 80% linked, {S['hi_match']['b']:.2f} (none significant).
- Exploratory (added after the planned results): parishes enclosed by Act were larger (median {R['area']['recent']:.1f} km² against {R['area']['never']:.1f} km²), and larger parishes were more likely to record any incident ({R['area_q']['top_bottom_riot'][0]:.0f}% in the smallest fifth, {R['area_q']['top_bottom_riot'][1]:.0f}% in the largest). Holding log parish area constant, the recent-enclosure gap is {f1(S['x_area'])}.
- Reading: no parish-level support for the claim that recent parliamentary enclosure predicted where Swing broke out. Observational data: correlation, not cause.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js`, `img/` | The interactive page (MapLibre, OpenFreeMap base map), built by `code/07_build_site.py`. |
| `header.png` | Social card, 1200 x 630. |
| `data/parishes_enclosure.csv` | Every 1851 parish of the Caprettini and Voth data: county, name, region, main-sample flag, centroid, Swing incidents (all, machine attacks, other), machines, number of linked Acts, first Act, last Act before 1831, exposure (recent, old only, never, windows, future), neighbours with recent Acts within 5 and 10 km, and exposure under the alternative linking rules. |
| `data/act_parish_links.csv` | Every place named in an enclosure Act with the parish it was linked to and how (name, name part, variant, map point, conflict, ambiguous, unmatched), plus the name-only, point-only and close-spelling candidates. |
| `data/link_audit.csv` | The 100 links checked by hand, with judgements. |
| `data/county_summary.csv`, `data/models_leave_one_county_out.csv` | County figures; the leave-one-county-out estimates. |
| `data/results.json` | Every number used in the page, paper, blog, collage, post and this README. |
| `data/page.json`, `data/england_wales.geojson` | Page data. |
| `code/` | Numbered scripts (below) and the page, paper and blog templates. |
| `release/paper/` | Paper (LaTeX source and PDF, figures) and `cover_note.md` (suggested journals, summary). |
| `release/blog/` | Blog post (WordPress blocks), figures, meta. |
| `release/zenodo/` | Paper PDF, data and code zip, metadata. |
| `reddit/` | Collage, looping GIF, `collage.py`, `post.md`. |
| `NOTES.md` | Working notes, including the analysis plan written before the models were run. |
| `qa/` | Page screenshots at desktop and phone widths. |

## Method in brief

Unit: the 1851 parish of Caprettini and Voth's replication data (main sample {N['sample']:,}). Outcome: at least one Swing incident. Exposure: parish named in an enclosure Act of 1790 to 1830 (recent), only before 1790 (old only), or not before 1831 (reference). Linking: name within the county named in the title (or a component of a compound parish name, or simple variants), else the gazetteer point if it falls within the parish; name matches more than 10 km from the point and ambiguous names set aside. Model: linear probability model with county fixed effects and county-clustered standard errors; logit, Poisson, region and market-town effects, 50 km grid clusters, windows, spillovers, placebo with later Acts, randomisation inference, leave-one-county-out and five linking variants. Caveats: observational; Acts only (no acreage, no enclosure by agreement); {100 - N['matched_window_pc']:.0f}% of places in 1790 to 1830 not linked; the parish-size models are exploratory.

## How to rerun

Python 3 with pandas, numpy, scipy, statsmodels, matplotlib, Pillow and shapely; xelatex and pdftotext for the paper; node with Playwright for `code/qa.js`. Inputs are read in place (paths in `code/common.py`): the captain-swing study's `data/` folder (Caprettini and Voth's data) and the enclosure study's `data/` folder. Intermediates go to `ES_SCRATCH` (default `/home/claude/scratch/enclosure-swing`).

```
python3 code/01_link.py        # link Act places to parishes
python3 code/02_exposure.py    # parish exposure variables
python3 code/03_models.py      # every model (planned and exploratory)
python3 code/04_results.py     # results.json
python3 code/05_figures.py     # figures and header
python3 code/06_export.py      # page data
python3 code/07_build_site.py  # index.html
python3 code/08_paper.py       # paper (DOI=10.5281/zenodo.N to fill the DOI)
python3 reddit/collage.py      # collage and GIF
python3 code/10_readme.py      # README, LICENSE, Reddit post
python3 code/09_release.py     # blog post, Zenodo files, cover note
```

## Sources and licences

- Caprettini, B. and Voth, H.-J. (2020) Rage against the machines: labor-saving technology and unrest in industrializing England. *American Economic Review: Insights* 2(3), 305 to 320. https://doi.org/10.1257/aeri.20190385. Replication data: openICPSR 117044 V1, https://doi.org/10.3886/E117044V1 (CC BY 4.0). Swing incidents from Holland, M. (ed.) (2005) *Swing Unmasked*.
- Chronological Table of Private and Personal Acts and Chronological Table of Local Acts, legislation.gov.uk. Contains public sector information licensed under the Open Government Licence v3.0. Compiled in Hotham, T. (2026) Fencing the commons, Zenodo, https://doi.org/10.5281/zenodo.23873003.
- Wikidata place coordinates (CC0). Base map: OpenFreeMap, OpenMapTiles, OpenStreetMap contributors (ODbL).

Text, figures and derived data: CC BY 4.0 (please also credit Caprettini and Voth). Code: MIT (see `LICENSE`).

## Citation

Hotham, T. (2026) Enclosure and the Swing riots: a pre-specified parish-level test of the grievance hypothesis, England and Wales, 1830 to 1831. Zenodo. {{https://doi.org/10.5281/zenodo.24091976}}

{AI}
"""
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in readme.replace("```", "").replace("|---|---|", ""), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """MIT License (code)

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Text, figures and derived data: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.
The parish data derive from Caprettini and Voth's replication package (CC BY 4.0); the enclosure Acts from legislation.gov.uk (Open Government Licence v3.0); place coordinates from Wikidata (CC0).
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
post = f"""**Title:** [OC] Did enclosure cause the Swing riots of 1830? Parishes Parliament had enclosed rioted {M['recent']['b']:.1f} points more often, but parishes enclosed decades earlier did too, and the gap vanishes once you allow for parish size

**Body:**

In 1830 farm labourers across southern England smashed threshing machines and burned ricks in the "Captain Swing" riots. Historians have long blamed enclosure, the fencing of open fields and commons by Act of Parliament, for the anger behind them.

I linked every enclosure Act to {N['sample']:,} parishes of England and Wales ({N['matched_window_pc']:.0f}% of places named in Acts of 1790 to 1830 matched) and wrote the test down before running it.

- Planned test: parishes enclosed by Act in 1790 to 1830 were {M['recent']['b']:.1f} percentage points more likely to see a Swing incident (base rate {M['recent']['ymean']:.0f}%).
- But parishes enclosed only before 1790 show the same gap ({M['old']['b']:.1f}).
- Bigger parishes were both more often enclosed ({R['area_q']['enc_share'][0]:.0f}% to {R['area_q']['enc_share'][4]:.0f}%) and more likely to riot ({R['area_q']['top_bottom_riot'][0]:.0f}% to {R['area_q']['top_bottom_riot'][1]:.0f}%). Allowing for parish area (a check I added after seeing the planned result), the gap is {S['x_area']['b']:.1f} points ({S['x_area']['lo']:.1f} to {S['x_area']['hi']:.1f}). So no robust sign that recent enclosure drove the riots.

Interactive map: {PAGE}

**Source comment:** Data: Caprettini and Voth (2020) parish data and replication package (Swing incidents from Holland, Swing Unmasked, 2005); enclosure Acts from the Chronological Tables of Private and Local Acts (legislation.gov.uk, OGL). Tools: Python (pandas, statsmodels, matplotlib). Paper with all the checks: {{https://doi.org/10.5281/zenodo.24091976}}
"""
for bad in ("—", "–", "--"):
    assert bad not in post, bad
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
print("README", len(readme.split()), "words")
