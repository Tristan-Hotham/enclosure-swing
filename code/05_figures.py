"""Step 5: figures for the paper (release/paper/f_*.png, 300 dpi), the blog (release/blog/b_*.png), the page (img/*.jpg)
and the social card header.png. Light parchment style; palette checked with the dataviz validator
(recent #A3261B, old-only #C8922E, future #2F6DB0; gold always labelled)."""
import warnings; warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np, pandas as pd
from PIL import Image
from shapely.geometry import shape
from common import *

for f in ("FrauncesVar.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
SERIF = "Source Serif 4"; DISP = "Fraunces"; MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": SERIF, "font.size": 12, "axes.edgecolor": "#6E604E", "axes.labelcolor": "#2B2119",
                     "xtick.color": "#6E604E", "ytick.color": "#6E604E", "axes.unicode_minus": False, "svg.fonttype": "none"})
PAPER, INK, MUT, GRID = "#FBF6E9", "#2B2119", "#6E604E", "#E6DCC4"
LAND, COAST = "#F1E7CF", "#8C7B5E"
REC, OLD, FUT, NEV, RIOT = "#A3261B", "#C8922E", "#2F6DB0", "#B9AE98", "#2B2119"
R = jload(f"{DATA}/results.json")
P = pd.read_pickle(f"{SCR}/panel.pkl")
S = P[P["sample"] == 1]
EW = shape(jload(f"{ENC}/england_wales.geojson")["features"][0]["geometry"])
HC = [shape(f["geometry"]) for f in jload(f"{ENC}/historic_counties.geojson")["features"]]
PO = os.path.join(ROOT, "release", "paper"); BL = os.path.join(ROOT, "release", "blog")
for d in (PO, BL): os.makedirs(d, exist_ok=True)
K = math.cos(math.radians(52.5))


def poly(ax, g, **kw):
    gs = g.geoms if hasattr(g, "geoms") else [g]
    for p in gs:
        if p.geom_type != "Polygon": continue
        v, c = [], []
        for ring in [p.exterior] + list(p.interiors):
            cs = np.asarray(ring.coords); cs = np.c_[cs[:, 0] * K, cs[:, 1]]
            v += cs.tolist(); c += [Path.MOVETO] + [Path.LINETO] * (len(cs) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(v, c), **kw))


def base(ax):
    ax.set_facecolor(PAPER)
    poly(ax, EW, fc=LAND, ec=COAST, lw=0.6, zorder=1)
    for g in HC:
        poly(ax, g.intersection(EW), fc="none", ec="#D2C3A0", lw=0.35, zorder=2)
    ax.set_xlim(-5.8 * K, 1.85 * K); ax.set_ylim(49.9, 55.85); ax.set_aspect("equal"); ax.axis("off")


def save(fig, name, paper=True, blog=True, img=False, dpi=300):
    if paper: fig.savefig(f"{PO}/f_{name}.png", dpi=dpi, facecolor=fig.get_facecolor())
    if blog: fig.savefig(f"{BL}/b_{name}.png", dpi=1800 / fig.get_figwidth(), facecolor=fig.get_facecolor())
    if img:
        fig.savefig(f"{SCR}/tmp.png", dpi=110, facecolor=fig.get_facecolor())
        Image.open(f"{SCR}/tmp.png").convert("RGB").save(f"{IMG}/{name}.jpg", quality=86); os.remove(f"{SCR}/tmp.png")
    plt.close(fig)


def axstyle(ax):
    ax.set_facecolor(PAPER)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(MUT); ax.spines["bottom"].set_color(MUT)
    ax.tick_params(labelsize=10.5)
    for t in ax.get_xticklabels() + ax.get_yticklabels(): t.set_fontfamily(MONO)


# ---------- 1. the two maps
fig, axs = plt.subplots(1, 2, figsize=(12, 7.6), facecolor=PAPER)
x, y = S.lon.values * K, S.lat.values
for ax in axs: base(ax)
a = axs[0]
a.scatter(x[S.never == 1], y[S.never == 1], s=1.2, c="#CDBF9F", lw=0, zorder=3)
a.scatter(x[S.old_only == 1], y[S.old_only == 1], s=4, c=OLD, lw=0, zorder=4)
a.scatter(x[S.recent == 1], y[S.recent == 1], s=4, c=REC, lw=0, zorder=5)
a.set_title("Parishes named in an enclosure Act", fontfamily=DISP, fontsize=16, fontweight="bold", color=INK, loc="left")
for lab, col, n in ((f"Act 1790 to 1830", REC, R["n"]["recent"]), ("Acts before 1790 only", OLD, R["n"]["old_only"]), ("No Act before 1831", "#CDBF9F", R["n"]["never"])):
    a.scatter([], [], s=40, c=col, label=f"{lab} ({n:,})")
