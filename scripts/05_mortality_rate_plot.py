# ============================================================
# 05_mortality_rate_plot.py
# Purpose: plot mortality rates by sex and year, with APC results
# ============================================================

# ---- 1. Imports ----
# %%
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---- 2. Paths ----
# %%
def find_root(start=Path.cwd()):
    for p in [start, *start.parents]:
        if (p / "data" / "processed").exists():
            return p
    raise FileNotFoundError("Project root not found")

ROOT = find_root()
PROCESSED = ROOT / "data" / "processed"

# ---- 3. Load ----
# %%
# ---- 3. Load ----
# %%
asr_df = pd.read_csv(PROCESSED / "asr_by_year_sex.csv")
apc_df = pd.read_csv(PROCESSED / "apc_results_r.csv")

# Normalise so "Male"/"male" etc. match
asr_df["sex"]   = asr_df["sex"].astype(str).str.strip().str.lower()
apc_df["group"] = apc_df["group"].astype(str).str.strip().str.lower()

# Convert APC and CI percentages to floats   <-- NEW
for col in ["APC", "CI_low", "CI_upp"]:
    apc_df[col] = (
        apc_df[col].astype(str)
        .str.replace("%", "", regex=False)
        .str.replace("−", "-", regex=False)
        .str.strip()
    )
    apc_df[col] = pd.to_numeric(apc_df[col], errors="coerce")

# Split period into start/end years
apc_df[["start_year", "end_year"]] = (
    apc_df["period"].str.split("-", expand=True).astype(int)
)

# ---- 3b. Assign each row a segment ----
# %%
# Ensure the segment column exists
if "segment" not in apc_df.columns:
    apc_df["segment"] = apc_df.groupby("group").cumcount() + 1

# Assign segment per row
asr_df["segment"] = None
for sex in asr_df["sex"].unique():
    sub_apc = apc_df[apc_df["group"] == sex].sort_values("start_year")
    mask = asr_df["sex"] == sex
    for _, seg in sub_apc.iterrows():
        in_seg = mask & (asr_df["year"] >= seg["start_year"]) & (asr_df["year"] <= seg["end_year"])
        asr_df.loc[in_seg, "segment"] = int(seg["segment"])

# Build descriptive label per segment, e.g. "male 2013–2024 (APC -1.2%)"
apc_lookup = {}
for _, seg in apc_df.iterrows():
    key = f"{seg['group']}_{int(seg['segment'])}"
    sig = "*" if (seg["CI_low"] * seg["CI_upp"]) > 0 else ""
    apc_lookup[key] = (
        f"{seg['group']} {seg['start_year']}–{seg['end_year']} "
        f"(APC {seg['APC']:+.1f}%{sig})"
    )

asr_df["color_key"] = asr_df["sex"] + "_" + asr_df["segment"].astype(int).astype(str)
asr_df["segment_label"] = asr_df["color_key"].map(apc_lookup)

# ---- 4. Plot ----
# %%
base_shades = {
    "male":   ["#c6dbef", "#6baed6", "#2171b5"],
    "female": ["#fcbba1", "#fb6a4a", "#a50f15"],
    "total":  ["#c7e9c0", "#74c476", "#238b45"],
}

color_map = {}
for sex in ["male", "female", "total"]:
    segs = apc_df[apc_df["group"] == sex].sort_values("segment")
    for i, (_, seg) in enumerate(segs.iterrows()):
        key = f"{sex}_{int(seg['segment'])}"
        if key in apc_lookup:
            shade = base_shades[sex][min(i, len(base_shades[sex]) - 1)]
            color_map[apc_lookup[key]] = shade

fig = px.line(
    asr_df,
    x="year",
    y="asr",
    color="segment_label",
    line_group="sex",
    color_discrete_map=color_map,
    markers=True,
    title="Portugal Age-Standardized Mortality Rate (1970–2024)",
    labels={"year": "Year", "asr": "ASR per 100,000", "segment_label": "Segment"},
)

# Label each segment at its midpoint
for label in asr_df["segment_label"].dropna().unique():
    sub = asr_df[asr_df["segment_label"] == label].sort_values("year")
    # Midpoint row of the segment
    mid_idx = len(sub) // 2
    mid_year = sub["year"].iloc[mid_idx]
    mid_asr = sub["asr"].iloc[mid_idx]
    fig.add_annotation(
        x=mid_year,
        y=mid_asr,
        text=label,
        showarrow=False,
        yshift=18,                      # push above the line
        font=dict(size=8, color=color_map.get(label, "black")),
        bgcolor="rgba(255,255,255,0.75)",
        bordercolor="rgba(0,0,0,0.1)",
        borderwidth=1,
    )

# ---- 5. Layout: legend at bottom, every year on x-axis ----
# %%
year_min = int(asr_df["year"].min())
year_max = int(asr_df["year"].max())
all_years = list(range(year_min, year_max + 1))

fig.update_layout(
    template="plotly_white",
    height=600,
    showlegend=False,
    margin=dict(b=80),
    xaxis=dict(
        tickmode="array",
        tickvals=all_years,
        ticktext=[str(y) for y in all_years],
        tickangle=-90,
        tickfont=dict(size=8),
    ),
)

# ---- 6. Save ----
# %%
out = ROOT / "dashboard" / "mortality_asr.html"
out.parent.mkdir(parents=True, exist_ok=True)
fig.write_html(out)
print(f"Saved → {out}")