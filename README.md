# LearnOpt

**Recovering the latent cognitive structure of standardized examinations, and using it to generate personalized study plans.**

LearnOpt is an open-source pipeline that:

1. Takes historical exam questions (currently NEET 2016-2024 and JEE Advanced 2016-2023)
2. Tags each question with a **skill category** (S1-S5: Recall, Application, Multi-concept Integration, Quantitative Reasoning, Elimination/Negation) using an LLM
3. Measures the **latent skill distribution** of the exam over time -- and detects when it *changes* (e.g. due to syllabus rationalization)
4. Builds a **knowledge graph** of topics, prerequisites, and skills
5. Generates a **personalized, time-bounded study plan** for a student, given their self-assessed mastery, using constrained optimization (OR-Tools)

The accompanying paper (`paper/`) found that NEET's latent skill distribution was stable from 2016-2021, underwent a statistically significant shift (KL=0.040, permutation p=0.0005) coinciding with NCERT's 2023 syllabus rationalization, and that the same pipeline applied to JEE Advanced shows a markedly different cognitive profile (KL=0.505 vs NEET) -- suggesting exam *tier* shapes cognitive structure more than subject, which shapes it more than time within a stable regime.

## Why this matters

Most exam prep tools tell you "study high-weightage chapters." LearnOpt tells you *what kind of thinking* the exam tests, whether that has recently changed, and -- given your own strengths and weaknesses -- what to prioritize next.

Unlike commercial systems (e.g. Embibe's PAJ, which relies on a 75,000-node manually-curated knowledge graph and proprietary behavioral data from millions of students), LearnOpt is built entirely from **publicly available exam papers** using LLM automation, and is designed so **any student can run their own calibration** and get a personalized plan -- no proprietary data required.

## Repo structure

```
learnopt/
├── paper/                      # arXiv paper source (markdown)
├── pipeline/
│   ├── 01_tag_questions.py    # LLM tagging (Groq + Ollama)
│   ├── 02_analyze_skills.py   # skill distribution, KL divergence, permutation tests
│   ├── 03_build_graph.py      # FalkorDB knowledge graph ingestion
│   └── 04_optimize.py         # OR-Tools study plan generator
├── prompts/
│   └── skill_taxonomy_prompt.md
├── data/
│   ├── neet_2016-2024_tagged.csv
│   └── jee_advanced_2016-2023_tagged.csv
├── student_calibration/
│   ├── calibration_template.md  # fill this out about yourself
│   └── calibrate.py              # turns your answers into a mastery vector
└── notebooks/
    └── reproduce_section4.ipynb
```

## Quickstart: get your own study plan

1. Copy `student_calibration/calibration_template.md` and fill it out (topic
   difficulty/frequency ratings + your self-assessed mastery per topic --
   takes about 30-60 minutes).
2. Run:
   ```bash
   python3 student_calibration/calibrate.py my_calibration.md > mastery_vector.json
   python3 pipeline/04_optimize.py --mastery mastery_vector.json --hours 150 --exam neet
   ```
3. Get a ranked study plan: which topics to prioritize, which to skip, and why.

## Quickstart: reproduce the paper's analysis

```bash
pip install -r requirements.txt
python3 pipeline/01_tag_questions.py --input data/raw/neet_questions.csv --output tagged.jsonl
python3 pipeline/02_analyze_skills.py --input tagged.jsonl
```

Or open `notebooks/reproduce_section4.ipynb` for the full Section 4 analysis
(skill distributions, KL divergence tables, permutation tests, JEE comparison).

## Dataset

Tagged question data is also available on HuggingFace:
- `joyboseroy/neet-skill-tags-2016-2024`
- `joyboseroy/jee-advanced-skill-tags-2016-2023`

The underlying NEET question text is sourced from
[`dipikakhullar/neet`](https://huggingface.co/datasets/dipikakhullar/neet)
(fair use); JEE Advanced questions are sourced from
[JEEBench](https://github.com/dair-iitd/jeebench) (Arora et al., EMNLP 2023).

## Skill Taxonomy

| Code | Skill | Description |
|---|---|---|
| S1 | Direct Recall | Answer is a single fact from one textbook sentence |
| S2 | Conceptual Application | A known principle applied to a new context |
| S3 | Multi-concept Integration | Requires combining two or more topics/chapters |
| S4 | Quantitative Reasoning | Requires calculation or formula application |
| S5 | Elimination/Negation | "Which is NOT correct" / "all EXCEPT" / Assertion-Reason |

See `prompts/skill_taxonomy_prompt.md` for the full tagging prompt and
`paper/` Section 3.4 for the taxonomy's justification.

## Citation

If you use this code or data, please cite:

```bibtex

```

## Status

This is an active research project. The skill-distribution analysis
(Section 4.1-4.4, 4.6 of the paper) is complete and reproducible. The
optimization/calibration tooling (Section 4.5) is under active development --
contributions welcome.

## License

Code: MIT. Data: see individual dataset cards for upstream licensing
(NEET questions are "fair use" per source; please verify before commercial
use).
