import os
import pandas as pd
from evaluator import calculate_weighted_score

DATA_DIR = "datasets"
OUTPUT_DIR = "outputs"

def process_all_datasets():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    
    for file in files:
        file_path = os.path.join(DATA_DIR, file)
        df = pd.read_csv(file_path)
        
        print(f"Processing {file}...")
        
        results = []
        
        for index, row in df.iterrows():
            story_text = row.get('User Story', '')
            
            mock_scores = {
                "Role Identification": 2,
                "Acceptance Criteria": 1,
                "Task Nature": 2
            }
            
            total, sound = calculate_weighted_score(mock_scores)
            
            results.append({
                "Story": story_text,
                "Total_Score": total,
                "Structurally_Sound": sound
            })
            
        output_df = pd.DataFrame(results)
        output_df.to_excel(f"{OUTPUT_DIR}/Evaluated_{file}.xlsx", index=False)

if __name__ == "__main__":
    process_all_datasets()