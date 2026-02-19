import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

FILE_NAME = "Master_QURAL_Analysis.xlsx"

def create_charts():
    try:
        df = pd.read_excel(FILE_NAME)
    except:
        print("Master file not found. Run merge_results.py first!")
        return

    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='Model', y='Total_Score', palette='viridis')
    plt.title('Average Quality Score by AI Model (QURAL Framework)', fontsize=14)
    plt.ylabel('Average Score (0-28)')
    plt.xlabel('AI Model')
    plt.ylim(0, 28)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig('Visual_Model_Comparison.png')
    print("Generated 'Visual_Model_Comparison.png'")

if __name__ == "__main__":
    create_charts()