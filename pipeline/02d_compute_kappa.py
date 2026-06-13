#!/usr/bin/env python3
"""Section 4.2 fallback: inter-model agreement (kappa) on the 136 questions
tagged by both qwen2.5:7b (tagged_fill.jsonl, original) and
llama-3.1-8b-instant (tagged_retag.jsonl, the retag)."""

import json
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

SKILLS = ["S1", "S2", "S3", "S4", "S5"]

qwen = {}
for line in open("tagged_fill.jsonl"):
    r = json.loads(line)
    if "error" not in r["tag"]:
        qwen[r["index"]] = r["tag"]["skill"]

llama = {}
for line in open("tagged_retag.jsonl"):
    r = json.loads(line)
    if "error" not in r["tag"]:
        llama[r["index"]] = r["tag"]["skill"]

common = sorted(set(qwen.keys()) & set(llama.keys()))
print(f"Questions tagged by both models: {len(common)}")

qwen_labels = [qwen[i] for i in common]
llama_labels = [llama[i] for i in common]

kappa = cohen_kappa_score(qwen_labels, llama_labels, labels=SKILLS)
print(f"\nCohen's kappa (qwen2.5:7b vs llama-3.1-8b-instant): {kappa:.4f}")

agreement = sum(a == b for a, b in zip(qwen_labels, llama_labels)) / len(common)
print(f"Raw agreement: {agreement:.4f} ({sum(a==b for a,b in zip(qwen_labels,llama_labels))}/{len(common)})")

print("\nConfusion matrix (rows=qwen, cols=llama):")
cm = confusion_matrix(qwen_labels, llama_labels, labels=SKILLS)
cm_df = pd.DataFrame(cm, index=[f"qwen_{s}" for s in SKILLS], columns=[f"llama_{s}" for s in SKILLS])
print(cm_df)

print("\nDisagreement breakdown:")
disagreements = [(qwen_labels[i], llama_labels[i]) for i in range(len(common)) if qwen_labels[i] != llama_labels[i]]
from collections import Counter
print(Counter(disagreements))

# Kappa interpretation
print("\nInterpretation (Landis & Koch 1977):")
if kappa < 0: interp = "poor"
elif kappa < 0.20: interp = "slight"
elif kappa < 0.40: interp = "fair"
elif kappa < 0.60: interp = "moderate"
elif kappa < 0.80: interp = "substantial"
else: interp = "almost perfect"
print(f"kappa={kappa:.3f} -> {interp} agreement")
