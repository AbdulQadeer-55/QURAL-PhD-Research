# src/main.py
import os
import pandas as pd
from tqdm import tqdm
from prompts import get_evaluation_prompt
from llm_engine import call_llm, MODELS
from evaluator import analyze_structural_quality

DATA_FILE = "datasets/User_Stories_Combined.xlsx"
BASE_OUTPUT_DIR = "outputs_with_text"

def process_datasets():
    if not os.path.exists(DATA_FILE):
        print(f"❌ Error: File not found at {DATA_FILE}")
        return

    print(f"📂 Loading Excel file: {DATA_FILE}...")
    try:
        all_sheets = pd.read_excel(DATA_FILE, sheet_name=None)
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return

    for model_name in MODELS.keys():
        print(f"\n==========================================")
        print(f"🤖 EXTRACTING WITH: {model_name}")
        print(f"==========================================")
        
        model_output_dir = os.path.join(BASE_OUTPUT_DIR, model_name)
        os.makedirs(model_output_dir, exist_ok=True)

        for sheet_name, df in all_sheets.items():
            safe_name = "".join([c if c.isalnum() else "_" for c in sheet_name])
            output_path = os.path.join(model_output_dir, f"Detailed_{safe_name}.xlsx")
            
            if os.path.exists(output_path):
                print(f"⏩ {sheet_name} already done. Skipping...")
                continue

            print(f"   📂 Processing {sheet_name} ({len(df)} stories)...")
            results = []
            
            for index, row in tqdm(df.iterrows(), total=len(df), desc=f"   {sheet_name}"):
                user_story = ""
                for col in df.columns:
                    if isinstance(col, str) and ("story" in col.lower() or "content" in col.lower()):
                        user_story = row[col]
                        break
                if not user_story and not df.empty: user_story = row.iloc[0]

                if not isinstance(user_story, str) or len(user_story) < 10:
                    continue

                prompt = get_evaluation_prompt(user_story)
                response = call_llm(prompt, model_friendly_name=model_name)
                
                if response:
                    evals = response.get('evaluations', {})
                    total = response.get('total_score', 0)
                    
                    simple_scores = {}
                    for k, v in evals.items():
                        if isinstance(v, dict):
                            simple_scores[k] = v.get('score', 0)
                        elif isinstance(v, (int, float)):
                            simple_scores[k] = int(v)
                        elif isinstance(v, str) and v.isdigit():
                            simple_scores[k] = int(v)
                        else:
                            simple_scores[k] = 0 

                    t1, t2, sound = analyze_structural_quality(simple_scores)
                    
                    # Build Row Data
                    row_data = {
                        "Model": model_name,
                        "Project": sheet_name,
                        "Original_Story": user_story,
                        "Total_Score": total,
                        "Structurally_Sound": sound,
                        "Tier_1_Score": t1,
                        "Tier_2_Score": t2,
                        "Reasoning": response.get('reasoning', '')
                    }
                    
                    # Add Score AND Text safely
                    for criteria, data in evals.items():
                        if isinstance(data, dict):
                            row_data[f"{criteria}_Score"] = data.get('score', 0)
                            row_data[f"{criteria}_Text"] = data.get('text', 'N/A')
                        else:
                            # Handle malformed extraction gracefully
                            row_data[f"{criteria}_Score"] = simple_scores.get(criteria, 0)
                            row_data[f"{criteria}_Text"] = "N/A (AI Format Error)"

                    results.append(row_data)

            # Save Results
            if results:
                pd.DataFrame(results).to_excel(output_path, index=False)

if __name__ == "__main__":
    process_datasets()