# Enclosure and the Swing riots

Did English and Welsh parishes enclosed by Act of Parliament shortly before 1830 riot more in the Swing rising of 1830 to 1831? A pre-specified parish-level test that links every parliamentary enclosure Act to the parish data of Caprettini and Voth (2020).

Interactive page: https://maps.tristanhotham.com/enclosure-swing/
Paper: https://doi.org/10.5281/zenodo.24091976
Blog post: https://blog.tristanhotham.com/2026/10/31/enclosure-swing/

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

## Headline results

- The analysis plan (hypotheses, main model, checks, and what would count against the idea) was written in `NOTES.md` before any model of the riots was run.
- Linkage: 79.0% of the 3,322 places named in enclosure Acts of 1790 to 1830 were linked to a parish; name and map point agree on the parish in 90.4% of cases where both exist; a hand audit of 100 links found 97 right.
- Planned model (9,674 parishes, 54 county fixed effects, Caprettini and Voth's controls plus threshing machines and soils, county-clustered errors): parishes named in an Act of 1790 to 1830 were 2.7 percentage points (95% CI 0.2 to 5.3) more likely to see a Swing incident, against a mean of 14.5%.
- No timing gradient: parishes enclosed only before 1790 show 3.1 percentage points (95% CI 0.5 to 5.7); recent minus old -0.37 points (p = 0.82).
- Placebo: parishes first enclosed in 1831 to 1870 show -4.5 percentage points (95% CI -9.9 to 0.8). Leaving out each county: 2.07 to 3.23, all positive.
- Fragile to linking: name and point agree only, 0.69; name only, 1.72; counties at least 80% linked, 1.24 (none significant).
- Exploratory (added after the planned results): parishes enclosed by Act were larger (median 10.5 km² against 8.4 km²), and larger parishes were more likely to record any incident (8% in the smallest fifth, 22% in the largest). Holding log parish area constant, the recent-enclosure gap is -0.8 percentage points (95% CI -3.2 to 1.5).
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

Unit: the 1851 parish of Caprettini and Voth's replication data (main sample 9,674). Outcome: at least one Swing incident. Exposure: parish named in an enclosure Act of 1790 to 1830 (recent), only before 1790 (old only), or not before 1831 (reference). Linking: name within the county named in the title (or a component of a compound parish name, or simple variants), else the gazetteer point if it falls within the parish; name matches more than 10 km from the point and ambiguous names set aside. Model: linear probability model with county fixed effects and county-clustered standard errors; logit, Poisson, region and market-town effects, 50 km grid clusters, windows, spillovers, placebo with later Acts, randomisation inference, leave-one-county-out and five linking variants. Caveats: observational; Acts only (no acreage, no enclosure by agreement); 21% of places in 1790 to 1830 not linked; the parish-size models are exploratory.

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

Hotham, T. (2026) Enclosure and the Swing riots: a pre-specified parish-level test of the grievance hypothesis, England and Wales, 1830 to 1831. Zenodo. https://doi.org/10.5281/zenodo.24091976

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