a.legend(loc="upper right", bbox_to_anchor=(1.02, 0.99), frameon=False, prop={"family": MONO, "size": 9.5})
b = axs[1]
b.scatter(x[S.any_swing == 0], y[S.any_swing == 0], s=1.2, c="#CDBF9F", lw=0, zorder=3)
q = S[S.any_swing == 1]
b.scatter(q.lon * K, q.lat, s=3 + 5 * np.sqrt(q.SWING), c=RIOT, lw=0, alpha=.8, zorder=4)
b.set_title("Parishes with Swing unrest, 1830 to 1831", fontfamily=DISP, fontsize=16, fontweight="bold", color=INK, loc="left")
for nn in (1, 5, 20):
    b.scatter([], [], s=3 + 5 * np.sqrt(nn), c=RIOT, label=f"{nn} incident{'s' if nn > 1 else ''}")
b.legend(loc="upper right", bbox_to_anchor=(1.02, 0.99), frameon=False, prop={"family": MONO, "size": 9.5}, title=f"{R['n']['riot_parishes']:,} parishes", title_fontproperties={"family": MONO, "size": 9.5})
fig.text(0.01, 0.01, "Parish centroids of the main sample of Caprettini and Voth (2020), 9,674 parishes. Acts: Chronological Tables of Private and Local Acts.", fontfamily=MONO, fontsize=8.5, color=MUT)
fig.subplots_adjust(left=0.01, right=0.99, top=0.94, bottom=0.04, wspace=0.02)
save(fig, "map", img=True)

# ---------- 2. coefficient plot
sp = R["spec"]
fig, ax = plt.subplots(figsize=(10, 8.2), facecolor=PAPER); axstyle(ax)
ys = []; yy = 0; gl = {"planned": "Planned specifications", "linking": "How Acts are linked to parishes", "exploratory": "Exploratory checks (added after the planned results)"}
last = None; ticks = []; labs = []
for r in sp:
    if r["group"] != last:
        yy -= 0.9; ax.text(-9.4, yy, gl[r["group"]], fontfamily=MONO, fontsize=10, color=REC, fontweight="medium", va="center"); yy -= 1; last = r["group"]
    col = INK if r["group"] == "planned" else (FUT if r["group"] == "linking" else REC)
    ax.plot([r["lo"], r["hi"]], [yy, yy], color=col, lw=2, solid_capstyle="round")
    ax.scatter([r["b"]], [yy], s=46, color=col, zorder=3, edgecolor=PAPER, lw=1.5)
    ticks.append(yy); labs.append(r["label"]); yy -= 1
ax.axvline(0, color=MUT, lw=1); ax.axvspan(-0.1, 0.1, color=GRID, zorder=0)
ax.set_yticks(ticks); ax.set_yticklabels(labs, fontfamily=SERIF, fontsize=10.5)
ax.set_xlim(-9.5, 11); ax.set_ylim(yy, 0.3)
ax.set_xlabel("Difference in the chance of any Swing incident: parish enclosed by Act 1790 to 1830\nagainst no Act before 1831, percentage points (95% confidence interval)", fontsize=10.5)
ax.grid(axis="x", color=GRID, lw=.8); ax.set_axisbelow(True)
ax.tick_params(axis="y", length=0)
fig.tight_layout(); save(fig, "coef", img=True)

# ---------- 3. parish size: riot share and enclosure share by area quintile
aq = R["area_q"]; e = aq["edges"]
lab = [f"{e[i]:.0f} to {e[i+1]:.0f}" for i in range(5)]; lab[0] = f"under {e[1]:.0f}"; lab[-1] = f"over {e[4]:.0f}"
riot = [round(100 * S[pd.qcut(S.AREA_m2, 5, labels=False) == i].any_swing.mean(), 1) for i in range(5)]
fig, axs = plt.subplots(1, 2, figsize=(11, 4.6), facecolor=PAPER)
for ax, vals, col, t in ((axs[0], riot, RIOT, "Parishes with any Swing incident (%)"), (axs[1], aq["enc_share"], REC, "Parishes named in an enclosure Act before 1831 (%)")):
    axstyle(ax)
    ax.bar(range(5), vals, color=col, width=0.72)
    for i, v in enumerate(vals): ax.text(i, v + 0.6, f"{v:.0f}%", ha="center", fontfamily=MONO, fontsize=10, color=INK)
    ax.set_xticks(range(5)); ax.set_xticklabels(lab, fontsize=9.5); ax.set_xlabel("Parish area, km² (fifths of parishes)", fontsize=10.5)
    ax.set_title(t, fontfamily=DISP, fontsize=13.5, fontweight="bold", color=INK, loc="left"); ax.set_ylim(0, max(vals) * 1.18); ax.set_yticks([])
    ax.spines["left"].set_visible(False)
fig.tight_layout(); save(fig, "size", img=True)

