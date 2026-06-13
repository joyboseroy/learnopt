#!/usr/bin/env python3
import json
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

SKILLS = ["S1", "S2", "S3", "S4", "S5"]

records = [json.loads(l) for l in open("tagged_merged.jsonl")]
df = pd.DataFrame([{
    "year": r["paper_year"],
    "skill": r["tag"]["skill"],
    "tagger": r["tagger"],
} for r in records])

# ---- 1. Chi-square: tagger architecture vs assigned skill ----
print("="*60)
print("1. CHI-SQUARE: tagger model vs assigned skill category")
print("="*60)
# Collapse to two groups: groq (llama) vs ollama (qwen)
df['tagger_group'] = df['tagger'].apply(lambda x: 'groq-llama' if 'groq' in x else 'ollama-qwen')
print(df['tagger_group'].value_counts())

ct = pd.crosstab(df['tagger_group'], df['skill'])
print("\nContingency table:")
print(ct)

chi2, p, dof, expected = chi2_contingency(ct)
print(f"\nChi-square = {chi2:.4f}, dof = {dof}, p = {p:.4f}")
if p > 0.05:
    print("-> No significant relationship between tagger model and skill category (p > 0.05)")
else:
    print("-> WARNING: significant relationship detected -- tagger choice may bias results")

# ---- 2. Permutation test: is 2022->2023 KL divergence unusual? ----
print("\n" + "="*60)
print("2. PERMUTATION TEST: 2022->2023 KL divergence")
print("="*60)

def kl_div(p, q, eps=1e-6):
    p = np.array(p) + eps
    q = np.array(q) + eps
    p, q = p / p.sum(), q / q.sum()
    return float(np.sum(p * np.log(p / q)))

def year_dist(d, year):
    sub = d[d['year'] == year]
    counts = sub['skill'].value_counts().reindex(SKILLS, fill_value=0).values
    return counts, len(sub)

# Observed KL for 2022->2023
c22, n22 = year_dist(df, 2022)
c23, n23 = year_dist(df, 2023)
observed_kl = kl_div(c22 / n22, c23 / n23)
print(f"Observed 2022->2023 KL = {observed_kl:.4f} (n22={n22}, n23={n23})")

# Null distribution: pool 2022+2023 questions, randomly split into groups
# of size n22/n23, compute KL, repeat
pooled = pd.concat([df[df['year'] == 2022], df[df['year'] == 2023]])
pooled_skills = pooled['skill'].values
n_total = len(pooled_skills)

n_perm = 10000
rng = np.random.default_rng(42)
null_kls = []
for _ in range(n_perm):
    perm = rng.permutation(pooled_skills)
    g1, g2 = perm[:n22], perm[n22:]
    c1 = pd.Series(g1).value_counts().reindex(SKILLS, fill_value=0).values
    c2 = pd.Series(g2).value_counts().reindex(SKILLS, fill_value=0).values
    null_kls.append(kl_div(c1 / max(c1.sum(),1), c2 / max(c2.sum(),1)))

null_kls = np.array(null_kls)
p_value = (null_kls >= observed_kl).mean()
print(f"Null distribution: mean={null_kls.mean():.4f}, 95th pct={np.percentile(null_kls,95):.4f}, max={null_kls.max():.4f}")
print(f"Permutation p-value (observed >= null): p = {p_value:.4f}")
if p_value < 0.01:
    print("-> Highly significant: 2022->2023 shift exceeds 99% of permuted shifts")
elif p_value < 0.05:
    print("-> Significant at p<0.05")
else:
    print("-> NOT significant -- shift may be within range expected from n=32 sampling noise")

# ---- 3. Sanity: same test for a "normal" within-regime transition (2016->2017) ----
print("\n" + "="*60)
print("3. SANITY CHECK: same test on 2016->2017 (in-regime, expect non-significant)")
print("="*60)
c16, n16 = year_dist(df, 2016)
c17, n17 = year_dist(df, 2017)
observed_kl_1617 = kl_div(c16 / n16, c17 / n17)
print(f"Observed 2016->2017 KL = {observed_kl_1617:.4f} (n16={n16}, n17={n17})")

pooled_1617 = pd.concat([df[df['year'] == 2016], df[df['year'] == 2017]])
pooled_skills_1617 = pooled_1617['skill'].values
null_kls_1617 = []
for _ in range(n_perm):
    perm = rng.permutation(pooled_skills_1617)
    g1, g2 = perm[:n16], perm[n16:]
    c1 = pd.Series(g1).value_counts().reindex(SKILLS, fill_value=0).values
    c2 = pd.Series(g2).value_counts().reindex(SKILLS, fill_value=0).values
    null_kls_1617.append(kl_div(c1 / max(c1.sum(),1), c2 / max(c2.sum(),1)))
null_kls_1617 = np.array(null_kls_1617)
p_1617 = (null_kls_1617 >= observed_kl_1617).mean()
print(f"Permutation p-value: p = {p_1617:.4f} (expect large, e.g. > 0.3)")
