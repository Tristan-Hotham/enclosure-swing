"""Reddit collage (2400 px wide, light background) and a looping GIF of enclosure Acts spreading, 1750 to 1830, with the
Swing parishes of 1830 appearing at the end. Numbers from data/results.json. Run from the study root or anywhere."""
import os, sys, math, warnings
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from PIL import Image
from common import *
import importlib.util
spec = importlib.util.spec_from_file_location("fs", os.path.join(ROOT, "code", "05_figures.py"))
# reuse the base map and palette without re-drawing the figures: exec only the definitions
src = open(os.path.join(ROOT, "code", "05_figures.py"), encoding="utf-8").read().split("# ---------- 1. the two maps")[0]
exec(src)
R = jload(f"{DATA}/results.json")
x, y = S.lon.values * K, S.lat.values

fig = plt.figure(figsize=(16, 10.4), dpi=150, facecolor=PAPER)
fig.text(0.03, 0.945, "Did enclosure cause the Swing riots of 1830?", fontfamily=DISP, fontweight="bold", fontsize=30, color=INK)
fig.text(0.03, 0.905, f"Parishes that Parliament enclosed in 1790 to 1830 rioted a little more, but so did parishes enclosed long before, and the gap vanishes once parish size is held constant.",
         fontfamily=SERIF, fontsize=15, color=INK)
ax = fig.add_axes([0.0, 0.06, 0.47, 0.70]); base(ax)
ax.scatter(x[S.never == 1], y[S.never == 1], s=1.4, c="#CDBF9F", lw=0, zorder=3)
ax.scatter(x[S.old_only == 1], y[S.old_only == 1], s=4.5, c=OLD, lw=0, zorder=4)
ax.scatter(x[S.recent == 1], y[S.recent == 1], s=4.5, c=REC, lw=0, zorder=5)
q = S[S.any_swing == 1]
ax.scatter(q.lon * K, q.lat, s=5 + 6 * np.sqrt(q.SWING), facecolor="none", edgecolor=RIOT, lw=.7, zorder=6)
ax.set_xlim(-6.2 * K, 2.0 * K)
for lab, kw in ((f"Enclosure Act 1790 to 1830 ({R['n']['recent']:,} parishes)", dict(s=60, c=REC)), (f"Enclosure Acts before 1790 only ({R['n']['old_only']:,})", dict(s=60, c=OLD)),
                (f"No enclosure Act before 1831 ({R['n']['never']:,})", dict(s=60, c="#CDBF9F")), (f"Swing unrest 1830 to 1831 ({R['n']['riot_parishes']:,}), ring sized by incidents", dict(s=60, facecolor="none", edgecolor=RIOT, lw=1.4))):
    ax.scatter([], [], label=lab, **kw)
fig.legend(*ax.get_legend_handles_labels(), loc="upper left", bbox_to_anchor=(0.025, 0.885), frameon=False, prop={"family": MONO, "size": 10.5}, handletextpad=0.4)
# right: size bars
aq = R["area_q"]; e = aq["edges"]
lab = ["under\n5", "5 to\n7", "7 to\n11", "11 to\n19", "over\n19"]
riot = []
for i in range(5):
    riot.append(round(100 * S[pd.qcut(S.AREA_m2, 5, labels=False) == i].any_swing.mean(), 1))
a1 = fig.add_axes([0.53, 0.55, 0.2, 0.28]); a2 = fig.add_axes([0.77, 0.55, 0.2, 0.28])
for a, vals, col, t in ((a1, riot, RIOT, "Any Swing incident"), (a2, aq["enc_share"], REC, "Named in an enclosure Act")):
    a.set_facecolor(PAPER); a.bar(range(5), vals, color=col, width=.72)
    for i, v in enumerate(vals): a.text(i, v + 0.8, f"{v:.0f}%", ha="center", fontfamily=MONO, fontsize=11, color=INK)
    a.set_xticks(range(5)); a.set_xticklabels(lab, fontfamily=MONO, fontsize=9.5, color=MUT, rotation=0)
    a.set_yticks([]); [a.spines[s_].set_visible(False) for s_ in ("top", "right", "left")]
    a.set_title(t + " (%)", fontfamily=DISP, fontweight="bold", fontsize=14, color=INK, loc="left"); a.set_ylim(0, max(vals) * 1.2)
    a.set_xlabel("Parish area, km²", fontfamily=MONO, fontsize=10, color=MUT)
