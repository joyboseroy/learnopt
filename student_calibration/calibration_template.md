# LearnOpt Student Calibration Sheet

Fill this out about yourself (~30-60 minutes). Output is used by
`calibrate.py` to generate your personal mastery vector, which
`pipeline/04_optimize.py` uses to build your study plan.

You can copy this file (e.g. `cp calibration_template.md my_calibration.md`),
fill in the tables, and keep it private -- only the generated
`mastery_vector.json` is needed by the optimizer.

---

## Section A: Your self-assessed mastery (required)

For each topic in your exam's syllabus, rate your current mastery from 0
(never studied) to 10 (fully confident). The topic list below is a NEET
Biology example -- for other exams/subjects, replace with the relevant
syllabus topic list (see `data/` for the topic lists used in the paper).

| Topic | Mastery (0-10) |
|---|---|
| Genetics -- Mendelian inheritance | |
| Genetics -- Pedigree analysis | |
| Genetics -- Molecular basis (DNA/RNA) | |
| Cell biology -- Organelles | |
| Cell biology -- Cell division | |
| Human physiology -- Digestion | |
| Human physiology -- Circulation | |
| Human physiology -- Nervous system | |
| Human physiology -- Excretion | |
| Ecology -- Ecosystem | |
| Ecology -- Population | |
| Plant physiology -- Photosynthesis | |
| Plant physiology -- Respiration | |
| Reproduction | |
| Evolution | |
| Biomolecules / Enzymes | |
| Microbes in human welfare | |
| Biotechnology | |

---

## Section B: Topic difficulty & frequency (optional, improves accuracy)

If you've prepared for this exam before, rate each topic on:
- **Effort to master** (1=easy/quick, 5=takes a long time)
- **Frequency feel** (1=rarely appears, 5=appears almost every paper)

These help calibrate the optimizer's cost/value functions with
domain-expert priors, supplementing the historical-frequency data already
in `data/`.

| Topic | Effort (1-5) | Frequency (1-5) |
|---|---|---|
| (same topic list as Section A) | | |

---

## Section C: Available study time (required)

- Total hours available before the exam: ____
- Hours per week you can realistically commit: ____

---

## Section D: Sanity check (optional but valuable)

After running the optimizer, you'll get a study plan. Come back and answer:

> Does this plan match your intuition about what you should prioritize? If
> not, what would you change, and why?

This kind of feedback -- from real students -- is how the taxonomy and
weighting get refined over time. Consider opening a GitHub issue with your
answer (anonymized) to help improve LearnOpt for future students.

---

## Generating your mastery vector

```bash
python3 calibrate.py my_calibration.md > mastery_vector.json
python3 ../pipeline/04_optimize.py --mastery mastery_vector.json --hours 150 --exam neet
```
