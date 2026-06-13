# Publishing LearnOpt Data to HuggingFace

This guide walks through releasing the tagged NEET and JEE datasets as
HuggingFace dataset repos under your `joyboseroy` namespace.

## 1. Prepare the files

Convert `tagged_merged.jsonl` (NEET) and `jee/jee_tagged_parsed.csv` +
`jee/jeebench_tagged.jsonl` (JEE) to clean CSVs -- see `data/README.md` for
the conversion script. You should end up with:

- `neet_2016-2024_tagged.csv`
- `jee_advanced_2016-2023_tagged.csv`

## 2. Create the dataset repos

```bash
pip install huggingface_hub --break-system-packages
huggingface-cli login   # use your HF_TOKEN

huggingface-cli repo create neet-skill-tags-2016-2024 --type dataset
huggingface-cli repo create jee-advanced-skill-tags-2016-2023 --type dataset
```

## 3. Upload

```bash
cd data
huggingface-cli upload joyboseroy/neet-skill-tags-2016-2024 neet_2016-2024_tagged.csv
huggingface-cli upload joyboseroy/jee-advanced-skill-tags-2016-2023 jee_advanced_2016-2023_tagged.csv
```

## 4. Write dataset cards (README.md on HF)

Each dataset repo gets its own `README.md` (the "dataset card"). Suggested
content for `neet-skill-tags-2016-2024`:

```markdown
---
license: other
license_name: fair-use-derived
task_categories:
  - text-classification
tags:
  - education
  - exam-analysis
  - neet
  - india
---

# NEET Skill-Tagged Questions (2016-2024)

1,496 NEET (National Eligibility cum Entrance Test) questions, 2016-2024,
each tagged with a five-category cognitive skill label (S1-S5: Direct Recall,
Conceptual Application, Multi-concept Integration, Quantitative Reasoning,
Elimination/Negation) using LLM-based annotation (llama-3.1-8b-instant via
Groq), plus topic/chapter/difficulty/NCERT-reference metadata.

Part of the LearnOpt project: [github.com/joyboseroy/learnopt](https://github.com/joyboseroy/learnopt)
Paper: [arXiv link]

## Source

Question text sourced from
[dipikakhullar/neet](https://huggingface.co/datasets/dipikakhullar/neet)
("fair use"). Skill/topic/difficulty annotations are original to this
release (MIT).

## Columns

| Column | Description |
|---|---|
| year | Exam year (2016-2024) |
| subject | Biology / Chemistry / Physics |
| question | Question text |
| skill | S1-S5 (see taxonomy below) |
| skill_evidence | LLM's stated reasoning for the label |
| chapter | Tagged chapter |
| topic | Tagged topic |
| difficulty | LLM-assigned difficulty, 1-5 |
| ncert_reference | Tagged NCERT chapter reference |
| tagger | Model used (all llama-3.1-8b-instant after consistency pass) |

## Skill Taxonomy

[same table as main README]

## Known Limitations

- 2022 is underrepresented (n=32 vs ~170-200 for other years)
- Question text drawn from a community-scraped archive, not official NTA PDFs
- Skill labels are LLM-generated; inter-model kappa=0.51 (see paper Section 4.2)
```

Adapt similarly for the JEE dataset card, crediting JEEBench/Arora et al.

## 5. Link back

Once both are live, update the main `README.md`'s "Dataset" section with the
live URLs, and consider adding the HF dataset badges:

```markdown
[![NEET Dataset](https://img.shields.io/badge/🤗-NEET%20Skill%20Tags-yellow)](https://huggingface.co/datasets/joyboseroy/neet-skill-tags-2016-2024)
[![JEE Dataset](https://img.shields.io/badge/🤗-JEE%20Skill%20Tags-yellow)](https://huggingface.co/datasets/joyboseroy/jee-advanced-skill-tags-2016-2023)
```
