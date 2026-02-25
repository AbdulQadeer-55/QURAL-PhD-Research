import pandas as pd
import numpy as np
from pathlib import Path

TEXT_XLSX = "outputs/analysis_text_metrics/Text_Similarity_Matrices.xlsx"
RANK_XLSX = "outputs/analysis_metrics/Rank_Correlation_Matrices.xlsx"
ALPHA_XLSX = "outputs/analysis_metrics/Krippendorff_Alpha_ByCriterion.xlsx"
ICC_XLSX = "outputs/analysis_metrics/ICC_Summary.xlsx"

OUT_DIR = Path("outputs/final_ranking")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def mean_offdiag(mat: pd.DataFrame) -> pd.Series:
    models = list(mat.index)
    out = {}
    for m in models:
        vals = mat.loc[m, [x for x in models if x != m]].astype(float)
        out[m] = float(vals.mean())
    return pd.Series(out).sort_values(ascending=False)

def minmax(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    if np.isclose(s.max(), s.min()):
        return pd.Series(1.0, index=s.index)
    return (s - s.min()) / (s.max() - s.min())

def main():
    # --- Load matrices ---
    text_xl = pd.ExcelFile(TEXT_XLSX)
    bert = text_xl.parse("BERTScore_F1", index_col=0)
    meteor = text_xl.parse("METEOR", index_col=0)

    rank_xl = pd.ExcelFile(RANK_XLSX)
    spearman = rank_xl.parse("Spearman_TotalScore", index_col=0)
    kendall = rank_xl.parse("Kendall_TotalScore", index_col=0)

    # --- Per-model “agreement with others” scores ---
    bert_m = mean_offdiag(bert)
    meteor_m = mean_offdiag(meteor)
    consistency_m = (mean_offdiag(spearman) + mean_offdiag(kendall)) / 2.0

    # Align index
    models = sorted(set(bert_m.index) & set(meteor_m.index) & set(consistency_m.index))
    bert_m = bert_m.reindex(models)
    meteor_m = meteor_m.reindex(models)
    consistency_m = consistency_m.reindex(models)

    # --- Normalize to 0–1 for weighted ranking ---
    bert_n = minmax(bert_m)
    meteor_n = minmax(meteor_m)
    cons_n = minmax(consistency_m)

    # Client weights
    W_BERT = 0.40
    W_METEOR = 0.30
    W_CONS = 0.30

    final = (W_BERT * bert_n) + (W_METEOR * meteor_n) + (W_CONS * cons_n)

    # --- Build ranking table ---
    table = pd.DataFrame({
        "Model": models,
        "BERTScore_mean_to_others": bert_m.values,
        "METEOR_mean_to_others": meteor_m.values,
        "Consistency_mean(Spearman,Kendall)": consistency_m.values,
        "BERTScore_norm": bert_n.values,
        "METEOR_norm": meteor_n.values,
        "Consistency_norm": cons_n.values,
        "Final_Weighted_Score": final.values
    }).sort_values("Final_Weighted_Score", ascending=False)

    # --- Save ---
    out_xlsx = OUT_DIR / "Table_LLM_Rankings_Final.xlsx"
    out_csv = OUT_DIR / "Table_LLM_Rankings_Final.csv"
    table.to_excel(out_xlsx, index=False)
    table.to_csv(out_csv, index=False)

    # --- Also export system-level reliability (Alpha + ICC) for report ---
    alpha_df = pd.read_excel(ALPHA_XLSX)
    icc_df = pd.read_excel(ICC_XLSX)

    report_notes = []
    report_notes.append("SYSTEM-LEVEL RELIABILITY (multi-rater):")
    report_notes.append(f"- Mean Krippendorff’s Alpha (ordinal, across criteria): {alpha_df['Krippendorff_Alpha_Ordinal'].mean():.3f}")
    report_notes.append(f"- Median Krippendorff’s Alpha: {alpha_df['Krippendorff_Alpha_Ordinal'].median():.3f}")
    for _, r in icc_df.iterrows():
        report_notes.append(f"- ICC(2,1) for {r['Metric']}: {r['ICC_2_1']:.3f}")

    # --- Select winners ---
    # Judge = highest consistency (stable scoring)
    judge_model = table.sort_values("Consistency_mean(Spearman,Kendall)", ascending=False).iloc[0]["Model"]
    # Regenerator = highest final weighted score
    regen_model = table.iloc[0]["Model"]

    report_notes.append("\nMODEL SELECTION:")
    report_notes.append(f"- Suggested Regeneration LLM (highest final weighted score): {regen_model}")
    report_notes.append(f"- Suggested Judge LLM (highest rank/score consistency): {judge_model}")
    report_notes.append("\nNOTE:")
    report_notes.append("Krippendorff’s Alpha and ICC are computed across all 5 models (system-level).")
    report_notes.append("Per-model consistency used for ranking is mean(Spearman,Kendall) vs other models.")

    (OUT_DIR / "Model_Selection_Rationale.txt").write_text("\n".join(report_notes), encoding="utf-8")

    print("✅ Saved:")
    print(" -", out_xlsx)
    print(" -", out_csv)
    print(" -", OUT_DIR / "Model_Selection_Rationale.txt")
    print("\nWinner (Regeneration):", regen_model)
    print("Winner (Judge):", judge_model)

if __name__ == "__main__":
    main()
