import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr, kendalltau

MASTER = "Master_QURAL_Analysis.xlsx"
OUT_DIR = Path("outputs/analysis_metrics")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CRITERIA = [
    "Task Identification",
    "Task Nature",
    "Role Identification",
    "Acceptance Criteria",
    "Dependency",
    "Business Need",
    "Priority",
    "Quality Requirement",
    "Estimable",
    "Unambiguous",
    "Well Formed",
    "Problem Oriented",
    "Unique",
    "Testable",
]

TIER1_KEYS = ["Role Identification","Task Nature","Acceptance Criteria","Business Need","Unambiguous"]
TIER2_KEYS = ["Task Identification","Dependency","Priority","Quality Requirement","Estimable","Well Formed","Problem Oriented","Unique","Testable"]

def krippendorff_alpha_ordinal(data, min_rating=0, max_rating=2):
    """
    data: 2D array (units x raters), may contain NaN
    ordinal distance: normalized squared distance
    alpha = 1 - Do/De
    """
    data = np.asarray(data, dtype=float)

    # distance function for ordinal
    rng = max_rating - min_rating
    def dist(a, b):
        return ((a - b) / rng) ** 2

    # observed disagreement Do
    Do_num = 0.0
    Do_den = 0.0
    for row in data:
        vals = row[~np.isnan(row)]
        m = len(vals)
        if m < 2:
            continue
        # pairwise disagreement
        s = 0.0
        for i in range(m):
            for j in range(i+1, m):
                s += dist(vals[i], vals[j])
        Do_num += 2 * s
        Do_den += m * (m - 1)

    if Do_den == 0:
        return np.nan
    Do = Do_num / Do_den

    # expected disagreement De from overall distribution
    all_vals = data[~np.isnan(data)].astype(int)
    if len(all_vals) == 0:
        return np.nan

    levels = np.arange(min_rating, max_rating+1)
    counts = np.array([(all_vals == l).sum() for l in levels], dtype=float)
    n = counts.sum()
    if n <= 1:
        return np.nan
    p = counts / n

    De = 0.0
    for i, a in enumerate(levels):
        for j, b in enumerate(levels):
            De += p[i] * p[j] * dist(a, b)

    if De == 0:
        return np.nan
    return 1.0 - (Do / De)

def icc_2_1(ratings_matrix):
    """
    ICC(2,1): Two-way random effects, absolute agreement, single rater.
    ratings_matrix: n_targets x k_raters, must be balanced (no NaN)
    """
    X = np.asarray(ratings_matrix, dtype=float)
    if np.isnan(X).any():
        return np.nan

    n, k = X.shape
    grand = X.mean()
    mean_target = X.mean(axis=1)
    mean_rater = X.mean(axis=0)

    # Sum of squares
    SS_target = k * np.sum((mean_target - grand) ** 2)
    SS_rater  = n * np.sum((mean_rater - grand) ** 2)
    SS_error  = np.sum((X - mean_target[:, None] - mean_rater[None, :] + grand) ** 2)

    df_target = n - 1
    df_rater = k - 1
    df_error = (n - 1) * (k - 1)

    MS_target = SS_target / df_target if df_target else np.nan
    MS_rater = SS_rater / df_rater if df_rater else np.nan
    MS_error = SS_error / df_error if df_error else np.nan

    denom = MS_target + (k - 1) * MS_error + (k * (MS_rater - MS_error) / n)
    if denom == 0 or np.isnan(denom):
        return np.nan
    return (MS_target - MS_error) / denom

def build_pivot(df, value_col):
    pivot = df.pivot_table(index="Original_Story", columns="Model", values=value_col, aggfunc="mean")
    pivot = pivot.dropna()  # require all 5 models present for that story
    return pivot

def main():
    df = pd.read_excel(MASTER)

    # ensure numeric
    df["Total_Score"] = pd.to_numeric(df["Total_Score"], errors="coerce")

    # compute tier scores if missing (some masters already have them)
    if "Tier_1_Score" not in df.columns:
        df["Tier_1_Score"] = df[[f"{k}_Score" for k in TIER1_KEYS]].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    if "Tier_2_Score" not in df.columns:
        df["Tier_2_Score"] = df[[f"{k}_Score" for k in TIER2_KEYS]].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)

    # --- Krippendorff's Alpha per criterion (ordinal 0-2) ---
    alpha_rows = []
    for c in CRITERIA:
        col = f"{c}_Score"
        if col not in df.columns:
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")
        pivot = build_pivot(df, col)  # stories x models
        alpha = krippendorff_alpha_ordinal(pivot.values, 0, 2)
        alpha_rows.append({"Criterion": c, "Krippendorff_Alpha_Ordinal": alpha, "Stories_Used": pivot.shape[0]})

    alpha_df = pd.DataFrame(alpha_rows).sort_values("Krippendorff_Alpha_Ordinal", ascending=False)
    alpha_df.to_excel(OUT_DIR / "Krippendorff_Alpha_ByCriterion.xlsx", index=False)

    # --- ICC for Total / Tier1 / Tier2 ---
    icc_rows = []
    for metric in ["Total_Score", "Tier_1_Score", "Tier_2_Score"]:
        pivot = build_pivot(df, metric)
        icc = icc_2_1(pivot.values)
        icc_rows.append({"Metric": metric, "ICC_2_1": icc, "Stories_Used": pivot.shape[0], "Num_Models": pivot.shape[1]})

    icc_df = pd.DataFrame(icc_rows)
    icc_df.to_excel(OUT_DIR / "ICC_Summary.xlsx", index=False)

    # --- Spearman & Kendall matrices (Total Score) ---
    pivot_total = build_pivot(df, "Total_Score")
    models = list(pivot_total.columns)

    spearman_mat = pd.DataFrame(index=models, columns=models, dtype=float)
    kendall_mat = pd.DataFrame(index=models, columns=models, dtype=float)

    for i, m1 in enumerate(models):
        for j, m2 in enumerate(models):
            if i == j:
                spearman_mat.loc[m1, m2] = 1.0
                kendall_mat.loc[m1, m2] = 1.0
            else:
                s, _ = spearmanr(pivot_total[m1], pivot_total[m2])
                k, _ = kendalltau(pivot_total[m1], pivot_total[m2])
                spearman_mat.loc[m1, m2] = s
                kendall_mat.loc[m1, m2] = k

    with pd.ExcelWriter(OUT_DIR / "Rank_Correlation_Matrices.xlsx") as xw:
        spearman_mat.to_excel(xw, sheet_name="Spearman_TotalScore")
        kendall_mat.to_excel(xw, sheet_name="Kendall_TotalScore")

    print("✅ Saved:")
    print(" -", OUT_DIR / "Krippendorff_Alpha_ByCriterion.xlsx")
    print(" -", OUT_DIR / "ICC_Summary.xlsx")
    print(" -", OUT_DIR / "Rank_Correlation_Matrices.xlsx")

if __name__ == "__main__":
    main()
