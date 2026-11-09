# enclosure-swing: working notes

Brief: /home/claude/work/new11/BRIEFS.md section 5, plus shared rules (new8, new9, new10 BRIEFS tops, newdata/BRIEF.md).
Format refs: /home/claude/studies/battle-moons, /home/claude/studies/sea-sunsets.
Inputs (read only): /home/claude/src6/captain-swing/data/{parishes,machines,unrest_pre1830,counties}.csv;
/home/claude/studies/enclosure/data/{enclosed_places,enclosure_acts,unmatched_places}.csv.
Scratch: /home/claude/scratch/enclosure-swing (delete at end).

## ANALYSIS PLAN (written before any outcome model was run; 2026)

Only non-outcome facts were looked at before writing this: column names, county names, sample size (9,674 parishes in
Caprettini and Voth's main sample, 54 counties/ridings), match-type counts in the enclosure gazetteer data.

### Hypothesis
H1 (Hobsbawm and Rude): parishes enclosed by parliamentary Act shortly before 1830 were more likely to see Swing
unrest in 1830 to 1831, holding constant the threshing-machine exposure and the other covariates of Caprettini and Voth.
H1b (mechanism, secondary): the association should be stronger for unrest other than machine breaking (arson, wage and
poor-relief riots, threatening letters) than for attacks on threshing machines.
H2 (timing): recent enclosure (Acts 1790 to 1830) should matter more than old enclosure (Acts before 1790).

### Unit, sample, outcome
- Unit: the 1851 parish of Caprettini and Voth (CV). Main sample: their main sample flag (sample == 1), N = 9,674.
- Main outcome: SWING1, any Swing incident in the parish (0/1). Secondary: SWING count; BREAKTHRESH (machine attacks)
  vs REST (other incidents), each as any-incident indicators.

### Treatment (exposure)
- Link each place named in an enclosure Act (private and local tables, enclosure and agreed enclosure Acts) to a CV parish.
  Matching rule (main): (1) normalised name of the place (or an alternative spelling) equals the normalised CV parish name,
  or the first or a component of a compound CV parish name, within the county named in the title (or the gazetteer
  county); (2) otherwise, if the place was located by the enclosure study's gazetteer, the CV parish whose centroid is
  nearest, provided it is within max(2 km, 1.2 x the parish's equivalent radius). Unique name match wins; ties broken
  by the gazetteer point if present, otherwise dropped.
- Main exposure: recent = parish named in at least one Act dated 1790 to 1830 (year = first year of the session; the
  1830 session ended before the riots began in late August 1830).
- Categories: recent (any Act 1790 to 1830), old only (Acts before 1790 only), never enclosed by Act before 1831 (reference).
- Window variants: Acts within 10 (1821 to 1830), 20 (1811 to 1830) and 40 (1791 to 1830) years.
- Spillover: number of other parishes with a recent Act whose centroids lie within 5 km and within 10 km (and an
  indicator for any), entered with own exposure.

### Main specification (pre-specified)
Linear probability model, SWING1 on recent enclosure and old-only enclosure (reference never), with CV controls
(log population density 1801, agricultural share 1801, log sex ratio, log distance to Elham, log distance to the
nearest newspaper town), threshing machine present (thresh1), cereal suitability (cer), heavy soil share (heavysh),
and county fixed effects (54). Standard errors clustered by county; also reported with clusters on 50 km grid cells.
Coefficient of interest: recent. Effect in percentage points with 95% CI; N reported.

### Alternatives and robustness (all planned)
1. Logit with the same controls and county FE (average marginal effect); Poisson for the SWING count.
2. Window variants (10, 20, 40 years); continuous years since last Act.
3. Without county FE but with region FE; with market-town FE (MARKETTOWN) instead of county FE.
4. Placebo/falsification: (a) future enclosure, parishes first named in an Act 1831 to 1870, among parishes not enclosed
   by Act before 1831, should show no association (unless future enclosure marks unobserved open-field character);
   (b) randomisation inference: permute recent status within county 1,000 times.
5. Leave-one-county-out: drop each county in turn; report range of the coefficient and whether its sign changes.
6. Matching sensitivity: name-only matches; spatial-only matches; matches where name and gazetteer point agree;
   restricting to counties where at least 80% of 1790 to 1830 Act places were matched; a simulation that reassigns
   a share (10%, 25%) of matches to a random neighbouring parish within 5 km.
7. Adding the CV district enclosure measure (Gonner) and the 1801 poor-rate sample controls where available (sub-samples).
8. Heterogeneity (labelled exploratory if not listed here): by machine presence; by region (South-East vs rest).

### What would count against H1
The recent-enclosure coefficient in the main LPM is not significantly positive and its 95% CI excludes effects of
about +3 percentage points (a fifth of the baseline riot rate of roughly 14%); or the future-enclosure placebo shows an
association of similar size; or the estimate is driven by one county (sign flips when it is dropped).
A null will be reported as the main result if that is what the planned specification shows.

### Design caveats (to say plainly)
Observational and correlational. Parliamentary enclosure was not random: it was concentrated in open-field Midland
parishes; much of the South-East (Kent, Sussex, Essex), where Swing began, was enclosed early by agreement, so
"never enclosed by Act" is not "open field". County FE compare parishes within counties. Matching misses places.

### Amendments to the linking rule (made after reading link cases by eye, still before any outcome model)
- A name match more than 10 km from the gazetteer point is not used (e.g. "Carlton", Yorkshire, 1800: the only CV parish
  called Carlton is 81 km from the gazetteer's Carlton near Drax); the point is used if it falls in a parish (26 places),
  otherwise the place is dropped (13).
- A unique CV name match for a place the gazetteer found several of in the county and could not place (Thornton,
  Yorkshire) is not used in the main link (55 places); kept in the "extended" sensitivity variant.
- Close spellings within the stated county (difflib ratio >= 0.85, clear winner) are used only in the "extended" variant;
  reading 25 of them by eye shows both rescues (Ulverstone, Beaminister) and errors (Horning -> Honing), so it is noisy.
- Audit: 100 random matched links for Acts 1790 to 1830 read by eye (data/link_audit.csv): 97 correct or a correct
  township-to-parish assignment; 3 doubtful (Tresham -> Alderley, Burwardsley -> Harthill, Thornton ER, the last now
  excluded by the ambiguous rule).

## Results of the planned specification (run after the plan and amendments above)
- Main LPM (N 9,674, 54 county FE, county clusters): recent +2.71 pp [0.16, 5.27], p 0.037; old-only +3.09 pp [0.47, 5.70].
  Baseline riot share 14.5%. H2 (recent > old) not supported: difference -0.37 pp, p 0.82.
- Logit AME +2.64; Poisson IRR 1.23; region FE +4.2; market-town FE +2.6; 50 km grid clusters p 0.026; RI p 0.003.
- Outcomes: machine attacks +0.93 (p 0.11); other unrest +2.44 (p 0.06).
- Windows: 10 y +5.3 (p 0.12), 20 y +3.2 (p 0.09), 40 y +2.7 (p 0.04); earlier enclosure about the same.
- Placebo future Acts (1831 to 1870, N 6,494 never-enclosed, 149 future): -4.5 pp (p 0.10). Not similar size.
- LOO county: 2.1 to 3.2 pp, all positive, 46 of 54 p < 0.05. Leave-one-region-out 1.5 to 3.7.
- Linking: name-only +1.7 (p 0.20), point-only +1.6 (p 0.18), agree-only +0.7 (p 0.56), extended +2.8, >= 80% match
  counties +1.2 (p 0.50); simulated relinking of 10%/25% of places to a neighbour: mean 2.6 / 2.4.
- Gonner subsample: recent +1.6 (p 0.18). Poor-rate subsample (N 1,251): -0.6.
- EXPLORATORY (after seeing the above): adding log parish area: recent -0.84 [-3.16, 1.47]; area deciles -0.3; logit
  with area -0.4; other unrest with area -1.0. Parishes enclosed by Act are larger (median 10.5 km2 vs 8.4 never).
  Reading: the planned positive association looks like a parish-size artefact (bigger parishes are both more likely to
  be named in an Act and more likely to record any incident). No robust evidence that recent enclosure predicted Swing.

## References verified (WebSearch/WebFetch, 2026)
All 44 references in the paper were checked for authors, title, year, venue, volume/pages (DOI where found):
Caprettini & Voth 2020 AER: Insights 2(3) 305-320 (RePEc; venue confirmed, not JEH); replication data openICPSR 117044 V1;
Aidt, Leon & Satchell 2022 J Politics 84(1) 209-225 (doi 10.1086/714784); Heldring, Robinson & Vollmer: still NBER WP 29772
(2022), no journal version found; Aidt & Franck 2015 Econometrica 83(2) 505-547; Randall 2009 IRSH 54(3) 419-427;
Shaw-Taylor 2001 JEH 61(3); Humphries 1990 JEH 50(1); Chambers 1953 EcHR 5(3); Clark & Clark 2001 JEH 61(4); Wordie 1983
EcHR 36(4) 483-505; Allen 1982 EJ 92(368); Bogart & Richardson 2011 JLE 54(2) 241-274; Cameron & Miller 2015; Abadie et al
2023; Conley 1999; Young 2019; books (Hobsbawm & Rude, Charlesworth 1979/1983, Neeson, Snell, Tate, Turner 1980/1984, Allen
1992, Griffin, Holland, Gonner, Hammond, Thompson 1963, Archer, Boyer, Tilly, Dunbabin, Stevenson, Mingay, Kain et al.,
Satchell et al. 2016). Charlesworth 1994 Rural History 5(1): pages not confirmed, cited without pages.
Dropped (not confirmed): Wells 1979 J Peasant Studies. Not stated: Swing sentence counts (search budget ran out).
Journal word limits (cover note) from EcHR notes 2026, SSH author instructions, AgHR submission page.

## Outputs
Paper release/paper/Hotham_Enclosure_and_Swing.pdf (20 pp, ~7,000 words before references + appendix), cover_note.md;
blog release/blog/post.html (5 figures); zenodo zip + metadata; reddit collage + GIF + post.md; index.html (QA in qa/).
Scratch /home/claude/scratch/enclosure-swing deleted at the end: rerun 01 to 04 to rebuild (about 1 minute).

## Independent review (referee and fact-check, 2026)

**Reproduction.** Re-ran 01 to 04 from the raw inputs into a separate scratch copy: results.json, act_parish_links.csv,
parishes_enclosure.csv, county_summary.csv and the leave-one-county-out file came out byte-identical. Numbers in the
paper, blog, page, README, Zenodo description, cover note, Reddit post, collage and GIF all come from results.json and agree.

**Framing.** The planned estimate (+2.71 pp, 95% CI 0.16 to 5.27, N 9,674) is reported as the main result everywhere, and the
log-area model (-0.84, -3.16 to 1.47) is labelled exploratory everywhere. Should area have been planned? The brief's "their
controls" are Caprettini and Voth's (log density, agricultural share, sex ratio, distances): no parish area or population.
Their density variable correlates only 0.23 with 1801 population per km2 of the 1851 parish (1,251 parishes with POP01),
so it is no proxy for size. A binary "any incident" outcome scales with unit size, so a referee would say area belonged in
the plan; the paper now says plainly that the adopted controls omit it. Population 1801 exists only for 1,251 parishes
(with it: recent -0.61, p 0.85), so area is the only feasible size control. Matching sensitivity does undermine the planned
estimate on its own (agree-only 0.69, name-only 1.72, >= 80% counties 1.24, none significant) even before size.
Reviewer checks (not in outputs): with area, link variants give -0.85 to -1.92; area-quintile x county FE -0.36;
OLS incident count with area -5.5 (p 0.09).

**Changes made.** Abstract cut to 185 words (EHR maximum 200, checked in the EcHR notes 2026 v2), ends "not robust evidence";
conclusion now says 2.7 (not "about 3") and flags the area models as exploratory; paper states that the adopted controls
contain no size measure; new exploratory result reported in the paper: future-enclosure placebo with log area is
-8.1 pp (-13.8 to -2.4, p 0.006), added to 03/04 and results.json (placebo_area), flagged as unexplained; "a count of incidents"
wording corrected (the outcome is an indicator). Charlesworth 1994 now cited as Rural History 5(1), 1 to 22 (start page 1 in the
Fordham Rural History index; pp. 1 to 22 in Sci. Rep. 2018 reference list; Cambridge page itself was not reachable).
Blog: "population" -> "population density"; "every version that allows for parish size" -> "the three versions in the
chart"; the closing claim that machines, winter and poor law "look like better guides" (not tested here) replaced with a
sourced, narrower sentence. Page: enclosure effects "may have spread" (was stated as fact). Reddit post: area check flagged as
added after the result, CI added. Collage: size row labelled "(exploratory)". Cover note: abstract now fits; EHR requires an
anonymised text (self-citations and map/repo links). Paper, Zenodo PDF, metadata and zip regenerated.

**References verified.** Journal items checked against RePEc/publisher/institutional pages: Caprettini and Voth 2020, Aidt,
Leon and Satchell 2022 (JoP 84(1) 209 to 225), Aidt and Franck 2015, Randall 2009 (419 to 427, doi ok), Shaw-Taylor 2001,
Humphries 1990, Chambers 1953, Clark and Clark 2001, Wordie 1983, Allen 1982, Bogart and Richardson 2011, Thompson 1971,
Cameron and Miller 2015, Abadie et al. 2023, Conley 1999, Young 2019. Heldring, Robinson and Vollmer: still NBER WP 29772
(no journal version listed). Books checked by catalogue/review: Hobsbawm and Rude, Holland (FACHRS, Milton Keynes 2005),
Griffin, Allen 1992, Archer, Boyer, Tilly, Stevenson 1979 (1700 to 1870 is the 1979 Longman title), Dunbabin, Gonner,
Neeson, Snell, Hammond, Turner 1980/1984, Tate, Kain et al., Mingay, Charlesworth 1979 (HGRS 1) and 1983, Satchell et al.
2016 (ReShare). No errors found beyond the Charlesworth pages.

**House rules.** Byline "Dr Tristan Hotham · Independent researcher · 2026"; no DSIT/DCMS/civil service; no dashes in visible
blog text; exact AI statement in page, blog, paper, README. Playwright (desktop 1280, phone 390, zoom 5 and 13): no console
errors, no horizontal scroll, full-screen button, layers panel with checkboxes, site-nav.js present, markers visible at
every zoom. Collage light, labels off land, full legend; GIF last frame shows 1830 with Swing rings.

**What a referee would still ask for.** (1) Pre-register or justify a size control and model counts with an exposure
offset (area or population) rather than an indicator. (2) Acreage or share of parish enclosed (Tate/Turner) instead of a
binary Act indicator. (3) Explain the negative size-adjusted future placebo (-8.1 pp): late-enclosed parishes differ (upland,
fen, waste enclosures), which questions any Act-based contrast. (4) Spatial (Conley) standard errors rather than 50 km grid
clusters only. (5) Labour-market or registration-district level analysis, since grievance mechanisms may work above the
parish. (6) Re-examine the threshing-machine association under size controls (falls 0.080 -> 0.037) and its IV.
(7) Population 1801 for all parishes (from the 1801 census) to separate area from people. (8) EHR uses footnote
references, not author-year: restyle on submission.
