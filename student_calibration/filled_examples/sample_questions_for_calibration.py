#!/usr/bin/env python3
"""Pull real sample questions for Om's task sheet -- a mix from pre-2022
(2018) and post-2023 regime, Biology-focused, across skill categories.
Pulls FULL question text + options from the original CSV (tagged_merged.jsonl
truncates question text to 200 chars)."""

import json
import random
import pandas as pd

random.seed(42)

records = [json.loads(l) for l in open("tagged_merged.jsonl")]
df = pd.read_csv("dipikakhullar_en_tagged.csv")

bio_2018 = [r for r in records if r["paper_subject"] == "Biology" and r["paper_year"] == 2018]
bio_2023 = [r for r in records if r["paper_subject"] == "Biology" and r["paper_year"] == 2023]

sample_2018 = random.sample(bio_2018, min(5, len(bio_2018)))
sample_2023 = random.sample(bio_2023, min(5, len(bio_2023)))

print("="*60)
print("SAMPLE QUESTIONS FOR OM'S TASK 3 (paste into task sheet)")
print("="*60)
for i, r in enumerate(sample_2018 + sample_2023, 1):
    full = df.iloc[r["index"]]
    print(f"\n--- Question {i} (NEET {r['paper_year']}, Biology) ---")
    print(full["question"])
    print(f"Options: {full['options']}")
    print(f"[LLM tagged as: {r['tag']['skill']} -- not shown to Om]")
