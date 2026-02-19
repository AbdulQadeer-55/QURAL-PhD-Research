import pandas as pd
import os
import glob

# Point to your NEW output folder
OUTPUT_DIR = "outputs_with_text"
FINAL_FILE = "Master_QURAL_Analysis.xlsx"

def merge_all_excels():
    print("🚀 Starting Merge Process...")
    all_files = glob.glob(os.path.join(OUTPUT_DIR, "*", "*.xlsx"))
    
    if not all_files:
        print("❌ No files found! Check your directory.")
        return

    combined_df = pd.DataFrame()
    
    for file in all_files:
        try:
            df = pd.read_excel(file)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        except Exception as e:
            print(f"⚠️ Skipping bad file {file}: {e}")

    cols = list(combined_df.columns)
    first_cols = ['Model', 'Project', 'Original_Story', 'Total_Score', 'Structurally_Sound']
    
    existing_first_cols = [c for c in first_cols if c in cols]
    other_cols = [c for c in cols if c not in existing_first_cols]
    
    combined_df = combined_df[existing_first_cols + other_cols]
    
    combined_df.to_excel(FINAL_FILE, index=False)
    print(f"✅ SUCCESS! Combined {len(combined_df)} rows into '{FINAL_FILE}'")

if __name__ == "__main__":
    merge_all_excels()