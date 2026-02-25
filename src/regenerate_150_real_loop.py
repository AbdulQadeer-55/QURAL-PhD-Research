# src/regenerate_150_real_loop.py

import pandas as pd
from pathlib import Path
from llm_engine import call_llm
from prompts import get_evaluation_prompt
from evaluator import analyze_structural_quality
from regeneration_prompt import get_regeneration_prompt

MASTER = "Master_QURAL_Analysis.xlsx"
SHORTLIST = "Shortlisted_150_Bad_Stories.csv"

OUT_DIR = Path("outputs/regeneration_real")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 🔧 Model Strategy
REGEN_MODEL = "Llama-3.1-70B"
JUDGE_MODEL = "Claude-3-Haiku"

# 🔧 Optimized Settings
MAX_ITERS = 2
THRESH_TOTAL = 22
THRESH_TIER1 = 8
THRESH_AC = 1


def simplify_scores(evals: dict):
    simple = {}
    for k, v in evals.items():
        if isinstance(v, dict):
            simple[k] = int(v.get("score", 0) or 0)
        elif isinstance(v, (int, float)):
            simple[k] = int(v)
        else:
            try:
                simple[k] = int(str(v))
            except:
                simple[k] = 0
    return simple


def judge_story(story_text: str):
    prompt = get_evaluation_prompt(story_text)
    resp = call_llm(prompt, model_friendly_name=JUDGE_MODEL)

    if not resp:
        return None

    evals = resp.get("evaluations", {})
    total = resp.get("total_score", 0)
    simple = simplify_scores(evals)

    t1, t2, sound = analyze_structural_quality(simple)
    ac = simple.get("Acceptance Criteria", 0)

    return {
        "total": int(total or 0),
        "tier1": int(t1),
        "tier2": int(t2),
        "ac": int(ac),
        "sound": bool(sound),
    }


def main():
    master = pd.read_excel(MASTER)
    shortlist = pd.read_csv(SHORTLIST)

    old_scores = master.drop_duplicates("Original_Story") \
        .set_index("Original_Story")["Total_Score"].to_dict()

    stories = shortlist["Defective User Story"].tolist() \
        if "Defective User Story" in shortlist.columns \
        else shortlist.iloc[:, 0].tolist()

    trace_rows = []
    final_rows = []

    for idx, story in enumerate(stories, start=1):

        original = str(story)
        old_score = int(old_scores.get(original, 0) or 0)

        baseline = judge_story(original)
        if baseline:
            best_total = baseline["total"]
        else:
            best_total = old_score

        best_story = original
        stop_reason = "no_improvement"

        current_story = original
        prev_score = best_total

        for iteration in range(1, MAX_ITERS + 1):

            regen_prompt = get_regeneration_prompt(current_story)
            regen_resp = call_llm(regen_prompt, model_friendly_name=REGEN_MODEL)

            if not regen_resp or "regenerated_story" not in regen_resp:
                stop_reason = "regen_failed"
                break

            candidate = str(regen_resp["regenerated_story"])
            judged = judge_story(candidate)

            if not judged:
                stop_reason = "judge_failed"
                break

            new_score = judged["total"]
            improvement = new_score - prev_score

            trace_rows.append({
                "Index": idx,
                "Iteration": iteration,
                "Old_Score": old_score,
                "Previous_Score": prev_score,
                "New_Score": new_score,
                "Improvement": improvement,
                "Tier1": judged["tier1"],
                "Tier2": judged["tier2"],
                "AC_Score": judged["ac"],
                "Structurally_Sound": judged["sound"],
                "Original_Story": original,
                "Candidate_Story": candidate
            })

            # If improved, update best
            if new_score > best_total:
                best_total = new_score
                best_story = candidate

            # Stop if threshold reached
            if (new_score >= THRESH_TOTAL and
                judged["tier1"] >= THRESH_TIER1 and
                judged["ac"] >= THRESH_AC):
                stop_reason = f"threshold_met_iter{iteration}"
                break

            # Stop if no improvement
            if improvement <= 0:
                stop_reason = f"no_improvement_iter{iteration}"
                break

            prev_score = new_score
            current_story = candidate

        final_rows.append({
            "Index": idx,
            "Original_Story": original,
            "Old_Score": old_score,
            "Final_Score": best_total,
            "Score_Improvement": best_total - old_score,
            "Final_Story": best_story,
            "Stop_Reason": stop_reason
        })

        print(f"[{idx}/{len(stories)}] Old={old_score} → Final={best_total} | Δ={best_total - old_score} | {stop_reason}")

    trace_df = pd.DataFrame(trace_rows)
    final_df = pd.DataFrame(final_rows)

    trace_df.to_excel(OUT_DIR / "Regeneration_Trace_150.xlsx", index=False)
    final_df.to_excel(OUT_DIR / "Regeneration_Final_150.xlsx", index=False)

    print("\n✅ Saved:")
    print(" - Regeneration_Trace_150.xlsx")
    print(" - Regeneration_Final_150.xlsx")


if __name__ == "__main__":
    main()