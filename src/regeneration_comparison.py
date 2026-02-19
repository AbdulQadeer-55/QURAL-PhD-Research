import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("Iterative_Regeneration_Results.xlsx")

plt.figure(figsize=(12, 6))
plt.plot(df.index, df["Old_Score"], label="Original Score", color="red", alpha=0.6, marker="o", linestyle="")
plt.plot(df.index, df["New_Score"], label="Regenerated Score", color="green", alpha=0.8, marker="^", linestyle="")

plt.title("Regeneration Process Improvement Old vs New Scores")
plt.xlabel("User Story Sample")
plt.ylabel("QURAL Evaluation Score")
plt.legend()
plt.grid(True, alpha=0.3)

plt.savefig("Visual_Regeneration_Improvement.png")