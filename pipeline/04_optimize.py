#!/usr/bin/env python3
"""
LearnOpt study plan optimizer (v0.1).

Implements the value/cost formulation from paper Section 3.5:
    V_S = sum_i R_i * W_skill(i) * (1 - m_skill(i))
    C_S = sum_i D_i * (1 - m_i)^alpha

subject to sum(C_S * x_S) <= T, x_S in {0,1}, prerequisite constraints.

STATUS: This is a v0.1 reference implementation. The full prerequisite-graph
subgraph enumeration (Section 3.3) and skill-level mastery tracking via BKT
(Section 2.1) are simplified here to per-topic granularity for tractability.
Contributions extending this to the full graph formulation are welcome --
see paper Section 5.4 "Future Extensions".

Usage:
    python3 04_optimize.py --mastery mastery_vector.json --hours 150 --exam neet
    python3 04_optimize.py --mastery mastery_vector.json --hours 150 --exam neet --no-skill-weights
"""

import json
import argparse
import pandas as pd
from ortools.sat.python import cp_model


# Keyword mapping: calibration_template topic -> substrings to match against
# (chapter + " " + topic), case-insensitive. First match wins. This bridges
# the gap between LLM free-text tagging (956 topics / 285 chapters) and the
# ~18 canonical syllabus topics used in student calibration. See
# data/README.md for context -- this is a heuristic v0.1 mapping, not
# exhaustive; unmatched rows fall into an "Other" bucket.
TOPIC_KEYWORDS = {
    "Genetics -- Mendelian inheritance": ["mendel", "inheritance"],
    "Genetics -- Pedigree analysis": ["pedigree"],
    "Genetics -- Molecular basis (DNA/RNA)": ["molecular biology", "dna", "rna", "transcription", "translation", "genetics and molecular"],
    "Cell biology -- Organelles": ["cell structure", "organelle"],
    "Cell biology -- Cell division": ["cell division", "cell cycle", "mitosis", "meiosis"],
    "Human physiology -- Digestion": ["digest"],
    "Human physiology -- Circulation": ["circulat", "cardiovascular", "blood"],
    "Human physiology -- Nervous system": ["nervous", "neuro"],
    "Human physiology -- Excretion": ["excret", "renal", "kidney"],
    "Ecology -- Ecosystem": ["ecosystem"],
    "Ecology -- Population": ["population", "ecology"],
    "Plant physiology -- Photosynthesis": ["photosynthesis"],
    "Plant physiology -- Respiration": ["respiration", "respiratory"],
    "Reproduction": ["reproduction", "pollination"],
    "Evolution": ["evolution", "genetics and evolution"],
    "Biomolecules / Enzymes": ["biomolecule", "enzyme"],
    "Microbes in human welfare": ["microbe", "microorganism"],
    "Biotechnology": ["biotechnology", "recombinant", "restriction enzyme"],
}


def map_to_calibration_topic(chapter, topic):
    """Map a free-text (chapter, topic) pair to a calibration_template topic
    via keyword substring matching. Returns None if no keyword matches."""
    text = f"{chapter} {topic}".lower()
    for cal_topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return cal_topic
    return None


def load_topic_data(exam):
    """
    Load per-topic relevance (R_i), dominant skill, difficulty (D_i), and
    skill weights (W_s) for the given exam, derived from the tagged corpus
    in data/. Rows are grouped by `calibration_topic` (mapped via
    TOPIC_KEYWORDS) where possible, falling back to the original `topic`
    for unmapped rows (grouped under their own names, will not match any
    calibration mastery entry and default to mastery=0.3).

    Returns a DataFrame with columns: topic, R, skill, D, W
    """
    tagged_path = f"data/{exam}_2016-2024_tagged.csv" if exam == "neet" \
        else f"data/jee_advanced_2016-2023_tagged.csv"
    df = pd.read_csv(tagged_path)

    df["calibration_topic"] = df.apply(
        lambda row: map_to_calibration_topic(row.get("chapter", ""), row.get("topic", "")),
        axis=1
    )
    n_mapped = df["calibration_topic"].notna().sum()
    print(f"[load_topic_data] {n_mapped}/{len(df)} rows mapped to a "
          f"calibration topic via keyword matching ({n_mapped/len(df)*100:.1f}%)")

    # Use calibration_topic where available, else fall back to original topic
    df["group_topic"] = df["calibration_topic"].fillna(df["topic"])

    # Per-topic relevance: normalized question frequency
    topic_counts = df.groupby("group_topic").size()
    R = (topic_counts / topic_counts.sum()).to_dict()

    # Dominant skill per topic (mode)
    dominant_skill = df.groupby("group_topic")["skill"].agg(
        lambda x: x.value_counts().idxmax()
    ).to_dict()

    # Per-topic difficulty: mean LLM-assigned difficulty (1-5), normalized to 0-1
    D = (df.groupby("group_topic")["difficulty"].mean() / 5.0).to_dict()

    # Skill weights: empirical frequency of each skill category overall
    skill_counts = df["skill"].value_counts(normalize=True)
    W = skill_counts.to_dict()

    rows = []
    for topic in topic_counts.index:
        rows.append({
            "topic": topic,
            "R": R.get(topic, 0),
            "skill": dominant_skill.get(topic, "S2"),
            "D": D.get(topic, 0.5),
            "W": W.get(dominant_skill.get(topic, "S2"), 0.2),
        })
    return pd.DataFrame(rows)


