#!/usr/bin/env python3
import json
import re
import pandas as pd
from collections import Counter

data = json.load(open("../jeebench_data/data/responses/GPT4_CoT_responses/responses.json"))

print("Total items:", len(data))
print("\nType distribution:")
print(Counter([d['type'] for d in data]))

print("\nSubject distribution:")
print(Counter([d['subject'] for d in data]))

# Extract year from description e.g. "JEE Adv 2016 Paper 1"
def extract_year(desc):
    m = re.search(r'(20\d{2})', desc)
    return int(m.group(1)) if m else None

for d in data:
    d['year'] = extract_year(d['description'])

print("\nType x Year (MCQ only matters most for us):")
df_all = pd.DataFrame(data)
print(pd.crosstab(df_all['year'], df_all['type']))

# Filter to single-correct MCQ only -- maps to S1-S5 like NEET
df_mcq = df_all[df_all['type'] == 'MCQ'].copy()
print(f"\nMCQ-only subset: {len(df_mcq)} questions")
print("\nMCQ by year:")
print(df_mcq['year'].value_counts().sort_index())
print("\nMCQ by subject:")
print(df_mcq['subject'].value_counts())
print("\nMCQ by year x subject:")
print(pd.crosstab(df_mcq['year'], df_mcq['subject']))

subject_map = {'phy': 'Physics', 'chem': 'Chemistry', 'math': 'Mathematics'}
df_mcq['paper_subject'] = df_mcq['subject'].map(subject_map)
df_mcq['paper_year'] = df_mcq['year']

# JEEBench MCQs don't include options as separate field -- options are
# embedded in 'question' text for single-correct? Check gold field too.
print("\nSample question (first MCQ):")
print(df_mcq.iloc[0]['question'][:1000])
print("\nGold answer field:", df_mcq.iloc[0]['gold'])

df_mcq[['paper_year', 'paper_subject', 'question', 'gold', 'description', 'index']].to_csv(
    "../jeebench_mcq.csv", index=False)
print("\nSaved -> ../jeebench_mcq.csv")