fig.text(0.53, 0.875, "Bigger parishes: more unrest, and more often enclosed", fontfamily=SERIF, fontsize=15, fontweight="semibold", color=INK)
# right bottom: the gap three ways
b = fig.add_axes([0.53, 0.12, 0.44, 0.28]); b.set_facecolor(PAPER)
rows = [("Planned test (within county, with controls)", R["main"]["recent"], INK), ("Same, enclosed only before 1790", R["main"]["old"], OLD),
        ("Stricter matching (name and point agree)", R["s"]["link_agree"], FUT), ("Holding parish size constant (exploratory)", R["s"]["x_area"], REC)]
for i, (l, e_, c) in enumerate(rows):
    yv = len(rows) - 1 - i
    b.plot([0, 0], [yv - 0.22, yv + 0.18], color=MUT, lw=1)
    b.plot([e_["lo"], e_["hi"]], [yv, yv], color=c, lw=3, solid_capstyle="round"); b.scatter([e_["b"]], [yv], s=90, color=c, zorder=3, edgecolor=PAPER, lw=2)
    b.text(-3.9, yv + 0.28, l, fontfamily=SERIF, fontsize=12.5, color=INK, bbox=dict(fc=PAPER, ec="none", pad=1), zorder=5)
    b.text(e_["hi"] + 0.2, yv - 0.08, f"{e_['b']:+.1f}", fontfamily=MONO, fontsize=11, color=INK, va="center")
b.set_xlim(-4, 7.5); b.set_ylim(-0.6, len(rows) - 0.1)
b.set_yticks([]); [b.spines[s_].set_visible(False) for s_ in ("top", "right", "left")]
b.tick_params(labelsize=10, colors=MUT)
for t_ in b.get_xticklabels(): t_.set_fontfamily(MONO)
b.set_xlabel("Extra chance of a Swing incident vs parishes with no Act, percentage points (95% CI)", fontfamily=MONO, fontsize=10, color=MUT)
fig.text(0.53, 0.43, f"The enclosure gap, {R['n']['sample']:,} parishes", fontfamily=SERIF, fontsize=15, fontweight="semibold", color=INK)
fig.text(0.03, 0.012, "Data: Caprettini and Voth (2020) parish data (Swing incidents from Holland, Swing Unmasked); enclosure Acts from the Chronological Tables of Private and Local Acts (legislation.gov.uk, OGL). "
         "\nCorrelation, not proof of cause.  Dr Tristan Hotham · maps.tristanhotham.com/enclosure-swing", fontfamily=MONO, fontsize=9.5, color=MUT, linespacing=1.6)
out = os.path.join(HERE, "enclosure_swing_collage.png")
fig.savefig(out, dpi=150, facecolor=PAPER); plt.close(fig)
print(Image.open(out).size)

# ---------- looping GIF: Acts accumulate year by year, then the Swing parishes of 1830
P_ = S.copy()
frames = []
years = list(range(1750, 1831, 2)) + [1830] * 4
for k, yr in enumerate(years):
    f = plt.figure(figsize=(6, 6.6), dpi=90, facecolor=PAPER)
    a = f.add_axes([0, 0, 1, 0.9]); base(a)
    a.scatter(x, y, s=0.8, c="#D6CAAD", lw=0)
    sel = P_.first_act.notna() & (P_.first_act <= yr) & (P_.never == 0)
    old = sel & (P_.first_act < 1790)
    a.scatter(P_.lon[old] * K, P_.lat[old], s=3, c=OLD, lw=0); a.scatter(P_.lon[sel & ~old] * K, P_.lat[sel & ~old], s=3, c=REC, lw=0)
    if k >= len(years) - 4:
        a.scatter(q.lon * K, q.lat, s=2 + 3 * np.sqrt(q.SWING), facecolor="none", edgecolor=RIOT, lw=.6)
    f.text(0.04, 0.94, f"{yr}", fontfamily=DISP, fontweight="bold", fontsize=26, color=REC)
    f.text(0.27, 0.955, "Parishes first enclosed by Act" if k < len(years) - 4 else "+ Swing unrest, 1830 (rings)", fontfamily=SERIF, fontsize=13, color=INK)
    f.text(0.27, 0.925, "gold before 1790, red 1790 on", fontfamily=MONO, fontsize=9.5, color=MUT)
    f.text(0.04, 0.02, "maps.tristanhotham.com/enclosure-swing", fontfamily=MONO, fontsize=8.5, color=MUT)
    f.canvas.draw()
    frames.append(Image.frombuffer("RGBA", f.canvas.get_width_height(), f.canvas.buffer_rgba()).convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=64))
    plt.close(f)
gp = os.path.join(HERE, "enclosure_swing.gif")
frames[0].save(gp, save_all=True, append_images=frames[1:], duration=[160] * (len(frames) - 4) + [900] * 4, loop=0, optimize=True)
print("gif", os.path.getsize(gp) // 1024, "KB", len(frames), "frames")
