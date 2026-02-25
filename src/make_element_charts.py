import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

MASTER = "Master_QURAL_Analysis.xlsx"
OUT_DIR = Path("outputs/analysis_figures")
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

def _score_col(c): return f"{c}_Score"

def main():
    df = pd.read_excel(MASTER)

    # keep only expected models (avoid old Gemini fallback folders if present in Master)
    df = df[df["Model"].notna()].copy()

    # Build per-model metrics
    rows = []
    for model, g in df.groupby("Model"):
        for c in CRITERIA:
            col = _score_col(c)
            if col not in g.columns:
                continue
            vals = pd.to_numeric(g[col], errors="coerce").fillna(0)
            avg_score = float(vals.mean())
            detect_rate = float((vals > 0).mean()) * 100.0
            rows.append({"Model": model, "Criterion": c, "AvgScore": avg_score, "DetectRatePct": detect_rate})

    mdf = pd.DataFrame(rows)
    mdf.to_excel(OUT_DIR / "Element_Metrics_ByModel.xlsx", index=False)

    # --- Plot 1: Avg score per criterion per model (grouped bar) ---
    pivot_avg = mdf.pivot_table(index="Criterion", columns="Model", values="AvgScore", aggfunc="mean").reindex(CRITERIA)
    plt.figure(figsize=(20,6))
    pivot_avg.plot(kind="bar")
    plt.title("Average QURAL Criterion Score by Model (0–2)")
    plt.ylabel("Average Score")
    plt.xlabel("Criterion")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 2.05)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "AvgScore_ByCriterion_ByModel.png", dpi=200)
    plt.close()

    # --- Plot 2: Detection rate per criterion per model (grouped bar) ---
    pivot_det = mdf.pivot_table(index="Criterion", columns="Model", values="DetectRatePct", aggfunc="mean").reindex(CRITERIA)
    plt.figure(figsize=(20,6))
    pivot_det.plot(kind="bar")
    plt.title("Detection Rate by Criterion and Model (% of stories with score > 0)")
    plt.ylabel("Detection Rate (%)")
    plt.xlabel("Criterion")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 105)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "DetectionRate_ByCriterion_ByModel.png", dpi=200)
    plt.close()

    # --- Plot 3: Single bar chart - overall element identification per model ---
    # overall detection = average detection rate across criteria
    overall = mdf.groupby("Model")["DetectRatePct"].mean().sort_values(ascending=False)
    plt.figure(figsize=(10,5))
    overall.plot(kind="bar")
    plt.title("Overall Elements Identified per Model (Avg Detection Rate Across 14 Criteria)")
    plt.ylabel("Avg Detection Rate (%)")
    plt.xlabel("Model")
    plt.ylim(0, 105)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "Overall_Element_Identification_ByModel.png", dpi=200)
    plt.close()

    print("✅ Saved:")
    print(f" - {OUT_DIR / 'Element_Metrics_ByModel.xlsx'}")
    print(f" - {OUT_DIR / 'AvgScore_ByCriterion_ByModel.png'}")
    print(f" - {OUT_DIR / 'DetectionRate_ByCriterion_ByModel.png'}")
    print(f" - {OUT_DIR / 'Overall_Element_Identification_ByModel.png'}")

if __name__ == "__main__":
    main()
