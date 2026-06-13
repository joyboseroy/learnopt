#!/usr/bin/env python3
"""Merge tagged_full.jsonl + any number of fill files -> tagged_merged.jsonl
Usage: python3 merge_tagged.py tagged_fill.jsonl tagged_fill2.jsonl ..."""

import json
import sys

records = {}

for line in open("tagged_full.jsonl"):
    r = json.loads(line)
    if "error" not in r["tag"]:
        r["tagger"] = "groq-llama-3.1-8b-instant"
        records[r["index"]] = r

fill_files = sys.argv[1:] if len(sys.argv) > 1 else ["tagged_fill.jsonl"]

for fname in fill_files:
    tagger = "ollama-qwen2.5:7b" if "ollama" in fname or fname == "tagged_fill.jsonl" else "groq-llama-3.1-8b-instant"
    fill_ok, fill_err = 0, 0
    for line in open(fname):
        r = json.loads(line)
        if "error" not in r["tag"]:
            r["tagger"] = tagger
            records[r["index"]] = r
            fill_ok += 1
        else:
            fill_err += 1
            print(f"[{fname}] Still failed:", r["index"], r["tag"])
    print(f"{fname}: filled OK = {fill_ok}, still failed = {fill_err}")

print(f"Total records: {len(records)} / 1496")

with open("tagged_merged.jsonl", "w") as f:
    for i in sorted(records.keys()):
        f.write(json.dumps(records[i]) + "\n")

print("Saved -> tagged_merged.jsonl")
