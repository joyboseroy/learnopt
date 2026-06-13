#!/usr/bin/env python3
"""
Parse a filled-out calibration_template.md into mastery_vector.json
for use by pipeline/04_optimize.py.

Usage:
    python3 calibrate.py my_calibration.md > mastery_vector.json
"""

import re
import sys
import json


def parse_markdown_table(text, section_header):
    """Extract rows from the first markdown table following a header."""
    pattern = rf"## {re.escape(section_header)}.*?\n(\|.*\n)+"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []

    table_text = match.group(0)
    rows = []
    for line in table_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        # skip header and separator rows
        if cells[0].lower() in ("topic",) or set(cells[0]) <= {"-", " "}:
            continue
        rows.append(cells)
    return rows


def parse_calibration(path):
    text = open(path).read()

    mastery = {}
    for row in parse_markdown_table(text, "Section A: Your self-assessed mastery (required)"):
        if len(row) < 2:
            continue
        topic, val = row[0], row[1]
        if not topic or topic.startswith("("):
            continue
        try:
            mastery[topic] = float(val) / 10.0  # normalize 0-10 -> 0-1
        except ValueError:
            mastery[topic] = None  # left blank

    priors = {}
    for row in parse_markdown_table(text, "Section B: Topic difficulty & frequency (optional, improves accuracy)"):
        if len(row) < 3:
            continue
        topic, effort, freq = row[0], row[1], row[2]
        if not topic or topic.startswith("("):
            continue
        entry = {}
        try:
            entry["effort"] = float(effort)
        except ValueError:
            pass
        try:
            entry["frequency_prior"] = float(freq)
        except ValueError:
            pass
        if entry:
            priors[topic] = entry

    # Section C: hours
    hours_match = re.search(r"Total hours available before the exam:\s*(\d+)", text)
    weekly_match = re.search(r"Hours per week.*?:\s*(\d+)", text)

    output = {
        "mastery": mastery,
        "priors": priors,
        "total_hours": int(hours_match.group(1)) if hours_match else None,
        "weekly_hours": int(weekly_match.group(1)) if weekly_match else None,
    }

    # Warn about unfilled mastery values
    unfilled = [t for t, v in mastery.items() if v is None]
    if unfilled:
        sys.stderr.write(
            f"WARNING: {len(unfilled)} topics have no mastery rating "
            f"(treated as null, optimizer should prompt or default):\n"
        )
        for t in unfilled:
            sys.stderr.write(f"  - {t}\n")

    return output


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 calibrate.py my_calibration.md > mastery_vector.json\n")
        sys.exit(1)

    result = parse_calibration(sys.argv[1])
    print(json.dumps(result, indent=2))
