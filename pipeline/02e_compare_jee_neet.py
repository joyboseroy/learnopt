#!/usr/bin/env python3
"""Section 4.5: JEE Advanced vs NEET skill distribution comparison."""

import json
import pandas as pd
import numpy as np

SKILLS = ["S1", "S2", "S3", "S4", "S5"]

def kl_div(p, q, eps=1e-6):
    p = np.array(p) / 100 + eps
    q = np.array(q) / 100 + eps
    p, q = p / p.sum(), q / q.sum()
    return float(np.sum(p * np.log(p / q)))

# ---- Load JEE ----
jee_rows = []
errors = 0
for line in open("jee/jeebench_tagged.jsonl"):
    r = json.loads(line)
    tag = r["tag"]
    skill = tag.get("skill", "").strip()
    if skill not in SKILLS:
        errors += 1
        continue
    jee_rows.append({
        "year": r["paper_year"],
        "subject": r["paper_subject"],
        "skill": skill,
    })

jee_df = pd.DataFrame(jee_rows)
print(f"JEE: {len(jee_df)} tagged, {errors} errors")

print("\n" + "="*60)
print("JEE ADVANCED (JEEBench MCQ subset) -- skill distribution")
print("="*60)
jee_pivot = pd.crosstab(jee_df["skill"], "pct", normalize=True).T * 100
jee_pivot = jee_pivot.reindex(columns=SKILLS, fill_value=0).round(1)
print(jee_pivot)

print("\nBy subject:")
jee_subj = pd.crosstab(jee_df["subject"], jee_df["skill"], normalize="index") * 100
jee_subj = jee_subj.reindex(columns=SKILLS, fill_value=0).round(1)
print(jee_subj)

print("\nBy year (n too small for stationarity, shown for reference):")
print(jee_df["year"].value_counts().sort_index())
jee_year = pd.crosstab(jee_df["year"], jee_df["skill"], normalize="index") * 100
jee_year = jee_year.reindex(columns=SKILLS, fill_value=0).round(1)
print(jee_year)

# ---- Load NEET aggregate (from earlier analysis) ----
neet_subj = pd.read_csv("skill_distribution_by_subject.csv", index_col=0)
neet_subj = neet_subj.reindex(columns=SKILLS, fill_value=0)

# NEET aggregate (across all subjects)
neet_year = pd.read_csv("skill_distribution_by_year.csv", index_col=0)
neet_full = pd.DataFrame([json.loads(l) for l in open("tagged_merged.jsonl")])
neet_skills = neet_full["tag"].apply(lambda t: t.get("skill"))
neet_agg = (neet_skills.value_counts(normalize=True) * 100).reindex(SKILLS, fill_value=0).round(1)

print("\n" + "="*60)
print("NEET (all subjects, all years) -- skill distribution")
print("="*60)
print(neet_agg)

print("\n" + "="*60)
print("CROSS-EXAM COMPARISON: JEE Advanced vs NEET")
print("="*60)
jee_agg = jee_pivot.loc["pct"]
comparison = pd.DataFrame({"JEE_Advanced": jee_agg, "NEET": neet_agg})
print(comparison.round(1))

kl_overall = kl_div(jee_agg.values, neet_agg.values)
print(f"\nKL divergence JEE Advanced vs NEET (overall): {kl_overall:.4f}")
print("(Compare to NEET in-regime year-to-year KL: 0.004-0.060,")
print(" and NEET cross-subject KL: 0.15-0.42)")

print("\n" + "="*60)
print("CROSS-EXAM, SAME-SUBJECT COMPARISON")
print("="*60)
for subj_jee, subj_neet in [("Mathematics", None), ("Chemistry", "Chemistry"), ("Physics", "Physics")]:
    if subj_neet is None:
        print(f"\n{subj_jee} (JEE) -- no NEET equivalent (NEET has no Math)")
        print(jee_subj.loc[subj_jee] if subj_jee in jee_subj.index else "n/a")
        continue
    jee_s = jee_subj.loc[subj_jee] if subj_jee in jee_subj.index else None
    neet_s = neet_subj.loc[subj_neet] if subj_neet in neet_subj.index else None
    if jee_s is not None and neet_s is not None:
        kl = kl_div(jee_s.values, neet_s.values)
        print(f"\n{subj_jee}: JEE n={int((jee_df['subject']==subj_jee).sum())}")
        print(pd.DataFrame({"JEE_Advanced": jee_s, "NEET": neet_s}).round(1))
        print(f"KL divergence: {kl:.4f}")

jee_df.to_csv("jee/jee_tagged_parsed.csv", index=False)
print("\nSaved -> jee/jee_tagged_parsed.csv")
