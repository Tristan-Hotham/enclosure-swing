"""Shared paths, constants and helpers for the enclosure-swing study ("Enclosure and the Swing riots").

Inputs (read in place, never modified):
  SWING/parishes.csv          Caprettini and Voth (2020) parish data for 1851 England and Wales, as tidied in the
                              captain-swing study (one row per parish: county, name, centroid, Swing incidents, threshing
                              machines, 1801 census covariates, distances, soils, Gonner district enclosure, poor rates).
  SWING/machines.csv, unrest_pre1830.csv, counties.csv  dated machine records, pre-1830 unrest, county totals.
  ENC/enclosed_places.csv     every place named in a parliamentary enclosure Act (private and local tables of
                              legislation.gov.uk), with year, county in the title and the gazetteer match (Wikidata).
  ENC/enclosure_acts.csv      one row per Act.
Intermediates go to SCR, outside the repo.
"""
import json, gzip, os, re, math, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWING = os.environ.get("ES_SWING", "/home/claude/src6/captain-swing/data")
ENC = os.environ.get("ES_ENC", "/home/claude/studies/enclosure/data")
GEO = os.environ.get("ES_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("ES_FONTS", "/home/claude/ref/fonts")
SCR = os.environ.get("ES_SCRATCH", "/home/claude/scratch/enclosure-swing")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
for d in (DATA, IMG, SCR):
    os.makedirs(d, exist_ok=True)

SLUG = "enclosure-swing"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"
SEED = 20261109
RECENT = (1790, 1830)      # main exposure window (inclusive)
FUTURE = (1831, 1870)      # placebo window

# controls of Caprettini and Voth, plus machines and soils
CTRL = ["log_density", "agri_share", "log_sex_ratio", "log_distel", "log_distnews", "thresh1", "cer", "heavysh"]
CTRL_NAMES = {"log_density": "Log population density, 1801", "agri_share": "Agricultural share of occupations, 1801",
              "log_sex_ratio": "Log sex ratio, 1801", "log_distel": "Log distance to Elham (km)",
              "log_distnews": "Log distance to newspaper town (km)", "thresh1": "Threshing machine recorded",
              "cer": "Cereal suitability", "heavysh": "Heavy soil share"}

# enclosure-table county names -> CV county names
CMAP = {"Caernarfonshire": ["CARNARVONSHIRE"], "County Durham": ["DURHAM"], "Glamorgan": ["GLAMORGANSHIRE"],
        "Yorkshire": ["YORKSHIRE, EAST RIDING", "YORKSHIRE, NORTH RIDING", "YORKSHIRE, WEST RIDING"],
        "Hampshire": ["HAMPSHIRE", "ISLE OF WIGHT"]}


def cv_counties(name):
    if not isinstance(name, str) or not name.strip():
        return []
    out = []
    for c in name.split(";"):
        c = c.strip()
        out += CMAP.get(c, [c.upper()])
    return out


def key(s):
    """Name key: accents, punctuation and bracketed alternatives dropped, lower case, saint -> st, upon/super -> on,
    juxta/near -> next, hyphens as spaces, 'the' dropped, final possessive s dropped."""
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\[.*?\]|\(.*?\)", " ", s)
    s = s.replace("&", " and ").replace("-", " ")
    s = re.sub(r"[^a-z ]", " ", s.replace("'s ", "s ").replace("'", ""))
    w = s.split()
    rep = {"saint": "st", "s": "st", "upon": "on", "super": "on", "juxta": "next", "near": "next", "magna": "great",
           "parva": "little", "cum": "with"}
    w = [rep.get(x, x) for x in w if x not in ("the",)]
    return " ".join(w)


LANDWORDS = {"common", "commons", "moor", "moors", "marsh", "marshes", "fen", "fens", "heath", "heaths", "down", "downs",
             "field", "fields", "waste", "wastes", "lands", "land", "meadow", "meadows", "pasture", "pastures", "green",
             "leys", "forest", "chase", "hill", "hills", "warren", "carr", "carrs", "ings", "level", "levels", "open",
             "lordship", "township", "manor", "parish", "hamlet", "liberty", "precinct", "chapelry"}


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def nonan(v):
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    if isinstance(v, list):
        return [nonan(x) for x in v]
    if isinstance(v, tuple):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {str(k): nonan(x) for k, x in v.items()}
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None, keepdash=False):
    obj = nonan(obj) if keepdash else dash(nonan(obj))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def pval(p):
    p = float(p)
    if p < 0.001: return "below 0.001"
    if p < 0.01: return f"{p:.3f}"
    return f"{p:.2f}"


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f0": return f"{round(float(v))}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "f3": return f"{float(v):.3f}"
    if f == "p": return pval(v)
    if f == "s1": return f"{float(v):+.1f}"
    raise ValueError(f)


def haversine(lat1, lon1, lat2, lon2):
    import numpy as np
    r = np.radians
    a = np.sin(r(lat2 - lat1) / 2) ** 2 + np.cos(r(lat1)) * np.cos(r(lat2)) * np.sin(r(lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))
