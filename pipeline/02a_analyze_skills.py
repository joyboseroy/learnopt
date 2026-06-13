#!/usr/bin/env python3
"""
LearnOpt Section 4.2/4.3 analysis.
Reads tagged_full.jsonl and produces:
- error/quality check
- skill distribution by year (Table 1 / Figure 1 data)
- per-category variance across years
- KL divergence between consecutive years
- skill distribution by subject
"""

import json
import pandas as pd
import numpy as np
from collections import Counter

SKILLS = ["S1", "S2", "S3", "S4", "S5"]

rows = []
errors = []
generic_evidence = 0

for line in open("tagged_full.jsonl"):
    r = json.loads(line)
    tag = r["tag"]
    if "error" in tag:
        errors.append(r)
        continue
    skill = tag.get("skill", "").strip()
    if skill not in SKILLS:
        errors.append(r)
        continue
    ev = tag.get("skill_evidence", "").lower()
    if ("combining knowledge from" in ev and "distinct" in ev) or \
       ("requires" in ev and "knowledge" in ev and len(ev) < 60):
        generic_evidence += 1
    rows.append({
        "index": r["index"],
        "year": r["paper_year"],
        "subject": r["paper_subject"],
        "skill": skill,
        "difficulty": tag.get("difficulty"),
        "chapter": tag.get("chapter"),
        "topic": tag.get("topic"),
    })

df = pd.DataFrame(rows)
print(f"Total tagged: {len(rows)} / 1496")
print(f"Errors / unparseable: {len(errors)}")
print(f"Likely-generic evidence strings: {generic_evidence} ({100*generic_evidence/len(rows):.1f}%)")
if errors:
    print("\nFirst few errors:")
    for e in errors[:5]:
        print(e["index"], e["tag"])

# ---- Skill distribution by year ----
print("\n" + "="*60)
print("SKILL DISTRIBUTION BY YEAR (% of questions per category)")
print("="*60)
pivot = pd.crosstab(df["year"], df["skill"], normalize="index") * 100
pivot = pivot.reindex(columns=SKILLS, fill_value=0).round(1)
print(pivot)

# Sample sizes per year
print("\nQuestions per year:")
print(df["year"].value_counts().sort_index())

# ---- Per-category variance / range across years ----
print("\n" + "="*60)
print("PER-CATEGORY STABILITY ACROSS YEARS")
print("="*60)
stats = pivot.agg(["mean", "std", "min", "max"]).round(2)
stats.loc["range"] = stats.loc["max"] - stats.loc["min"]
print(stats)
print("\n(Paper claims stability if 'range' < 5 percentage points)")

# ---- KL divergence between consecutive years ----
print("\n" + "="*60)
print("KL DIVERGENCE BETWEEN CONSECUTIVE YEARS")
print("="*60)
years = sorted(pivot.index)

def kl_div(p, q, eps=1e-6):
    p = np.array(p) / 100 + eps
    q = np.array(q) / 100 + eps
    p = p / p.sum()
    q = q / q.sum()
    return float(np.sum(p * np.log(p / q)))

for i in range(len(years) - 1):
    y1, y2 = years[i], years[i+1]
    kl = kl_div(pivot.loc[y1].values, pivot.loc[y2].values)
    print(f"{y1} -> {y2}: KL = {kl:.4f}")

# ---- KL divergence between subjects (for comparison) ----
print("\n" + "="*60)
print("SKILL DISTRIBUTION BY SUBJECT")
print("="*60)
pivot_subj = pd.crosstab(df["subject"], df["skill"], normalize="index") * 100
pivot_subj = pivot_subj.reindex(columns=SKILLS, fill_value=0).round(1)
print(pivot_subj)

print("\nKL divergence between subjects (pairwise):")
subjects = list(pivot_subj.index)
for i in range(len(subjects)):
    for j in range(i+1, len(subjects)):
        s1, s2 = subjects[i], subjects[j]
        kl = kl_div(pivot_subj.loc[s1].values, pivot_subj.loc[s2].values)
        print(f"{s1} vs {s2}: KL = {kl:.4f}")

# ---- Save outputs ----
pivot.to_csv("skill_distribution_by_year.csv")
pivot_subj.to_csv("skill_distribution_by_subject.csv")
df.to_csv("tagged_full_parsed.csv", index=False)
print("\nSaved: skill_distribution_by_year.csv, skill_distribution_by_subject.csv, tagged_full_parsed.csv")
