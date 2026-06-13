#!/bin/bash
cd ~/learnopt/data

python3 << 'EOF'
import pandas as pd
import re

df = pd.read_csv("dipikakhullar_en.csv")
print("Total rows:", len(df))

# Extract year and subject from file_name like NEET_2016_Physics.pdf
def extract_year(fname):
    m = re.search(r'(20\d{2})', str(fname))
    return int(m.group(1)) if m else None

def extract_subject(fname):
    for s in ['Physics', 'Chemistry', 'Biology', 'Botany', 'Zoology']:
        if s in str(fname):
            return s
    return None

df['paper_year'] = df['file_name'].apply(extract_year)
df['paper_subject'] = df['file_name'].apply(extract_subject)

print("\nYear distribution:")
print(df['paper_year'].value_counts().sort_index())

print("\nYear x Subject:")
print(pd.crosstab(df['paper_year'], df['paper_subject']))

print("\ncategory_en distribution:")
print(df['category_en'].value_counts())

print("\nUnique file_names:")
print(df['file_name'].unique())

print("\nSample questions per year (first question of earliest and latest year):")
years = sorted(df['paper_year'].dropna().unique())
if years:
    print(f"\nEarliest year {years[0]}, sample:")
    print(df[df['paper_year']==years[0]]['question'].iloc[0][:300])
    print(f"\nLatest year {years[-1]}, sample:")
    print(df[df['paper_year']==years[-1]]['question'].iloc[0][:300])

df.to_csv("dipikakhullar_en_tagged.csv", index=False)
print("\nSaved -> dipikakhullar_en_tagged.csv")
EOF
