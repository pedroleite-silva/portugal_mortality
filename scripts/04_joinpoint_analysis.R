# ============================================================
# 04_joinpoint_analysis.R
# Purpose: analyze age-standardized rates using joinpoint regression
# ============================================================

# ---- 1. Imports ----#
library(joinpointR)
library(dplyr)
library(segmented)

# ---- 2. Load ----
asr_df <- read.csv("data/processed/asr_by_year_sex.csv")

# ---- 3. Ensure Sex is a factor, and column names match the function requirements
asr_df$sex <- factor(asr_df$sex, levels = c("male", "female", "total"))

# ---- 4. Fit joinpoint models (grid search + BIC selection)
# rate specifies the rate column, time specifies the year column, group specifies grouping by sex
mods <- model_jp(
  data = asr_df,
  value = "asr",
  time = "year",
  group = "sex"
)

# Extract APC for each time segment and its 95% CI
apc_table <- summary_jp(mods)
print(apc_table)

# Export the results for Python plotting
write.csv(apc_table, "data/processed/apc_results_r.csv", row.names = FALSE)
