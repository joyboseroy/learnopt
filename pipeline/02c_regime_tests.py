#!/usr/bin/env python3
import json
import numpy as np
import pandas as pd

SKILLS = ["S1", "S2", "S3", "S4", "S5"]

records = [json.loads(l) for l in open("tagged_merged.jsonl")]
df = pd.DataFrame([{
    "year": r["paper_year"],
    "skill": r["tag"]["skill"],
} for r in records])

def kl_div(p, q, eps=1e-6):
    p = np.array(p) + eps
    q = np.array(q) + eps
    p, q = p / p.sum(), q / q.sum()
    return float(np.sum(p * np.log(p / q)))

def year_dist(d, year):
    sub = d[d['year'] == year]
    counts = sub['skill'].value_counts().reindex(SKILLS, fill_value=0).values
    return counts, len(sub)

rng = np.random.default_rng(42)
n_perm = 10000

def perm_test(y1, y2, label):
    c1, n1 = year_dist(df, y1)
    c2, n2 = year_dist(df, y2)
    observed_kl = kl_div(c1 / n1, c2 / n2)
    pooled = pd.concat([df[df['year'] == y1], df[df['year'] == y2]])
    pooled_skills = pooled['skill'].values
    null_kls = []
    for _ in range(n_perm):
        perm = rng.permutation(pooled_skills)
        g1, g2 = perm[:n1], perm[n1:]
        cc1 = pd.Series(g1).value_counts().reindex(SKILLS, fill_value=0).values
        cc2 = pd.Series(g2).value_counts().reindex(SKILLS, fill_value=0).values
        null_kls.append(kl_div(cc1 / max(cc1.sum(),1), cc2 / max(cc2.sum(),1)))
    null_kls = np.array(null_kls)
    p_value = (null_kls >= observed_kl).mean()
    print(f"{label}: KL={observed_kl:.4f} (n{y1}={n1}, n{y2}={n2}), "
          f"null mean={null_kls.mean():.4f}, p={p_value:.4f}")
    return observed_kl, p_value

print("="*60)
print("Direct comparisons (skipping/including noisy 2022)")
print("="*60)
perm_test(2021, 2023, "2021 -> 2023 (skip 2022)")
perm_test(2021, 2022, "2021 -> 2022")
perm_test(2022, 2023, "2022 -> 2023 (rerun)")
perm_test(2016, 2023, "2016 -> 2023 (earliest vs post-shift)")

print("\n" + "="*60)
print("2016-2021 pooled vs 2023-2024 pooled (regime vs regime)")
print("="*60)
regime1 = df[df['year'].between(2016, 2021)]
regime2 = df[df['year'].between(2023, 2024)]
c1 = regime1['skill'].value_counts().reindex(SKILLS, fill_value=0).values
c2 = regime2['skill'].value_counts().reindex(SKILLS, fill_value=0).values
n1, n2 = len(regime1), len(regime2)
observed_kl = kl_div(c1/n1, c2/n2)
print(f"2016-2021 (n={n1}) vs 2023-2024 (n={n2}): KL = {observed_kl:.4f}")

pooled = pd.concat([regime1, regime2])
pooled_skills = pooled['skill'].values
null_kls = []
for _ in range(n_perm):
    perm = rng.permutation(pooled_skills)
    g1, g2 = perm[:n1], perm[n1:]
    cc1 = pd.Series(g1).value_counts().reindex(SKILLS, fill_value=0).values
    cc2 = pd.Series(g2).value_counts().reindex(SKILLS, fill_value=0).values
    null_kls.append(kl_div(cc1/max(cc1.sum(),1), cc2/max(cc2.sum(),1)))
null_kls = np.array(null_kls)
p_value = (null_kls >= observed_kl).mean()
print(f"Null mean={null_kls.mean():.4f}, 95th pct={np.percentile(null_kls,95):.4f}")
print(f"Permutation p = {p_value:.4f}")
