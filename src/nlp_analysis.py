import pandas as pd
from bert_score import score
from nltk.translate.bleu_score import sentence_bleu
import nltk
import numpy as np

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

FILE_PATH = "Master_QURAL_Analysis.xlsx"

def calculate_nlp_metrics():
    print("📂 Loading Master Dataset...")
    try:
        df = pd.read_excel(FILE_PATH)
    except:
        print("❌ Master file not found. Please zip/unzip or check path.")
        return

    print("🤖 Filtering data for GPT-4o-Mini vs Llama-3.1-70B...")
    
    gpt_df = df[df['Model'] == 'GPT-4o-Mini'][['Original_Story', 'Reasoning']].rename(columns={'Reasoning': 'GPT_Reasoning'})
    llama_df = df[df['Model'] == 'Llama-3.1-70B'][['Original_Story', 'Reasoning']].rename(columns={'Reasoning': 'Llama_Reasoning'})

    merged = pd.merge(gpt_df, llama_df, on='Original_Story', how='inner')
    
    sample = merged.head(50) 
    print(f"📊 Analyzing {len(sample)} pairs of reasoning...")

    refs = sample['GPT_Reasoning'].tolist()
    cands = sample['Llama_Reasoning'].tolist()

    print("   ...Calculating BERTScore (Deep Learning)...")
    P, R, F1 = score(cands, refs, lang="en", verbose=True)
    bert_mean = F1.mean().item()

    print("   ...Calculating BLEU Score (Lexical)...")
    bleu_scores = []
    for ref, cand in zip(refs, cands):
        ref_tokens = nltk.word_tokenize(ref)
        cand_tokens = nltk.word_tokenize(cand)
        b_score = sentence_bleu([ref_tokens], cand_tokens)
        bleu_scores.append(b_score)
    bleu_mean = np.mean(bleu_scores)

    print("\n" + "="*40)
    print("🧪 INTER-MODEL AGREEMENT RESULTS")
    print("="*40)
    print(f"Comparison: GPT-4o (Reasoning) vs Llama-3 (Reasoning)")
    print("-" * 40)
    print(f"🔹 BERTScore (Semantic): {bert_mean:.4f}")
    print(f"   (0.0 = Different Meaning, 1.0 = Same Meaning)")
    print("-" * 40)
    print(f"🔹 BLEU Score (Lexical):  {bleu_mean:.4f}")
    print(f"   (0.0 = Different Words, 1.0 = Exact Same Words)")
    print("="*40)
    
    if bert_mean < 0.85:
        print("\n📢 FINDING: The BERTScore is LOW (<0.85).")
        print("   This proves the models have DIFFERENT reasoning logic.")
        print("   This validates the 'Subjectivity Hypothesis'.")
    else:
        print("\n📢 FINDING: The BERTScore is HIGH.")
        print("   The models largely agree in their reasoning.")

if __name__ == "__main__":
    calculate_nlp_metrics()