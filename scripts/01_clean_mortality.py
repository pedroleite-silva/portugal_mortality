# ============================================================
# 01_clean_mortality.py
# Purpose: load raw mortality file, standardise columns, save tidy CSV
# ============================================================

# ---- 1. Imports ----
# %%
from pathlib import Path
import pandas as pd

# ---- 2. Paths ----
# %%
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

# ---- 3. Load ----
# %%
deaths = pd.read_csv(RAW / "mortality_long.csv")
deaths.head()   # Run this line with Shift+Enter to see the data

# ---- 4. Data inspection ----
# %%
print(deaths.columns.tolist())
#print(deaths.shape)
#set(deaths_long["age_group"].unique())

# ---- 5. DB cleansing ----
# %%
deaths_long = deaths.melt(
    id_vars=["Year", "Age"],
    value_vars=["Female", "Male", "Total"],
    var_name="Sex",
    value_name="Mortality",
)

deaths_long.head()
# %%
age_map = {
    "0": "0-4",
    "1-4": "0-4",
    "85-89": "85+",
    "90-94": "85+",
    "95-99": "85+",
    "100-104": "85+",
    "105-109": "85+",
    "110": "85+",
}

deaths_long["Age"] = deaths_long["Age"].replace(age_map)

deaths_long = (
    deaths_long.groupby(["Year", "Sex", "Age"], as_index=False)["Mortality"]
       .sum()
)
# %%
age_order = [
    "0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34",
    "35-39", "40-44", "45-49", "50-54", "55-59", "60-64",
    "65-69", "70-74", "75-79", "80-84", "85+",
]

deaths_long["Age"] = pd.Categorical(deaths_long["Age"], categories=age_order, ordered=True)
deaths_long = deaths_long.sort_values(["Year", "Sex", "Age"]).reset_index(drop=True)

deaths_long.head()

# ---- 6. Standardise column names ----
# %%
deaths_long = deaths_long.rename(columns={
    "Year": "year",
    "Sex": "sex",
    "Age": "age_group",
    "Mortality": "mortality",
})

# ---- 7. Clean values ----
# %%
deaths_long["year"] = deaths_long["year"].astype(int)
deaths_long["sex"] = deaths_long["sex"].str.strip().str.lower()
deaths_long["age_group"] = deaths_long["age_group"].str.strip()
deaths_long["mortality"] = pd.to_numeric(deaths_long["mortality"], errors="coerce")

# ---- 8. Save tidy output ----
# %%
deaths_long.to_csv(PROCESSED / "mortality_tidy.csv", index=False)
print(f"Saved {len(deaths_long)} rows to mortality_tidy.csv")