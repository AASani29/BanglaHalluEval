# Annotation Guidelines: QA-Model (Live Model Output) Hallucination

## 1. Task Overview

This task is like the QA task, but the answers here are **real outputs from live language models**
answering Bengali questions zero-shot (not synthetically constructed). Because the answers come
straight from models, they are often **longer, more verbose, or partially off-topic**, and they may
mix correct and incorrect content in the same response.

You are given a **question**, a **reference (ground-truth) answer**, and the **model's answer**. Your
job is to decide whether the model's answer is **hallucinated**, meaning whether it contains
information that is factually wrong or unsupported.

You will assign exactly one label per row:

- **`is_hallucinated` = Yes**: the model answer is hallucinated.
- **`is_hallucinated` = No**: the model answer is correct and faithful.

## 2. What You Will See

| Column | Meaning |
|--------|---------|
| `question` | The Bengali question. |
| `right_answer` (reference answer) | The correct answer, for your comparison. |
| `model_answer` (model output) | The live model's answer you must judge. |
| `is_hallucinated` | **You fill this in:** `Yes` or `No`. |

## 3. Definition

A model answer is **hallucinated** when it is **factually incorrect** or states information that is
**not supported**, judged against the reference answer and the question. Because these are free-form
model outputs, pay attention to the following behaviours, which are all hallucinations:

- **Wrong fact.** The model gives an answer that contradicts the reference answer.
- **Fabricated detail.** The model adds specific names, dates, numbers, or explanations that are
  invented and not supported.
- **Confident non-answer.** The model produces a fluent, confident-sounding response that does not
  actually contain the correct fact, or answers a different question.
- **Mixed answer.** The model gives the correct answer **plus** extra fabricated claims.

## 4. Labeling Rules

**Mark `is_hallucinated` = Yes if the model answer:**

- Contradicts the reference answer.
- Contains a fabricated fact, name, number, date, or explanation not supported by the question or
  reference.
- Talks around the question fluently without ever giving the correct information.
- Is correct in one part but adds **any** fabricated or wrong claim elsewhere.

**Mark `is_hallucinated` = No if the model answer:**

- Gives the correct answer (matching the reference in meaning), even if it is phrased differently or
  is more verbose.
- Adds only **true, relevant, and well-known** supporting detail that does not contradict anything.
- Correctly states that it does not know or that the information is unavailable, **when that is
  actually the case**.

## 5. How to Judge Verbose Model Answers

Live-model answers are often long. Use this procedure:

1. Find the part of the answer that actually addresses the question and compare it to the
   **reference answer**.
2. Then scan the **rest** of the response for any fabricated or contradicting claim.
3. If the core answer is correct **and** nothing else is fabricated, mark `No`. If the core answer is
   wrong, **or** any added claim is fabricated or contradicting, mark `Yes`.

**Length and confidence are not evidence of correctness.** A long, well-written answer can still be
hallucinated; a short, plain one can be perfectly correct.

## 6. Examples

> **Question:** পদ্মা সেতু কোন নদীর উপর নির্মিত?
> **Reference answer:** পদ্মা নদী।

- **Model answer:** পদ্মা সেতু পদ্মা নদীর উপর নির্মিত। → **is_hallucinated = No**
  *(Matches the reference.)*
- **Model answer:** পদ্মা সেতু মেঘনা নদীর উপর নির্মিত। → **is_hallucinated = Yes**
  *(Contradicts the reference; wrong river.)*
- **Model answer:** পদ্মা সেতু পদ্মা নদীর উপর নির্মিত এবং এটি ২০১৮ সালে উদ্বোধন করা হয়। →
  **is_hallucinated = Yes**
  *(Core answer is right, but the opening year is fabricated or incorrect; one wrong added claim makes
  the whole answer hallucinated.)*
- **Model answer:** পদ্মা সেতু বাংলাদেশের একটি গুরুত্বপূর্ণ সেতু যা যোগাযোগ ব্যবস্থায় বড় ভূমিকা রাখে। →
  **is_hallucinated = Yes**
  *(Fluent but never answers which river; a confident non-answer.)*

## 7. Common Pitfalls

- **Verbose is not hallucinated, and verbose is not correct.** Extra length is fine only if it stays
  true and actually answers the question.
- **One bad claim spoils the answer.** If a correct answer is bundled with a fabricated fact, mark
  `Yes`.
- **Don't reward fluent evasions.** A polished response that never delivers the correct fact is a
  hallucination (`Yes`).

## 8. Final Notes

- Label **every** row with `Yes` or `No`. Do not skip.
- If the model answer is genuinely ambiguous or only partially addresses the question, give your best
  label and add a short note or highlight it for supervisor review.
- Work independently and contact the supervisor for any case this guideline does not cover.
