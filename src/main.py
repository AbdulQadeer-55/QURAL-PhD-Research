# src/main.py
import os
import pandas as pd
from tqdm import tqdm
from prompts import get_evaluation_prompt
from llm_engine import call_llm
from evaluator import analyze_structural_quality

# Define paths
DATA_FILE = "datasets/User_Stories_Combined.xlsx"  # The single Excel file
OUTPUT_DIR = "outputs"

def process_datasets():
    # 1. Check if file exists
    if not os.path.exists(DATA_FILE):
        print(f"❌ Error: File not found at {DATA_FILE}")
        print("Please make sure the client's Excel file is renamed to 'User_Stories_Combined.xlsx' and inside the 'datasets' folder.")
        return

    print(f"📂 Loading Excel file: {DATA_FILE}...")
    
    # 2. Read ALL sheets at once (sheet_name=None returns a Dictionary of sheets)
    all_sheets = pd.read_excel(DATA_FILE, sheet_name=None)
    
    print(f"✅ Found {len(all_sheets)} Datasets (Sheets) inside the file.")

    # 3. Loop through each sheet (Project)
    for sheet_name, df in all_sheets.items():
        print(f"\n🚀 Processing Project: {sheet_name}...")
        
        results = []
        
        # LIMIT TO 2 STORIES FOR TEST (Remove .head(2) later for full run)
        # for index, row in tqdm(df.iterrows(), total=len(df)): # <--- USE THIS FOR FULL RUN
        for index, row in tqdm(df.head(2).iterrows(), total=2): # <--- CURRENTLY IN TEST MODE
            
            # Detect the column containing the story (Handle different column names)
            possible_cols = ['User Story', 'Story', 'Content', 'story']
            user_story = ""
            for col in possible_cols:
                if col in df.columns:
                    user_story = row[col]
                    break
            
            # Skip empty rows
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
                
                # Prepare Row Data
                row_data = {
                    "Original_Story": user_story,
                    "Total_Score": total,
                    "Structurally_Sound": is_sound,
                    "Tier_1_Score": t1_score,
                    "Tier_2_Score": t2_score,
                    "Reasoning": response.get('reasoning', '')
                }
                row_data.update(scores) # Add the 14 individual scores
                results.append(row_data)

        # 4. Save Individual Excel for this Project
        if results:
            output_path = f"{OUTPUT_DIR}/Evaluated_{sheet_name}.xlsx"
            pd.DataFrame(results).to_excel(output_path, index=False)
            print(f"   💾 Saved results to: {output_path}")

if __name__ == "__main__":
    process_datasets()