# ---------- 4. timing: riot share by decade of last Act before 1831
dd = R["decade"]
fig, ax = plt.subplots(figsize=(10, 4.8), facecolor=PAPER); axstyle(ax)
cols = [REC if d >= 1790 else OLD for d in dd["dec"]]
ax.bar(range(len(dd["dec"])), dd["riot"], color=cols, width=0.72)
for i, (v, n) in enumerate(zip(dd["riot"], dd["n"])):
    ax.text(i, v + 0.5, f"{v:.0f}%", ha="center", fontfamily=MONO, fontsize=10, color=INK, bbox=dict(fc=PAPER, ec="none", pad=1))
    ax.text(i, 0.7, f"n={n}", ha="center", fontfamily=MONO, fontsize=8.5, color="#FFFFFF")
nv = R["desc"]["never"]["riot"]
ax.axhline(nv, color=MUT, lw=1.4, ls=(0, (4, 3)))
ax.text(-0.45, max(dd["riot"]) * 1.1, f"Dashed line: parishes with no Act before 1831, {nv:.0f}%", ha="left", fontfamily=MONO, fontsize=9.5, color=MUT)
ax.set_xticks(range(len(dd["dec"]))); ax.set_xticklabels([f"{d}s" for d in dd["dec"]], fontsize=10)
ax.set_xlabel("Decade of the parish's last enclosure Act before 1831 (raw shares, no controls)", fontsize=10.5)
ax.set_ylabel("Parishes with any Swing incident (%)", fontsize=10.5); ax.set_ylim(0, max(dd["riot"]) * 1.2)
ax.set_title("Swing unrest by when the parish was enclosed", fontfamily=DISP, fontsize=14, fontweight="bold", color=INK, loc="left")
fig.tight_layout(); save(fig, "timing", img=True)

# ---------- 5. leave one county out
lo = pd.read_csv(f"{DATA}/models_leave_one_county_out.csv").sort_values("b")
fig, ax = plt.subplots(figsize=(10, 4.6), facecolor=PAPER); axstyle(ax)
xs = np.arange(len(lo))
ax.vlines(xs, 100 * lo.lo, 100 * lo.hi, color="#BFAF8E", lw=1.6)
ax.scatter(xs, 100 * lo.b, s=16, color=REC, zorder=3)
ax.axhline(R["main"]["recent"]["b"], color=INK, lw=1, ls=(0, (4, 3))); ax.axhline(0, color=MUT, lw=.8)
ax.text(1, R["main"]["recent"]["b"] + 0.25, f"All counties: {R['main']['recent']['b']:.1f}", fontfamily=MONO, fontsize=9.5, color=INK)
ax.set_xticks([]); ax.set_xlabel(f"The main model re-estimated {len(lo)} times, each time leaving out one county (sorted)", fontsize=10.5)
ax.set_ylabel("Recent enclosure, pp (95% CI)", fontsize=10.5)
for i in (0, len(lo) - 1):
    ax.text(xs[i], 100 * lo.iloc[i].hi + 0.3, lo.iloc[i].county.title().replace("Yorkshire, ", ""), ha="center", fontfamily=MONO, fontsize=8.5, color=MUT)
fig.tight_layout(); save(fig, "loo", img=False)

# ---------- header 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=PAPER)
ax = fig.add_axes([0.52, 0.02, 0.47, 0.96]); base(ax)
ax.scatter(x[S.never == 1], y[S.never == 1], s=1.0, c="#D3C6A6", lw=0)
ax.scatter(x[S.recent == 1], y[S.recent == 1], s=3, c=REC, lw=0)
ax.scatter(q.lon * K, q.lat, s=2 + 3 * np.sqrt(q.SWING), facecolor="none", edgecolor=RIOT, lw=.6)
fig.text(0.05, 0.80, "Enclosure and", fontfamily=DISP, fontsize=40, fontweight="bold", color=INK)
fig.text(0.05, 0.68, "the Swing riots", fontfamily=DISP, fontsize=40, fontweight="bold", color=REC)
fig.text(0.05, 0.55, f"Did parishes fenced by Act in 1790 to 1830\nriot more in 1830? A test on {R['n']['sample']:,} parishes.", fontfamily=SERIF, fontsize=17, color=INK, va="top", linespacing=1.4)
lg = fig.add_axes([0, 0, 1, 1], facecolor="none"); lg.set_xlim(0, 1); lg.set_ylim(0, 1); lg.axis("off")
lg.scatter([0.058], [0.315], s=70, c=REC); lg.scatter([0.058], [0.255], s=70, facecolor="none", edgecolor=RIOT, lw=1.4)
fig.text(0.075, 0.30, "enclosed by Act 1790 to 1830", fontfamily=MONO, fontsize=12.5, color=INK)
fig.text(0.075, 0.24, "Swing unrest, 1830 to 1831", fontfamily=MONO, fontsize=12.5, color=INK)
fig.text(0.05, 0.07, "Dr Tristan Hotham · maps.tristanhotham.com/enclosure-swing", fontfamily=MONO, fontsize=11, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=PAPER); plt.close(fig)
print(Image.open(os.path.join(ROOT, "header.png")).size, sorted(os.listdir(PO)), sorted(os.listdir(BL)))
