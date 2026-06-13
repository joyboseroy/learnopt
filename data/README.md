# Data Directory

This directory should contain the tagged exam datasets. These files are NOT
included in this zip (they live on your WSL machine from the tagging
pipeline) -- copy them here before pushing to GitHub, or release them via
HuggingFace and reference them from the main README instead.

## Files expected here

- `neet_2016-2024_tagged.csv` -- derived from `tagged_merged.jsonl` on your
  WSL machine (`~/learnopt/data/`). Convert with:
  ```bash
  python3 -c "
  import json, pandas as pd
  records = [json.loads(l) for l in open('tagged_merged.jsonl')]
  rows = []
  for r in records:
      t = r['tag']
      rows.append({
          'year': r['paper_year'], 'subject': r['paper_subject'],
          'question': r['question'], 'skill': t['skill'],
          'skill_evidence': t.get('skill_evidence',''),
          'chapter': t.get('chapter',''), 'topic': t.get('topic',''),
          'difficulty': t.get('difficulty',''),
          'ncert_reference': t.get('ncert_reference',''),
          'tagger': r['tagger'],
      })
  pd.DataFrame(rows).to_csv('neet_2016-2024_tagged.csv', index=False)
  "
  ```

- `jee_advanced_2016-2023_tagged.csv` -- derived similarly from
  `jee/jee_tagged_parsed.csv` + `jee/jeebench_tagged.jsonl` on WSL.

## Source data licensing

- NEET question text: sourced from
  [`dipikakhullar/neet`](https://huggingface.co/datasets/dipikakhullar/neet)
  (license: "fair use" per dataset metadata). Verify current terms before
  any commercial use.
- JEE Advanced question text: sourced from
  [JEEBench](https://github.com/dair-iitd/jeebench) (Arora et al., EMNLP 2023).
  See their repository for license.

The `skill`, `topic`, `chapter`, `difficulty`, etc. columns are LearnOpt's
own derived annotations (MIT licensed, see root LICENSE), independent of the
underlying question text licensing.
