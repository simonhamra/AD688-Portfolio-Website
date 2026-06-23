"""
Build on-brand dark charts for the portfolio from the real Lightcast cleaned data.
Palette = the "Signal" theme: near-black background, indigo primary, cyan glow.
No pink anywhere. All numbers come from the real a03 cleaned export.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

# ---- palette -------------------------------------------------------------
BG      = "#050505"
PANEL   = "#0A0A0A"
INK     = "#EDEDED"   # headings
BODY     = "#B4B4B4"  # labels
MUTE    = "#6E6E6E"
GRID    = "#1A1A1A"
SPINE   = "#262626"
INDIGO  = "#4F46E5"
INDIGO_L= "#818CF8"
CYAN    = "#22D3EE"
EMERALD = "#10B981"
AMBER   = "#FB923C"

plt.rcParams.update({
    "font.family": "monospace",
    "font.monospace": ["DejaVu Sans Mono"],
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
    "text.color": INK,
    "axes.labelcolor": BODY,
    "xtick.color": BODY,
    "ytick.color": BODY,
    "axes.edgecolor": SPINE,
    "axes.linewidth": 0.8,
    "axes.grid": False,
})

SRC = "/home/ubuntu/Assignments/a03-sum26-simonhamra/data/lightcast_cleaned.csv"
OUT = "/home/ubuntu/Assignments/Portfolio/assets/charts"

df = pd.read_csv(SRC, low_memory=False)
print("loaded", len(df), "rows")

# real, observed salaries only (no imputed values), sane range
obs = df[df["SALARY_OBSERVED"].notna()].copy()
obs = obs[(obs["SALARY_OBSERVED"] >= 20000) & (obs["SALARY_OBSERVED"] <= 400000)]
print("rows with a real observed salary:", len(obs))


def style_ax(ax, xgrid=False, ygrid=True):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(SPINE)
    if ygrid:
        ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    if xgrid:
        ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    ax.tick_params(length=0, labelsize=9)


def save(fig, name, transparent=False):
    fig.savefig(f"{OUT}/{name}", dpi=160, bbox_inches="tight",
                transparent=transparent, facecolor=("none" if transparent else BG))
    plt.close(fig)
    print("wrote", name)


def edu_group(x):
    x = str(x)
    if "Ph.D" in x or "Doctor" in x: return "PhD"
    if "Master" in x: return "Master"
    if "Bachelor" in x: return "Bachelor"
    if "Associate" in x: return "Associate"
    if "High school" in x or "GED" in x: return "High school"
    return "Other"


def remote_group(x):
    x = str(x)
    if "Hybrid" in x: return "Hybrid"
    if x.strip() == "Remote": return "Remote"
    return "Onsite"


def usd(x, _=None):
    return f"${x/1000:.0f}k"


# ========================================================================
# 1. HERO SIGNATURE  ----  "you are one data point in a labor market"
# ========================================================================
h = obs[obs["MIN_YEARS_EXPERIENCE"].notna()].copy()
h = h[(h["MIN_YEARS_EXPERIENCE"] >= 0) & (h["MIN_YEARS_EXPERIENCE"] <= 20)]
h = h.sample(min(1600, len(h)), random_state=42)
jit = h["MIN_YEARS_EXPERIENCE"] + np.random.uniform(-0.35, 0.35, len(h))

fig, ax = plt.subplots(figsize=(12, 4.6))
fig.patch.set_alpha(0)
ax.set_facecolor("none")
ax.scatter(jit, h["SALARY_OBSERVED"], s=14, c=INDIGO, alpha=0.22,
           edgecolors="none", zorder=2)
# the single highlighted point: an entry-level analyst moving into ML
me_x, me_y = 1.0, 112000
for r, a in [(620, 0.10), (360, 0.16), (190, 0.26)]:      # soft halo
    ax.scatter([me_x], [me_y], s=r, c=CYAN, alpha=a, edgecolors="none", zorder=3)
ax.scatter([me_x], [me_y], s=46, c=CYAN, edgecolors=BG, linewidths=1.2, zorder=4)
ax.annotate("you", (me_x, me_y), xytext=(me_x + 1.1, me_y + 34000),
            color=CYAN, fontsize=11, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color=CYAN, lw=1, alpha=0.7))
ax.set_xlim(-0.6, 20.5)
ax.set_ylim(0, 360000)
ax.yaxis.set_major_formatter(usd)
ax.set_xlabel("years of experience", fontsize=9, color=MUTE)
ax.set_ylabel("advertised salary", fontsize=9, color=MUTE)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["left", "bottom"]:
    ax.spines[s].set_color(SPINE)
ax.tick_params(length=0, labelsize=8, colors=MUTE)
ax.grid(axis="y", color="#121212", linewidth=0.8)
save(fig, "hero_market.png", transparent=True)


# ========================================================================
# 2. PAY BY OCCUPATION (A03)  ----  median salary, sized by demand
# ========================================================================
g = (obs.groupby("LOT_OCCUPATION_NAME")
        .agg(median=("SALARY_OBSERVED", "median"), n=("SALARY_OBSERVED", "size"))
        .reset_index())
g = g[g["n"] >= 30].sort_values("median").tail(8)

fig, ax = plt.subplots(figsize=(9, 5))
colors = [CYAN if v == g["median"].max() else INDIGO for v in g["median"]]
ax.barh(g["LOT_OCCUPATION_NAME"], g["median"], color=colors, height=0.62, zorder=3)
for y, (v, n) in enumerate(zip(g["median"], g["n"])):
    ax.text(v + 1500, y, f"{usd(v)}", va="center", ha="left",
            color=INK, fontsize=9, fontweight="bold")
style_ax(ax, xgrid=True, ygrid=False)
ax.xaxis.set_major_formatter(usd)
ax.set_xlim(0, g["median"].max() * 1.18)
ax.set_xlabel("median advertised salary", fontsize=9)
ax.set_title("Pay by occupation", color=INK, fontsize=13, fontweight="bold",
             loc="left", pad=12)
save(fig, "pay_by_occupation.png")


# ========================================================================
# 3. PAY BY EDUCATION (A03)  ----  the rising ladder
# ========================================================================
obs["EDU"] = obs["MIN_EDULEVELS_NAME"].apply(edu_group)
order = ["High school", "Associate", "Bachelor", "Master", "PhD"]
e = (obs[obs["EDU"].isin(order)]
        .groupby("EDU")["SALARY_OBSERVED"].median().reindex(order).dropna())

fig, ax = plt.subplots(figsize=(8, 5))
cole = [CYAN if v == e.max() else INDIGO for v in e.values]
ax.bar(e.index, e.values, color=cole, width=0.62, zorder=3)
for x, v in zip(e.index, e.values):
    ax.text(x, v + 2500, usd(v), ha="center", color=INK, fontsize=9.5, fontweight="bold")
style_ax(ax, ygrid=True)
ax.yaxis.set_major_formatter(usd)
ax.set_ylim(0, e.max() * 1.16)
ax.set_ylabel("median advertised salary", fontsize=9)
ax.set_title("Pay by education level", color=INK, fontsize=13,
             fontweight="bold", loc="left", pad=12)
save(fig, "pay_by_education.png")


# ========================================================================
# 4. PAY BY REMOTE TYPE (A03)
# ========================================================================
obs["REM"] = obs["REMOTE_TYPE_NAME"].apply(remote_group)
order_r = ["Onsite", "Hybrid", "Remote"]
r = obs.groupby("REM")["SALARY_OBSERVED"].median().reindex(order_r).dropna()

fig, ax = plt.subplots(figsize=(7.5, 5))
colr = [INDIGO, INDIGO_L, CYAN][-len(r):]
ax.bar(r.index, r.values, color=colr, width=0.55, zorder=3)
for x, v in zip(r.index, r.values):
    ax.text(x, v + 2500, usd(v), ha="center", color=INK, fontsize=9.5, fontweight="bold")
style_ax(ax, ygrid=True)
ax.yaxis.set_major_formatter(usd)
ax.set_ylim(0, r.max() * 1.16)
ax.set_ylabel("median advertised salary", fontsize=9)
ax.set_title("Remote roles pay a premium", color=INK, fontsize=13,
             fontweight="bold", loc="left", pad=12)
save(fig, "pay_by_remote.png")


# ========================================================================
# 5. PAY BY STATE (A02 theme)  ----  where the money is
# ========================================================================
s = (obs.groupby("STATE_NAME")
        .agg(median=("SALARY_OBSERVED", "median"), n=("SALARY_OBSERVED", "size"))
        .reset_index())
s = s[s["n"] >= 80].sort_values("median").tail(10)

fig, ax = plt.subplots(figsize=(9, 5.4))
colors = [CYAN if v == s["median"].max() else INDIGO for v in s["median"]]
ax.barh(s["STATE_NAME"], s["median"], color=colors, height=0.64, zorder=3)
for y, v in enumerate(s["median"]):
    ax.text(v + 1500, y, usd(v), va="center", color=INK, fontsize=9, fontweight="bold")
style_ax(ax, xgrid=True, ygrid=False)
ax.xaxis.set_major_formatter(usd)
ax.set_xlim(0, s["median"].max() * 1.16)
ax.set_xlabel("median advertised salary", fontsize=9)
ax.set_title("Top paying states", color=INK, fontsize=13, fontweight="bold",
             loc="left", pad=12)
save(fig, "pay_by_state.png")


# ========================================================================
# 6. SALARY DRIVERS (A05 theme)  ----  real random forest importances
# ========================================================================
from sklearn.ensemble import RandomForestRegressor

feat = obs.dropna(subset=["MIN_YEARS_EXPERIENCE"]).copy()
feat["EDU"] = feat["MIN_EDULEVELS_NAME"].apply(edu_group)
feat["REM"] = feat["REMOTE_TYPE_NAME"].apply(remote_group)
cat = ["EDU", "REM", "NAICS2_NAME", "EMPLOYMENT_TYPE_NAME"]
num = ["MIN_YEARS_EXPERIENCE"]
X = pd.get_dummies(feat[num + cat], columns=cat, dummy_na=False)
y = feat["SALARY_OBSERVED"]
rf = RandomForestRegressor(n_estimators=160, max_depth=10, random_state=42, n_jobs=-1)
rf.fit(X, y)
imp = pd.Series(rf.feature_importances_, index=X.columns)

# group one-hot importances back to the parent feature
groups = {
    "Years of experience": ["MIN_YEARS_EXPERIENCE"],
    "Industry": [c for c in X.columns if c.startswith("NAICS2_NAME_")],
    "Education": [c for c in X.columns if c.startswith("EDU_")],
    "Employment type": [c for c in X.columns if c.startswith("EMPLOYMENT_TYPE_NAME_")],
    "Remote type": [c for c in X.columns if c.startswith("REM_")],
}
gi = pd.Series({k: imp[v].sum() for k, v in groups.items()}).sort_values()
print("R2 (in-sample, demo only):", round(rf.score(X, y), 3))
print(gi)

fig, ax = plt.subplots(figsize=(9, 4.8))
colors = [CYAN if v == gi.max() else INDIGO for v in gi.values]
ax.barh(gi.index, gi.values, color=colors, height=0.6, zorder=3)
for y_, v in enumerate(gi.values):
    ax.text(v + 0.006, y_, f"{v*100:.0f}%", va="center", color=INK,
            fontsize=9, fontweight="bold")
style_ax(ax, xgrid=True, ygrid=False)
ax.set_xlim(0, gi.max() * 1.18)
ax.set_xlabel("share of model importance", fontsize=9)
ax.set_title("What moves salary", color=INK, fontsize=13, fontweight="bold",
             loc="left", pad=12)
save(fig, "salary_drivers.png")

print("done.")
