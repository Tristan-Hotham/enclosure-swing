"""Step 9: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo), cover note (release/paper).
10.5281/zenodo.24091976, https://doi.org/10.5281/zenodo.24091976 and https://blog.tristanhotham.com/2026/10/31/enclosure-swing/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile, importlib.util
from PIL import Image
from common import *

spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "07_build_site.py"))
spec.loader.exec_module(importlib.util.module_from_spec(spec))          # shared fact checks (and rebuilds index.html)
R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Enclosure_and_Swing"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP, set(re.findall(r"\{\{([^|}]+)\}\}", post))
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
assert AI in post
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Did enclosure cause the Swing riots? A test on every parish",
        "slug": "enclosure-swing",
        "excerpt": f"Historians have long blamed enclosure for the Swing riots of 1830. I linked every enclosure Act to {R['n']['sample']:,} parishes and wrote the test down first: enclosed parishes rioted a little more, but the gap looks like parish size, not grievance.",
        "seo_description": "Did parishes enclosed by Act of Parliament riot more in the Swing rising of 1830? A pre-planned test on 9,674 English and Welsh parishes.",
        "tags": ["maps", "data visualisation", "history", "enclosure", "Swing riots", "rural protest", "economic history", "England"],
        "header_alt": "Title card on cream paper reading 'Enclosure and the Swing riots' in black and red, beside a map of England and Wales with red dots for parishes enclosed by Act in 1790 to 1830 and black rings for parishes with Swing unrest."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
assert f"{R['n']['sample']:,}" in meta["seo_description"]
jsave(meta, f"{REL}/blog/meta.json", indent=2)
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
OWN = ["parishes_enclosure.csv", "act_parish_links.csv", "link_audit.csv", "county_summary.csv", "models_leave_one_county_out.csv", "results.json"]
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(os.path.join(ROOT, "code"))):
        if fn.endswith((".pyc", ".png")) or fn == "__pycache__":
            continue
        z.write(os.path.join(ROOT, "code", fn), f"{SLUG}/code/{fn}")
    for fn in OWN:
        z.write(os.path.join(DATA, fn), f"{SLUG}/data/{fn}")
    for fn in ("README.md", "LICENSE", "NOTES.md"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), f"{SLUG}/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("$", "").replace("Rud\\'e", "Rudé")
assert "\\" not in ab, ab
zmeta = {"title": "Enclosure and the Swing Riots: A Pre-specified Parish-level Test of the Grievance Hypothesis, England and Wales, 1830 to 1831",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/enclosure-swing/}}.</p><p>Sources: Caprettini and Voth (2020) replication data (openICPSR 117044, CC BY 4.0); Chronological Tables of Private and Local Acts, legislation.gov.uk (Open Government Licence v3.0); Wikidata (CC0). Text, figures and derived data CC BY 4.0; code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["enclosure", "Swing riots", "collective action", "agrarian protest", "parliamentary enclosure", "record linkage", "pre-registration", "economic history", "England"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "10.3886/E117044V1", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "10.5281/zenodo.23873003", "relation": "isDerivedFrom", "resource_type": "publication"},
                                 {"identifier": "10.1257/aeri.20190385", "relation": "references", "resource_type": "publication"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2, keepdash=True)
# cover note
M = R["main"]
cover = f"""# Cover note: Enclosure and the Swing Riots

## Suggested journals

All three are subscription journals that publish accepted articles without an author charge (open access is optional and paid). Word limits from the journals' own author guidelines, checked in 2026.

1. **Economic History Review** (Economic History Society, Wiley). Articles should normally not exceed 10,000 words including footnotes but excluding tables, figures, bibliography and appendices; abstract up to 200 words, plus a two-sentence summary and a 280-character social media statement. The main text fits and the abstract is under 200 words. Submissions must be anonymised: the two self-citations (the enclosure and Captain Swing data studies) and the map and repository links must be made anonymous in the submitted text. The best fit: it publishes quantitative tests of classic debates in British economic and social history, including enclosure and the Swing riots.
2. **Social Science History** (Social Science History Association, Cambridge University Press). Main text including notes and references up to 12,000 words; abstract up to 250 words. Fits as it stands, with the appendix as online supplementary material. Suits the pre-registered design and the methodological point about unit size in event data.
3. **Agricultural History Review** (British Agricultural History Society). Usual maximum about 9,000 to 11,000 words including footnotes, with tables and figures counted (a full-page figure counts as 720 words); articles up to 15,000 words are considered. The paper would need shortening (move the appendix tables and two figures to supplementary material). Suits the rural-history readership most directly.

## Summary for a cover letter (about 150 words)

Hobsbawm and Rudé's claim that parliamentary enclosure helped to cause the Swing riots of 1830 has never been tested parish by parish. This paper links the {R['n']['places_all']:,} places named in every enclosure Act to the parishes of Caprettini and Voth's Swing data, publishes and audits the linkage, and estimates a model specified in advance on {R['n']['sample']:,} parishes. The planned model finds that recently enclosed parishes were {M['recent']['b']:.1f} percentage points more likely to riot, but parishes enclosed before 1790 show the same gap, stricter linking weakens it, and, in exploratory models, it disappears once parish area is held constant ({R['s']['x_area']['b']:.1f} points, 95% CI {R['s']['x_area']['lo']:.1f} to {R['s']['x_area']['hi']:.1f}). The paper therefore offers a careful, transparent null result on a central claim of the history of rural protest, and a general warning that parish size confounds studies of whether any event occurred in a unit.
"""
for bad in ("\u2014", "\u2013", "--"):
    assert bad not in cover
open(f"{REL}/paper/cover_note.md", "w", encoding="utf-8").write(cover)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
