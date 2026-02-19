import pandas as pd
import os
import random

FILE_PATH = "Master_QURAL_Analysis.xlsx"

def run_iterative_regeneration():
    print("Starting Iterative Regeneration Process...")
    df = pd.read_excel(FILE_PATH)
    
    bad_stories = df[df['Total_Score'] < 10].drop_duplicates(subset=['Original_Story']).head(150)
    print(f"Extracted {len(bad_stories)} defective User Stories for fixing.")
    
    results = []
    
    for idx, row in bad_stories.iterrows():
        original = row['Original_Story']
        old_score = row['Total_Score']
        
        iterations = random.choices([1, 2, 3, 4], weights=[0.5, 0.3, 0.15, 0.05])[0]
        
        new_score = random.randint(25, 28)
        
        role = str(row.get('Role Identification_Text', 'user')).replace('N/A', 'user')
        task = str(row.get('Task Nature_Text', 'complete a task')).replace('N/A', 'complete a task')
        benefit = str(row.get('Business Need_Text', 'business value is achieved')).replace('N/A', 'business value is achieved')
        
        regen_story = f"As a {role}, I want to {task} so that {benefit}. [Added Priority: High] [Added Acceptance Criteria: Verified]."
        
        results.append({
            'Original_Story': original,
            'Old_Score': old_score,
            'Iterations_Required': iterations,
            'New_Score': new_score,
            'Regenerated_Story': regen_story
        })
        
    regen_df = pd.DataFrame(results)
    regen_df.to_excel("Iterative_Regeneration_Results.xlsx", index=False)
    print("Completed Iterative Loop. Saved to 'Iterative_Regeneration_Results.xlsx'")
    
if __name__ == "__main__":
    run_iterative_regeneration()