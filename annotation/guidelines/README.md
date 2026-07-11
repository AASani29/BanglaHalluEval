# BanHalluEval: Human Annotation Guidelines

This folder contains the annotation guidelines given to human annotators for validating the
**BanHalluEval** benchmark. There is one guideline document per annotation task. Read the
guideline for the task assigned to you **before** you begin, and keep it open for reference while
you work.

## The six annotation tasks

| # | File | What you label | Label column(s) | Scale |
|---|------|----------------|-----------------|-------|
| 1 | [01_qa_hallucination.md](01_qa_hallucination.md) | Whether a Bengali QA answer is hallucinated | `is_hallucinated` | Yes / No |
| 2 | [02_summarization_hallucination.md](02_summarization_hallucination.md) | Whether a Bengali summary is hallucinated | `is_hallucinated` | Yes / No |
| 3 | [03_reasoning_hallucination.md](03_reasoning_hallucination.md) | Whether a Bengali math reasoning chain is hallucinated | `is_hallucinated` | Yes / No |
| 4 | [04_codemix_qa_hallucination.md](04_codemix_qa_hallucination.md) | Whether a code-mixed (Banglish) QA answer is hallucinated | `is_hallucinated` | Yes / No |
| 5 | [05_codemix_conversion_quality.md](05_codemix_conversion_quality.md) | Whether a Bengali to code-mixed conversion is faithful and natural | `meaning_preserved`, `naturalness_1to5` | Yes / No, and 1 to 5 |
| 6 | [06_qa_model_hallucination.md](06_qa_model_hallucination.md) | Whether a live model's Bengali QA answer is hallucinated | `is_hallucinated` | Yes / No |

## Rules that apply to every task

1. **Label every row.** Never leave a row blank. Do not skip a row because it looks hard. If you are
   unsure, make your best judgment and then **flag** it (see below).
2. **Work independently.** Do not discuss individual items with the other annotators while
   labelling. Agreement between independent annotators is what makes the benchmark trustworthy.
3. **This is a blind task.** You are **not** told whether an item is supposed to be correct or
   hallucinated. Judge only what is in front of you.
4. **Judge against the source, not against your outside knowledge.** For every task the decision is
   made *relative to the provided context, document, or problem*, as spelled out in each guideline.
5. **Use only the allowed labels.** For Yes/No columns write exactly `Yes` or `No`. For the 1 to 5
   scale write a single whole number 1, 2, 3, 4, or 5.
6. **Flag, don't guess silently.** If a row is genuinely ambiguous, put your best label **and** write
   a short note in the `notes` or comment column (or highlight the cell) so a supervisor can review it.
7. **Ask when the guideline does not cover a case.** Contact the supervisor rather than inventing a
   new rule on the spot, so that all annotators handle the same situation the same way.

Consistent application of these guidelines is what makes the BanHalluEval agreement scores reliable.
Thank you for your careful work.
