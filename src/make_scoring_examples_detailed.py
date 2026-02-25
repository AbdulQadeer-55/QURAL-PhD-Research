import pandas as pd
from pathlib import Path

MASTER = "Master_QURAL_Analysis.xlsx"
OUT_DIR = Path("outputs/analysis_tables")
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

META_COLS = [
    "Project", "Model", "Original_Story",
    "Total_Score", "Tier_1_Score", "Tier_2_Score", "Structurally_Sound"
]

def score_col(c): return f"{c}_Score"
def text_col(c): return f"{c}_Text"

def pick_projects_and_stories(df, projects_n=3, stories_per_project=2):
    # pick projects with most stories to ensure all models exist
    proj_counts = df.groupby("Project")["Original_Story"].nunique().sort_values(ascending=False)
    projects = proj_counts.head(projects_n).index.tolist()

    stories = []
    for p in projects:
        # pick diverse set: lowest, middle, highest score stories (based on mean Total_Score across models)
        sub = df[df["Project"] == p].copy()
        agg = sub.groupby("Original_Story")["Total_Score"].mean().sort_values()
        candidates = []
        if len(agg) > 0:
            candidates.append(agg.index[0])
        if len(agg) > 2:
            candidates.append(agg.index[len(agg)//2])
        if len(agg) > 1:
            candidates.append(agg.index[-1])

        # keep unique, limit per project
        chosen = []
        for s in candidates:
            if s not in chosen:
                chosen.append(s)
            if len(chosen) >= stories_per_project:
                break

        # fallback if not enough
        if len(chosen) < stories_per_project:
            more = list(sub["Original_Story"].dropna().unique())
            for s in more:
                if s not in chosen:
                    chosen.append(s)
                if len(chosen) >= stories_per_project:
                    break

        stories.extend([(p, s) for s in chosen])

    return projects, stories

def main():
    df = pd.read_excel(MASTER)

    # basic clean
    df = df[df["Model"].notna() & df["Project"].notna() & df["Original_Story"].notna()].copy()

    # Ensure numeric
    df["Total_Score"] = pd.to_numeric(df["Total_Score"], errors="coerce")

    projects, project_story_pairs = pick_projects_and_stories(df, projects_n=3, stories_per_project=2)

    # Filter down to chosen stories
    chosen_stories = [s for _, s in project_story_pairs]
    df_small = df[df["Original_Story"].isin(chosen_stories) & df["Project"].isin(projects)].copy()

    # TABLE A: scores only
    cols_scores = [c for c in META_COLS if c in df_small.columns]
    for c in CRITERIA:
        sc = score_col(c)
        if sc in df_small.columns:
            cols_scores.append(sc)

    table_scores = df_small[cols_scores].sort_values(["Project", "Original_Story", "Model"])
    table_scores.to_excel(OUT_DIR / "Table_Scoring_Examples_ScoresOnly.xlsx", index=False)

    # TABLE B: scores + extracted text evidence
    cols_ev = [c for c in META_COLS if c in df_small.columns]
    for c in CRITERIA:
        sc, tc = score_col(c), text_col(c)
        if sc in df_small.columns:
            cols_ev.append(sc)
        if tc in df_small.columns:
            cols_ev.append(tc)

    table_ev = df_small[cols_ev].sort_values(["Project", "Original_Story", "Model"])
    table_ev.to_excel(OUT_DIR / "Table_Scoring_Examples_WithEvidence.xlsx", index=False)

    # A small trace file describing which projects/stories were sampled
    trace = pd.DataFrame(project_story_pairs, columns=["Project", "Original_Story"])
    trace.to_csv(OUT_DIR / "Scoring_Examples_Trace.csv", index=False)

    print("✅ Saved:")
    print(" -", OUT_DIR / "Table_Scoring_Examples_ScoresOnly.xlsx")
    print(" -", OUT_DIR / "Table_Scoring_Examples_WithEvidence.xlsx")
    print(" -", OUT_DIR / "Scoring_Examples_Trace.csv")
    print("\nProjects used:", projects)
    print("Total unique stories sampled:", len(chosen_stories))

if __name__ == "__main__":
    main()
