"""Step 8: the paper. Fills code/paper_template.tex from data/results.json, adds booktabs tables, compiles with xelatex.
Output: release/paper/Hotham_Enclosure_and_Swing.pdf and .tex beside the f_*.png figures.
The DOI stays a placeholder (https://doi.org/10.5281/zenodo.24091976 printed) unless DOI is set: DOI=10.5281/zenodo.N python3 code/08_paper.py"""
import subprocess
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Enclosure_and_Swing"
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "f0": return f"{float(v):.0f}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "f3": return f"{float(v):.3f}"
    if f == "s1": return f"{float(v):+.1f}"
    return tex(str(v))


def stars(p): return "^{***}" if p < 0.001 else "^{**}" if p < 0.01 else "^{*}" if p < 0.05 else ""
def cell(e): return f"${e['b']:.2f}{stars(e['p'])}$"
def ci(e): return f"[{e['lo']:.2f}, {e['hi']:.2f}]"

N = R["n"]; D = R["desc"]
rows = ""
for k, lab in (("recent", "Act 1790 to 1830"), ("old_only", "Acts before 1790 only"), ("never", "No Act before 1831"), ("future", "of which first Act 1831 to 1870"), ("all", "All parishes")):
    d = D[k]; rows += f"{lab} & {d['n']:,} & {d['riot']:.1f} & {d['machine_attack']:.1f} & {d['other']:.1f} & {d['incidents']:,} & {d['machines']:.1f}\\\\\n"
TD = ("\\begin{table}[tbp]\\centering\\small\\caption{Parishes of the main sample by enclosure exposure.}\\label{tab:desc}"
      "\\resizebox{\\textwidth}{!}{\\begin{tabular}{lrrrrrr}\\toprule Exposure & Parishes & Any Swing (\\%) & Machine attack (\\%) & Other unrest (\\%) & Incidents & Machine (\\%)\\\\\\midrule\n" + rows +
      "\\bottomrule\\end{tabular}}\\par\\vspace{4pt}\\parbox{\\textwidth}{\\footnotesize Shares of parishes with at least one incident of each kind and with a recorded threshing machine. Raw figures, no controls.}\\end{table}")
mw = R["n"]
L = jload(f"{DATA}/results.json")
lk = jload(f"{SCR}/models.json")["link"]["method_window"]
lab = {"name": "Name, within county", "name_part": "Name, part of compound parish name", "name_variant": "Name variant (X in Y, land words)",
       "spatial": "Gazetteer point in parish", "spatial_conflict": "Point used (name match over 10 km away)", "conflict": "Not linked: name and point conflict",
       "ambiguous_name": "Not linked: ambiguous name", "unmatched": "Not linked: no name or point"}
tot = sum(lk.values())
rows = "".join(f"{lab.get(k, k)} & {v:,} & {100*v/tot:.1f}\\\\\n" for k, v in sorted(lk.items(), key=lambda x: -x[1]))
TL = ("\\begin{table}[tbp]\\centering\\small\\caption{How the places named in enclosure Acts of 1790 to 1830 were linked to parishes.}\\label{tab:link}"
      "\\begin{tabular}{lrr}\\toprule Method & Places & Share (\\%)\\\\\\midrule\n" + rows + f"\\midrule All & {tot:,} & 100.0\\\\\\bottomrule\\end{{tabular}}\\end{{table}}")
S = R["s"]; M = R["main"]
cols = [("(1)", S["raw"], R["full"]["raw"]["coefs"]["old_only"]), ("(2)", S["fe_noctrl"], R["full"]["fe_noctrl"]["coefs"]["old_only"]), ("(3)", S["main"], R["full"]["main"]["coefs"]["old_only"]),
        ("(4)", S["logit"], None), ("(5)", S["machine"], R["full"]["machine"]["coefs"]["old_only"]), ("(6)", S["other"], R["full"]["other"]["coefs"]["old_only"]), ("(7)", S["x_area"], R["full"]["x_area"]["coefs"]["old_only"])]
