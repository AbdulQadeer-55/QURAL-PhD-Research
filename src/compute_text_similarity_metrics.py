import pandas as pd
import numpy as np
from pathlib import Path

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer
from bert_score import score as bertscore

import nltk
nltk.download("punkt", quiet=True)

MASTER = "Master_QURAL_Analysis.xlsx"
OUT_DIR = Path("outputs/analysis_text_metrics")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CRITERIA = [
    "Task Identification",
    "Task Nature",
    "Role Identification",
    "Acceptance Criteria",
    "Dependency",
    "Business Need",
    "Priority",
    "Quality Requirement",
    "Estimable",
    "Unambiguous",
    "Well Formed",
    "Problem Oriented",
    "Unique",
    "Testable",
]

def build_evidence_text(row):
    parts = []
    for c in CRITERIA:
        col = f"{c}_Text"
        if col in row and pd.notna(row[col]):
            t = str(row[col]).strip()
            if t and t.lower() != "n/a":
                parts.append(t)
    return " | ".join(parts).strip()

def cosine_tfidf(texts_a, texts_b):
    # lightweight cosine similarity using TF-IDF (works offline, no external APIs)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vec = TfidfVectorizer(min_df=1)
    X = vec.fit_transform(list(texts_a) + list(texts_b))
    A = X[:len(texts_a)]
    B = X[len(texts_a):]
    sims = cosine_similarity(A, B).diagonal()
    return sims

def pairwise_metrics(refs, cands):
    # BLEU
    smooth = SmoothingFunction().method1
    bleu_vals = []
    for r, c in zip(refs, cands):
        r_tok = nltk.word_tokenize(r)
        c_tok = nltk.word_tokenize(c)
        bleu_vals.append(sentence_bleu([r_tok], c_tok, smoothing_function=smooth))
    bleu = float(np.mean(bleu_vals))

    # METEOR
    meteor_vals = []
    for r, c in zip(refs, cands):
        meteor_vals.append(meteor_score([nltk.word_tokenize(r)], nltk.word_tokenize(c)))
    meteor = float(np.mean(meteor_vals))

    # ROUGE-L
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    rouge_vals = []
    for r, c in zip(refs, cands):
        rouge_vals.append(scorer.score(r, c)["rougeL"].fmeasure)
    rougeL = float(np.mean(rouge_vals))

    # BERTScore
    P, R, F1 = bertscore(cands, refs, lang="en", verbose=False)
    bert = float(F1.mean().item())

    # Cosine (TF-IDF)
    cos_vals = cosine_tfidf(refs, cands)
    cos = float(np.mean(cos_vals))

    return {
        "BLEU": bleu,
        "METEOR": meteor,
        "ROUGE_L": rougeL,
        "BERTScore_F1": bert,
        "Cosine_TFIDF": cos
    }

def main():
    df = pd.read_excel(MASTER)
    df = df[df["Model"].notna() & df["Original_Story"].notna()].copy()

    # build evidence text column
    df["Evidence_Text"] = df.apply(build_evidence_text, axis=1)

    # pivot: story x model -> evidence text
    pivot = df.pivot_table(index="Original_Story", columns="Model", values="Evidence_Text", aggfunc="first")

    # keep only stories present for all models
    pivot = pivot.dropna()
    models = list(pivot.columns)

    metrics_names = ["BLEU", "METEOR", "ROUGE_L", "BERTScore_F1", "Cosine_TFIDF"]
    matrices = {m: pd.DataFrame(index=models, columns=models, dtype=float) for m in metrics_names}

    for i, m1 in enumerate(models):
        for j, m2 in enumerate(models):
            if i == j:
                for mn in metrics_names:
                    matrices[mn].loc[m1, m2] = 1.0
                continue

            refs = pivot[m1].astype(str).tolist()
            cands = pivot[m2].astype(str).tolist()

            res = pairwise_metrics(refs, cands)
            for mn in metrics_names:
                matrices[mn].loc[m1, m2] = res[mn]

    # save
    out_xlsx = OUT_DIR / "Text_Similarity_Matrices.xlsx"
    with pd.ExcelWriter(out_xlsx) as xw:
        for mn, mat in matrices.items():
            mat.to_excel(xw, sheet_name=mn)

    print("✅ Saved:", out_xlsx)
    print("Stories compared (complete across all models):", pivot.shape[0])

if __name__ == "__main__":
    main()
