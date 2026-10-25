# ============================================================
# 03_build_rates.py
# Purpose: build age-standardized rates from cleaned mortality and population data
# ============================================================

# ---- 1. Imports ----
# %%
from pathlib import Path
import pandas as pd
import numpy as np

# ---- 2. Paths ----
# %%
ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

# ---- 3. Load ----
# %%
mortality = pd.read_csv(PROCESSED / "mortality_tidy.csv")
pop = pd.read_csv(PROCESSED / "population_tidy.csv")

# %%
print(mortality.head(-1))
# %%
print(pop.head(-1))

# ---- 4. ESP 2013 weights for your age groups (per 100,000 total standard population) ----
# %%
esp_weights = {
    "0-4": 5000,      # 1000 (under 1) + 4000 (1-4)
    "5-9": 5500,
    "10-14": 5500,
    "15-19": 5500,
    "20-24": 6000,
    "25-29": 6000,
    "30-34": 6500,
    "35-39": 7000,
    "40-44": 7000,
    "45-49": 7000,
    "50-54": 7000,
    "55-59": 6500,
    "60-64": 6000,
    "65-69": 5500,
    "70-74": 5000,
    "75-79": 4000,
    "80-84": 2500,
    "85+": 2500,      # 1500 (85-89) + 800 (90-94) + 200 (95+)
}


# ---- 5. Merge mortality and population ----
# %%
df = mortality.merge(pop, on=["year", "sex", "age_group"], how="inner")
df["weight"] = df["age_group"].map(esp_weights)
print(df.head())
# ---- 6. Build age-standardized rates ----
# Direct standardization: ASR = sum(w_i * rate_i) / sum(w_i)
# %%
def asr_with_ci(g):
    w = g["weight"].values
    d = g["mortality"].values
    n = g["population"].values
    rate = d / n
    asr = (w * rate).sum() / w.sum()
    # Poisson SE for directly standardized rate
    se = np.sqrt((w**2 * d / n**2).sum()) / w.sum()
    return pd.Series({
        "asr": asr * 1e5,
        "lower": (asr - 1.96 * se) * 1e5,
        "upper": (asr + 1.96 * se) * 1e5,
    })

print(df.head())
# ---- 8. Save output ----
# %%
asr_df = df.groupby(["year", "sex"]).apply(asr_with_ci, include_groups=False).reset_index()
asr_df.to_csv(PROCESSED / "asr_by_year_sex.csv", index=False)
# %%