def oc(o, c):
    if o is None: return "$" + f"{next(s for s in R['spec'] if s['key'] == 'logit')['old']:.2f}" + "$"
    return f"${100*o['b']:.2f}{stars(o['p'])}$"
TM = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Enclosure by Act and Swing unrest: main estimates (percentage points).}\\label{tab:main}"
      "\\resizebox{\\textwidth}{!}{\\begin{tabular}{lrrrrrrr}\\toprule & (1) & (2) & (3) & (4) & (5) & (6) & (7)\\\\"
      " & Raw & County FE & \\textbf{Main} & Logit AME & Machine attack & Other unrest & + log area\\\\\\midrule\n"
      "Recent (Act 1790 to 1830) & " + " & ".join(cell(c) for _, c, _ in cols) + "\\\\\n"
      " & " + " & ".join(ci(c) for _, c, _ in cols) + "\\\\\n"
      "Old only (Acts before 1790) & " + " & ".join(oc(o, c) for _, c, o in cols) + "\\\\\n"
      "Controls & no & no & yes & yes & yes & yes & yes\\\\\n"
      "County fixed effects & no & yes & yes & yes & yes & yes & yes\\\\\n"
      "Outcome mean (\\%) & " + " & ".join(f"{c['ymean']:.1f}" for _, c, _ in cols) + "\\\\\n"
      "Parishes & " + " & ".join(f"{c['n']:,}" for _, c, _ in cols) + "\\\\\n"
      "\\bottomrule\\end{tabular}}\\par\\vspace{4pt}\\parbox{\\textwidth}{\\footnotesize Linear probability models (logit average marginal effects in column 4) of at least one Swing incident (columns 1 to 4 and 7), machine attack (5) or other incident (6). Reference: no enclosure Act before 1831. Controls: log population density, agricultural share and log sex ratio in 1801, log distances to Elham and to the nearest newspaper town, threshing machine recorded, cereal suitability, heavy-soil share. Standard errors clustered by county (54 clusters); 95\\% confidence intervals in brackets. Column 7 is exploratory. $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.}\\end{table}")
W = R["windows"]; SI = R["since"]
rows = "".join(f"{lab} & {cell(W[w]['win'])} & {ci(W[w]['win'])} & {cell(W[w]['earlier'])} & {ci(W[w]['earlier'])}\\\\\n" for w, lab in (("w10", "Act 1821 to 1830"), ("w20", "Act 1811 to 1830"), ("w40", "Act 1791 to 1830")))
rows2 = "".join(f"{lab} & {cell(SI[k])} & {ci(SI[k])} & & \\\\\n" for k, lab in (("ys_0_9", "Last Act 0 to 9 years before 1830"), ("ys_10_19", "10 to 19 years"), ("ys_20_39", "20 to 39 years"), ("ys_40p", "40 years or more")))
TT = ("\\begin{table}[tbp]\\centering\\small\\caption{Timing: windows of enclosure before 1830 (percentage points).}\\label{tab:timing}"
      "\\begin{tabular}{lrrrr}\\toprule Exposure & In window & 95\\% CI & Earlier Acts only & 95\\% CI\\\\\\midrule\n" + rows + "\\midrule\n" + rows2 +
      f"\\bottomrule\\end{{tabular}}\\par\\vspace{{4pt}}\\parbox{{\\textwidth}}{{\\footnotesize Each window row is one model with an indicator for an Act within the window and one for Acts only before it; the last four rows are one model. Controls and county fixed effects as in the main model; N = {N['main']:,}. $^{{*}}p<0.05$, $^{{**}}p<0.01$.}}\\end{{table}}")
rows = ""
last = None
gl = {"planned": "Planned", "linking": "Linking rules", "exploratory": "Exploratory"}
for sp in R["spec"]:
    if sp["group"] != last:
        rows += f"\\multicolumn{{5}}{{l}}{{\\textit{{{gl[sp['group']]}}}}}\\\\\n"; last = sp["group"]
    rows += f"{tex(sp['label'])} & {sp['b']:.2f} & [{sp['lo']:.2f}, {sp['hi']:.2f}] & {sp['p']:.3f} & {sp['n']:,}\\\\\n"
