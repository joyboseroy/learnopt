# LearnOpt Skill Taxonomy & Tagging Prompt

## The Five Categories

**S1 -- Direct Recall**
Answer is a single fact retrievable from one textbook sentence. No reasoning required.
*Example: "The process of transfer of genetic information from DNA to RNA is called ___."*

**S2 -- Conceptual Application**
A known principle applied to a new or unfamiliar context. One inferential step beyond retrieval.
*Example: A standard genetic cross with non-standard allele combinations.*

**S3 -- Multi-concept Integration**
Correct answer requires combining knowledge from two or more distinct topics/chapters simultaneously.
*Example: A question requiring both inheritance rules and enzyme biochemistry.*

**S4 -- Quantitative Reasoning**
Requires numerical calculation, unit analysis, or formula application in a domain context.
*Example: Hardy-Weinberg allele frequency calculation.*

**S5 -- Elimination and Negation**
Structured as "which is NOT correct," "all EXCEPT," an Assertion-Reason pair, or
multi-statement "Statement I / Statement II" verification. Requires exhaustive
checking of multiple claims rather than retrieval of one answer.
*Example: "Given below are two statements... choose the most appropriate answer."*

## Why These Five?

Six-level Bloom's Taxonomy shows poor inter-rater reliability on science MCQs
(reported ICC as low as 0.54). Collapsed three-level rubrics
(Recall/Comprehension, Application, Analysis) raise ICC to ~0.94. S1-S4 here
map approximately onto Remember/Understand/Apply/Analyze. S5 is added as a
sixth, *format-driven* category -- it can be identified from the surface
structure of the question (does it contain "NOT", "EXCEPT", "Assertion",
"Statement I/II"?) independent of content, and our inter-model reliability
check found S5 to be the most consistently identified category (80% agreement
between two different LLMs), while S2/S3/S4 form a fuzzier cluster.

## The Tagging Prompt

```
You are an expert exam analyst. Classify each question using EXACTLY one of
these five skill categories:

S1 - Direct Recall: Answer is a single fact retrievable from one textbook
sentence. No reasoning required.
S2 - Conceptual Application: A known principle applied to a new context. One
inferential step beyond retrieval.
S3 - Multi-concept Integration: Correct answer requires combining knowledge
from two or more distinct topics/chapters simultaneously.
S4 - Quantitative Reasoning: Requires numerical calculation, unit analysis, or
formula application.
S5 - Elimination and Negation: Question structured as "which is NOT correct"
or "all EXCEPT" or Assertion-Reason / Statement I & II -- requires exhaustive
verification of multiple claims.

Respond with ONLY a JSON object, no markdown, no preamble, in this exact
format:
{"skill": "S1|S2|S3|S4|S5", "skill_evidence": "one short sentence specific to
THIS question", "chapter": "...", "topic": "...", "difficulty": 1-5,
"ncert_reference": "Class 11/12 Subject Chapter N"}
```

The `skill_evidence` field implements a chain-of-evidence design: the model
must cite question-specific reasoning, not restate the category definition.
This provides a human-reviewable audit trail -- in our tagging run, 3.5% of
records produced generic (definition-restating) evidence strings, flagging
them as lower-confidence.

## Adapting to a New Exam

To tag a new exam (JEE Main, GATE, UPSC, etc.), this prompt requires no
changes -- the categories are deliberately exam-agnostic, defined by
cognitive operation and question format rather than subject content. Only the
`chapter`/`topic`/`ncert_reference` fields need adaptation to the relevant
syllabus.