def estimate_hours_per_topic(difficulty, mastery, alpha=1.5, base_hours=10):
    """C_i: estimated study hours for topic given difficulty and current mastery."""
    return base_hours * difficulty * ((1 - mastery) ** alpha)


def optimize_plan(topics_df, mastery, total_hours, use_skill_weights=True, alpha=1.5):
    """
    Solve the knapsack-style selection problem: which topics to study,
    maximizing value subject to a time budget.
    """
    model = cp_model.CpModel()

    n = len(topics_df)
    x = [model.NewBoolVar(f"x_{i}") for i in range(n)]

    values = []
    costs = []
    for _, row in topics_df.iterrows():
        m = mastery.get(row["topic"], 0.3)  # default: assume low-moderate mastery
        if m is None:
            m = 0.3

        if use_skill_weights:
            value = row["R"] * row["W"] * (1 - m)
        else:
            value = row["R"] * (1 - m)

        cost = estimate_hours_per_topic(row["D"], m, alpha=alpha)

        # Scale to integers for CP-SAT (x1000)
        values.append(int(value * 100000))
        costs.append(int(cost * 100))

    total_hours_scaled = int(total_hours * 100)
    model.Add(sum(c * xi for c, xi in zip(costs, x)) <= total_hours_scaled)
    model.Maximize(sum(v * xi for v, xi in zip(values, x)))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("Solver failed to find a solution")

    results = []
    for i, row in topics_df.iterrows():
        selected = solver.Value(x[i]) == 1
        m = mastery.get(row["topic"], 0.3) or 0.3
        results.append({
            "topic": row["topic"],
            "skill": row["skill"],
            "selected": selected,
            "mastery": m,
            "estimated_hours": estimate_hours_per_topic(row["D"], m, alpha=alpha) if selected else 0,
            "value": (row["R"] * row["W"] * (1 - m)) if use_skill_weights else (row["R"] * (1 - m)),
        })

    results_df = pd.DataFrame(results).sort_values("value", ascending=False)
    return results_df, solver.ObjectiveValue() / 100000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mastery", required=True, help="mastery_vector.json from calibrate.py")
    parser.add_argument("--hours", type=float, required=True, help="total study hours available")
    parser.add_argument("--exam", choices=["neet", "jee"], default="neet")
    parser.add_argument("--no-skill-weights", action="store_true",
                         help="Ablation: disable skill-weighted objective (W_s=1)")
    parser.add_argument("--alpha", type=float, default=1.5,
                         help="learning-cost decay exponent (Section 3.5)")
    args = parser.parse_args()

    mastery_data = json.load(open(args.mastery))
    mastery = mastery_data.get("mastery", {})

    topics_df = load_topic_data(args.exam)

    plan_df, total_value = optimize_plan(
        topics_df, mastery, args.hours,
        use_skill_weights=not args.no_skill_weights,
        alpha=args.alpha,
    )

    selected = plan_df[plan_df["selected"]]
    skipped = plan_df[~plan_df["selected"]]

    print(f"\n{'='*60}")
    print(f"STUDY PLAN ({args.exam.upper()}, {args.hours} hours, "
          f"{'skill-weighted' if not args.no_skill_weights else 'topic-frequency only'})")
    print(f"{'='*60}\n")

    print(f"STUDY ({len(selected)} topics, "
          f"{selected['estimated_hours'].sum():.1f} hours):")
    for _, row in selected.iterrows():
        print(f"  [{row['skill']}] {row['topic']:40s} "
              f"mastery={row['mastery']:.1f}  ~{row['estimated_hours']:.1f}h")

    print(f"\nSKIP ({len(skipped)} topics, low ROI given your profile):")
    for _, row in skipped.head(10).iterrows():
        print(f"  [{row['skill']}] {row['topic']:40s} mastery={row['mastery']:.1f}")

    print(f"\nTotal expected value (predicted score-relevance gain): {total_value:.4f}")


if __name__ == "__main__":
    main()
