# src/main.py
import os
import pandas as pd
from tqdm import tqdm
from prompts import get_evaluation_prompt
from llm_engine import call_llm
from evaluator import analyze_structural_quality

# Point to your single Excel file
DATA_FILE = "datasets/User_Stories_Combined.xlsx"
OUTPUT_DIR = "outputs"

def process_datasets():
    # 1. Check if the Excel file exists
    if not os.path.exists(DATA_FILE):
        print(f"❌ Error: File not found at {DATA_FILE}")
        print("Please make sure your file is named 'User_Stories_Combined.xlsx' inside the 'datasets' folder.")
        return

    print(f"📂 Loading Excel file: {DATA_FILE}...")
    
    try:
        # 2. Read ALL sheets at once (sheet_name=None gets all tabs)
        all_sheets = pd.read_excel(DATA_FILE, sheet_name=None)
        print(f"✅ Found {len(all_sheets)} Projects (Sheets) inside the file.")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return

    # 3. Loop through each Sheet (Project)
    for sheet_name, df in all_sheets.items():
        print(f"\n🚀 Processing Project: {sheet_name}...")
        
        results = []
        
        # --- TEST MODE: Process only first 2 stories per project ---
        # Change .head(2) to .head(550) or remove .head() later for the full run
        for index, row in tqdm(df.head(2).iterrows(), total=2): 
            
            # Find the story column automatically
            user_story = ""
            for col in df.columns:
                if isinstance(col, str) and ("story" in col.lower() or "content" in col.lower()):
                    user_story = row[col]
                    break
            
            # Fallback: Use the first column if no "story" header found
            if not user_story and not df.empty:
                user_story = row.iloc[0]

            # Validation: Skip empty or too short rows
            if not isinstance(user_story, str) or len(user_story) < 10:
                continue

            # --- AI PROCESSING ---
            prompt = get_evaluation_prompt(user_story)
            response = call_llm(prompt)
            
            if response:
                scores = response.get('scores', {})
                total = response.get('total_score', 0)
                
                # Weighted Analysis (Tier 1 vs Tier 2)
                t1_score, t2_score, is_sound = analyze_structural_quality(scores)
                
                row_data = {
                    "Original_Story": user_story,
                    "Total_Score": total,
                    "Structurally_Sound": is_sound,
                    "Tier_1_Score": t1_score,
                    "Tier_2_Score": t2_score,
                    "Reasoning": response.get('reasoning', '')
                }
                row_data.update(scores) # Add the 14 scores
                results.append(row_data)

        # 4. Save Individual Excel File for this Project
        if results:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            # Create a safe filename (remove spaces/special chars)
            safe_name = "".join([c if c.isalnum() else "_" for c in sheet_name])
            output_path = f"{OUTPUT_DIR}/Evaluated_{safe_name}.xlsx"
            
            pd.DataFrame(results).to_excel(output_path, index=False)
            print(f"   💾 Saved results to: {output_path}")

if __name__ == "__main__":
    process_datasets()