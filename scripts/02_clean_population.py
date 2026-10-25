# ============================================================
# 02_clean_population.py
# Purpose: load raw population file, standardise columns, save tidy CSV
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
pop = pd.read_csv(RAW / "population_long.csv")
pop.head()   # Run this line with Shift+Enter to see the data

# ---- 4. Data inspection ----
# %%
print(pop.columns.tolist())
#print(pop.shape)
#set(pop["age_group"].unique())

# ---- 5. DB cleansing ----
# %%
columns_to_keep = [
    "Year",
    "Sex",
    "0 - 4 anos",
    "5 - 9 anos",
    "10 - 14 anos",
    "15 - 19 anos",
    "20 - 24 anos",
    "25 - 29 anos",
    "30 - 34 anos",
    "35 - 39 anos",
    "40 - 44 anos",
    "45 - 49 anos",
    "50 - 54 anos",
    "55 - 59 anos",
    "60 - 64 anos",
    "65 - 69 anos",
    "70 - 74 anos",
    "75 - 79 anos",
    "80 - 84 anos",
    "85 e mais anos",
]

missing = [c for c in columns_to_keep if c not in pop.columns]
print("Missing:", missing)
# %%
pop = pop[columns_to_keep].copy()
print(pop.head())
print(pop.shape)

# %%
pop = pop.melt(
    id_vars=["Year", "Sex"],
    var_name="Age",
    value_name="Population",
)

# %%
pop["Sex"] = pop["Sex"].replace({
    "H": "male",
    "M": "female",
    "HM": "total",
})

pop["Age"] = pop["Age"].replace({
    "0 - 4 anos": "0-4",
    "5 - 9 anos": "5-9",
    "10 - 14 anos": "10-14",
    "15 - 19 anos": "15-19",
    "20 - 24 anos": "20-24",
    "25 - 29 anos": "25-29",
    "30 - 34 anos": "30-34",
    "35 - 39 anos": "35-39",
    "40 - 44 anos": "40-44",
    "45 - 49 anos": "45-49",
    "50 - 54 anos": "50-54",
    "55 - 59 anos": "55-59",
    "60 - 64 anos": "60-64",
    "65 - 69 anos": "65-69",
    "70 - 74 anos": "70-74",
    "75 - 79 anos": "75-79",
    "80 - 84 anos": "80-84",
    "85 e mais anos": "85+",
})

age_order = [
    "0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34",
    "35-39", "40-44", "45-49", "50-54", "55-59", "60-64",
    "65-69", "70-74", "75-79", "80-84", "85+",
]

pop["Age"] = pd.Categorical(pop["Age"], categories=age_order, ordered=True)
pop = pop.sort_values(["Year", "Sex", "Age"]).reset_index(drop=True)

print(pop.head(20))
print(pop.shape)
# %%

# ---- 6. Standardise column names ----
# %%
pop = pop.rename(columns={
    "Year": "year",
    "Sex": "sex",
    "Age": "age_group",
    "Population": "population",
})

# ---- 7. Clean values ----
# %%
pop["year"] = pop["year"].astype(int)
pop["sex"] = pop["sex"].str.strip().str.lower()
pop["age_group"] = pop["age_group"].str.strip()
pop["population"] = pd.to_numeric(pop["population"], errors="coerce")

# ---- 8. Save tidy output ----
# %%
pop.to_csv(PROCESSED / "population_tidy.csv", index=False)
print(f"Saved {len(pop)} rows to population_tidy.csv")
