"""Step 7: index.html from code/page_template.html, filled from data/results.json, with the full-screen snippet.
10.5281/zenodo.24091976, https://doi.org/10.5281/zenodo.24091976 and https://blog.tristanhotham.com/2026/10/31/enclosure-swing/ stay as placeholders for the publisher."""
from common import *

R = jload(f"{DATA}/results.json")
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
assert R["F"]["area_kills"] and R["F"]["old_equal"]
rows = "".join(f'<tr><td>{s["label"]}</td><td class="r">{s["b"]:+.1f}</td><td class="r">{s["lo"]:.1f} to {s["hi"]:.1f}</td><td class="r">{s["n"]:,}</td></tr>\n'
               for s in R["spec"])
rows += f'<tr><td>Placebo: first Act 1831 to 1870 (parishes with no earlier Act)</td><td class="r">{R["placebo"]["b"]:+.1f}</td><td class="r">{R["placebo"]["lo"]:.1f} to {R["placebo"]["hi"]:.1f}</td><td class="r">{R["placebo"]["n"]:,}</td></tr>\n'
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
t = t.replace("{{FULLSCREEN}}", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
t = t.replace("{{SPEC_ROWS}}", rows).replace("{{REPO}}", REPO).replace("{{AI}}", AI).replace("{{BYLINE}}", BYLINE).replace("{{VERSION}}", "20261109")
t = re.sub(r"\{\{([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), t)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= KEEP, set(re.findall(r"\{\{([^}]+)\}\}", t))
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("index.html", len(t) // 1024, "KB")