pl = R["placebo"]
rows += f"\\multicolumn{{5}}{{l}}{{\\textit{{Placebo}}}}\\\\\nFirst Act 1831 to 1870 (parishes with no earlier Act) & {pl['b']:.2f} & [{pl['lo']:.2f}, {pl['hi']:.2f}] & {pl['p']:.3f} & {pl['n']:,}\\\\\n"
TR = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Every specification: coefficient on recent enclosure (percentage points).}\\label{tab:rob}"
      "\\begin{tabular}{p{7.6cm}rrrr}\\toprule Specification & Coef. & 95\\% CI & $p$ & N\\\\\\midrule\n" + rows +
      "\\bottomrule\\end{tabular}\\par\\vspace{4pt}\\parbox{\\textwidth}{\\footnotesize Standard errors clustered by county except where stated. Subsample rows use the parishes with Gonner's district estimate or with 1803 poor rates.}\\end{table}")
NM = {"Intercept": "Constant", "recent": "Recent enclosure", "old_only": "Old-only enclosure", "log_area": "Log parish area (km\\textsuperscript{2})", **{k: tex(v) for k, v in CTRL_NAMES.items()}}
F1, F2 = R["full"]["main"], R["full"]["x_area"]
rows = ""
for k in ["recent", "old_only", "log_area"] + CTRL + ["Intercept"]:
    a = F1["coefs"].get(k); b = F2["coefs"].get(k)
    f = lambda c: (f"${c['b']:.4f}{stars(c['p'])}$", f"({c['se']:.4f})") if c else ("", "")
    a1, a2 = f(a); b1, b2 = f(b)
    rows += f"{NM[k]} & {a1} & {b1}\\\\\n & {a2} & {b2}\\\\\n"
TF = ("\\begin{table}[tbp]\\centering\\small\\caption{Full coefficients of the main model and the exploratory model with parish area (probability scale).}\\label{tab:full}"
      "\\begin{tabular}{lrr}\\toprule & Main & With log area\\\\\\midrule\n" + rows +
      f"\\midrule County fixed effects & yes & yes\\\\ $R^2$ & {F1['r2']:.3f} & {F2['r2']:.3f}\\\\ Parishes & {F1['n']:,} & {F2['n']:,}\\\\\\bottomrule\\end{{tabular}}"
      "\\par\\vspace{4pt}\\parbox{\\textwidth}{\\footnotesize OLS; standard errors clustered by county in parentheses. Log area 1851 parish, km\\textsuperscript{2}. $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.}\\end{table}")
rows = "".join(f"{tex(g)} & {v['b']:.2f} & [{v['lo']:.2f}, {v['hi']:.2f}] & {v['n']:,}\\\\\n" for g, v in R["lor"].items())
TO = ("\\begin{table}[tbp]\\centering\\small\\caption{Leave one region out: coefficient on recent enclosure (percentage points) when the named region is dropped.}\\label{tab:lor}"
      "\\begin{tabular}{lrrr}\\toprule Region left out & Coef. & 95\\% CI & N\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{AI}}", AI).replace("{{PAGE}}", PAGE).replace("{{REPO}}", REPO)
for k, v in (("TABLE_DESC", TD), ("TABLE_LINK", TL), ("TABLE_MAIN", TM), ("TABLE_TIMING", TT), ("TABLE_ROB", TR), ("TABLE_FULL", TF), ("TABLE_LOR", TO)):
    t = t.replace("{{" + k + "}}", v)
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")
t = t.replace("https://doi.org/10.5281/zenodo.24091976", f"\\url{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t, [l for l in t.splitlines() if "--" in l or "{{" in l][:3]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
body = txt.split("References")[0]
print("paper", r.returncode, len(txt.split()), "words in all;", len(body.split()), "before references;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–"))
