#!/usr/bin/env python3
"""
Fills missing indices in tagged_full.jsonl using local Ollama (qwen2.5:7b).
Writes results to tagged_fill.jsonl (separate file), then run merge step.
"""

import json
import time
import argparse
import pandas as pd
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:7b"

SYSTEM_PROMPT = """You are an expert NEET exam analyst. Classify each question
using EXACTLY one of these five skill categories:

S1 - Direct Recall: Answer is a single fact retrievable from one NCERT sentence. No reasoning required.
S2 - Conceptual Application: A known principle applied to a new context. One inferential step beyond retrieval.
S3 - Multi-concept Integration: Correct answer requires combining knowledge from two or more distinct chapters/topics simultaneously.
S4 - Quantitative Reasoning: Requires numerical calculation, unit analysis, or formula application.
S5 - Elimination and Negation: Question structured as "which is NOT correct" or "all EXCEPT" -- requires exhaustive verification of multiple claims.

Respond with ONLY a JSON object, no markdown, no preamble, in this exact format:
{"skill": "S1|S2|S3|S4|S5", "skill_evidence": "one short sentence specific to THIS question", "chapter": "...", "topic": "...", "difficulty": 1-5, "ncert_reference": "Class 11/12 Subject Chapter N"}
"""

def build_user_prompt(row):
    return f"Subject: {row['paper_subject']}\nQuestion: {row['question']}\nOptions: {row['options']}"


def tag_with_ollama(row, retries=2):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(row)},
        ],
        "stream": False,
        "options": {"temperature": 0},
    }
    for attempt in range(retries):
        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
            resp.raise_for_status()
            text = resp.json()["message"]["content"].strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            if attempt == retries - 1:
                return {"error": f"json_decode: {e}", "raw": text}
        except Exception as e:
            if attempt == retries - 1:
                return {"error": str(e)}
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="dipikakhullar_en_tagged.csv")
    parser.add_argument("--indices", required=True, help="comma-separated or file with one index per line")
    parser.add_argument("--output", default="tagged_fill.jsonl")
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    if "," in args.indices:
        indices = [int(x) for x in args.indices.split(",")]
    else:
        indices = [int(x.strip()) for x in open(args.indices) if x.strip()]

    print(f"Filling {len(indices)} missing indices via Ollama ({MODEL})...")

    with open(args.output, "w") as f:
        for n, i in enumerate(indices):
            row = df.iloc[i]
            result = tag_with_ollama(row)
            record = {
                "index": int(i),
                "paper_year": int(row.get("paper_year")),
                "paper_subject": row.get("paper_subject"),
                "question": row["question"][:200],
                "tag": result,
            }
            f.write(json.dumps(record) + "\n")
            f.flush()
            if n % 10 == 0:
                print(f"Filled {n}/{len(indices)}")

    print(f"Done. Output -> {args.output}")
    print("Next: run merge_tagged.py to combine with tagged_full.jsonl")


if __name__ == "__main__":
    main()
