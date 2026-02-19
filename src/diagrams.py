import matplotlib.pyplot as plt
import networkx as nx

g1 = nx.DiGraph()
g1.add_edges_from([
    ("Dataset", "Evaluation Engine"),
    ("Evaluation Engine", "5 LLMs"),
    ("5 LLMs", "QURAL Scoring"),
    ("QURAL Scoring", "Statistical Ranking"),
    ("Statistical Ranking", "Winning LLM")
])

pos1 = {
    "Dataset": (0, 5),
    "Evaluation Engine": (0, 4),
    "5 LLMs": (0, 3),
    "QURAL Scoring": (0, 2),
    "Statistical Ranking": (0, 1),
    "Winning LLM": (0, 0)
}

plt.figure(figsize=(8, 8))
nx.draw(g1, pos1, with_labels=True, node_size=5000, node_color="lightblue", font_size=9, font_weight="bold", arrows=True)
plt.title("Phase 1 Evaluation Architecture")
plt.margins(0.2)
plt.savefig("Architecture_Diagram.png")
plt.close()

g2 = nx.DiGraph()
g2.add_edges_from([
    ("150 Bad Stories", "GPT4o Mini"),
    ("GPT4o Mini", "Regenerate"),
    ("Regenerate", "Evaluate Score"),
    ("Evaluate Score", "Check Score"),
    ("Check Score", "GPT4o Mini"),
    ("Check Score", "Final Perfect Story")
])

pos2 = {
    "150 Bad Stories": (0, 5),
    "GPT4o Mini": (0, 4),
    "Regenerate": (0, 3),
    "Evaluate Score": (0, 2),
    "Check Score": (0, 1),
    "Final Perfect Story": (1, 1)
}

plt.figure(figsize=(8, 8))
nx.draw(g2, pos2, with_labels=True, node_size=5000, node_color="lightgreen", font_size=9, font_weight="bold", arrows=True)
plt.title("Phase 2 Iterative Loop Process Flow")
plt.margins(0.2)
plt.savefig("Process_Flow.png")
print("diagrams saved successfully")