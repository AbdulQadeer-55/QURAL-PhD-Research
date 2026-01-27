# src/main.py
import os
import pandas as pd
from tqdm import tqdm
from prompts import get_evaluation_prompt
from llm_engine import call_llm, MODELS  # Import the list of models
from evaluator import analyze_structural_quality

DATA_DIR = "datasets"
BASE_OUTPUT_DIR = "outputs"

def process_datasets():
    # 1. Find CSV Files
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    
    if not files:
        print("❌ No CSV files found in 'datasets/'")
        return

    # 2. OUTER LOOP: Iterate through all 5 Models
    for model_name in MODELS.keys():
        print(f"\n==========================================")
        print(f"🤖 STARTING EVALUATION WITH: {model_name}")
        print(f"==========================================")
        
        # Create a specific folder for this model's results
        model_output_dir = os.path.join(BASE_OUTPUT_DIR, model_name)
        os.makedirs(model_output_dir, exist_ok=True)

        # 3. INNER LOOP: Iterate through all 15 Projects
        for file in files:
            project_name = file.split(' - ')[-1].replace('.csv', '').strip()
            output_path = os.path.join(model_output_dir, f"Evaluated_{project_name}.xlsx")
            
            # Skip if already done (Resume capability)
            if os.path.exists(output_path):
                print(f"⏩ {project_name} already done for {model_name}. Skipping...")
                continue

            print(f"   📂 Processing Project: {project_name}...")
            
            # Load Data
            input_path = os.path.join(DATA_DIR, file)
            try:
                df = pd.read_csv(input_path, encoding='utf-8')
            except:
                df = pd.read_csv(input_path, encoding='ISO-8859-1')

            results = []
            
            # --- TEST MODE: LIMIT TO 2 STORIES ---
            # Remove .head(2) when ready for full production run
            for index, row in tqdm(df.head(2).iterrows(), total=2, desc=f"   Processing {project_name}"):
                
                # Find Story Column
                user_story = ""
                for col in df.columns:
                    if "story" in col.lower() or "content" in col.lower():
                        user_story = row[col]
                        break
                if not user_story and not df.empty: user_story = row.iloc[0]

                if not isinstance(user_story, str) or len(user_story) < 10:
                    continue

                # --- AI CALL ---
                prompt = get_evaluation_prompt(user_story)
                
                # Call the specific model in the loop
                response = call_llm(prompt, model_friendly_name=model_name)
                
                if response:
                    scores = response.get('scores', {})
                    total = response.get('total_score', 0)
                    t1, t2, sound = analyze_structural_quality(scores)
                    
                    row_data = {
                        "Original_Story": user_story,
                        "Total_Score": total,
                        "Structurally_Sound": sound,
                        "Tier_1_Score": t1,
                        "Tier_2_Score": t2,
                        "Reasoning": response.get('reasoning', '')
                    }
                    row_data.update(scores)
                    results.append(row_data)

            # Save Results for this Model + Project
            if results:
                pd.DataFrame(results).to_excel(output_path, index=False)

if __name__ == "__main__":
    process_datasets()