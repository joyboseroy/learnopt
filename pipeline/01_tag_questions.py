#!/usr/bin/env python3
"""
LearnOpt tagging pipeline.
Tags each NEET question with: skill (S1-S5), skill_evidence, chapter, topic,
difficulty (1-5), ncert_reference.

Usage:
  python3 tag_questions.py --input dipikakhullar_en_tagged.csv \
                            --output tagged_neet.jsonl \
                            --limit 50      # start small to test/cost-check
"""

import os
import json
import time
import argparse
import pandas as pd
from groq import Groq

GROQ_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are an expert NEET exam analyst. Classify each question
using EXACTLY one of these five skill categories:

S1 - Direct Recall: Answer is a single fact retrievable from one NCERT sentence. No reasoning required.
S2 - Conceptual Application: A known principle applied to a new context. One inferential step beyond retrieval.
S3 - Multi-concept Integration: Correct answer requires combining knowledge from two or more distinct chapters/topics simultaneously.
S4 - Quantitative Reasoning: Requires numerical calculation, unit analysis, or formula application.
S5 - Elimination and Negation: Question structured as "which is NOT correct" or "all EXCEPT" -- requires exhaustive verification of multiple claims.

Respond with ONLY a JSON object, no markdown, no preamble, in this exact format:
{"skill": "S1|S2|S3|S4|S5", "skill_evidence": "one short sentence", "chapter": "...", "topic": "...", "difficulty": 1-5, "ncert_reference": "Class 11/12 Subject Chapter N"}
"""

def build_user_prompt(row):
    opts = row['options']
    return f"Subject: {row['paper_subject']}\nQuestion: {row['question']}\nOptions: {opts}"


def tag_with_groq(client, row, retries=3):
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(row)},
                ],
                temperature=0,
                max_tokens=300,
            )
            text = resp.choices[0].message.content.strip()
            # strip markdown fences if present
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            if attempt == retries - 1:
                return {"error": f"json_decode: {e}", "raw": text}
            time.sleep(1)
        except Exception as e:
            if attempt == retries - 1:
                return {"error": str(e)}
            time.sleep(2 ** attempt)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--indices-file", default=None,
                         help="file with one row-index per line; if set, --start/--limit ignored")
    args = parser.parse_args()

    df_full = pd.read_csv(args.input)
    if args.indices_file:
        indices = [int(x.strip()) for x in open(args.indices_file) if x.strip()]
        df = df_full.iloc[indices]
    elif args.limit:
        df = df_full.iloc[args.start:args.start + args.limit]
    else:
        df = df_full.iloc[args.start:]

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY not set in environment")
    client = Groq(api_key=api_key)

    mode = "a" if (args.start > 0 or args.indices_file) else "w"
    with open(args.output, mode) as f:
        for i, row in df.iterrows():
            result = tag_with_groq(client, row)
            record = {
                "index": int(i),
                "paper_year": row.get("paper_year"),
                "paper_subject": row.get("paper_subject"),
                "question": row["question"][:200],  # truncate for storage
                "tag": result,
            }
            f.write(json.dumps(record) + "\n")
            f.flush()
            if i % 20 == 0:
                print(f"Tagged {i}/{len(df)+args.start}")
            time.sleep(0.3)  # gentle rate limiting

    print(f"Done. Output -> {args.output}")


if __name__ == "__main__":
    main()
