# Annotation Guidelines: Question Answering (QA) Hallucination

## 1. Task Overview

You are given a Bengali **reading-comprehension** item: a source **context** passage, a **question**
about that passage, and a **model answer**. Your job is to decide, for each item, whether the model
answer is **hallucinated**, meaning whether it contains information that is wrong or that the context
does not support.

You will assign exactly one label per row:

- **`is_hallucinated` = Yes**: the answer is hallucinated.
- **`is_hallucinated` = No**: the answer is faithful and correct.

You are **not** told whether an item is meant to be correct or wrong. Judge only what you see.

## 2. What You Will See

| Column | Meaning |
|--------|---------|
| `context` | The Bengali source passage. This is the only ground truth. |
| `question` | The Bengali question. |
| `answer` (model answer) | The answer you must judge. |
| `is_hallucinated` | **You fill this in:** `Yes` or `No`. |

## 3. Definition

A QA answer is **hallucinated** when it states something that is **factually incorrect** or **not
supported by the context**. The two error patterns you will most often see are:

- **Factualness error.** The answer gives a wrong fact: a wrong name, number, date, place, or
  relationship compared to what the context says.
- **Comprehension error.** The answer misreads the question or the context: it answers a different
  question, confuses two entities, or draws a conclusion the passage does not support.

The reference point is always the **context**. If the answer adds specific details (names, dates,
figures) that do not appear in and cannot be inferred from the context, treat those added details as
unsupported, even if they might sound plausible.

## 4. Labeling Rules

**Mark `is_hallucinated` = Yes if the answer:**

- Contradicts a fact stated in the context (e.g. context says 1965, answer says 1975).
- Contains a specific detail (name, number, date, place) that the context neither states nor implies.
- Answers a different question than the one asked, or confuses two people or things in the passage.
- Is partly correct but contains **any** fabricated or wrong piece of information.

**Mark `is_hallucinated` = No if the answer:**

- Is fully supported by the context and correctly answers the question.
- Is a paraphrase or reworded version of the correct answer that keeps the same meaning.
- Correctly states that the information is not available, **when the context genuinely does not
  contain it**.

## 5. Examples

> **Context:** ১৯৬৫ সালের ৩১শে জুলাই ইংল্যান্ডের ইয়েট শহরে জে. কে. রাউলিং জন্মগ্রহণ করেন। তাঁর মায়ের নাম অ্যান।
> **Question:** জে. কে. রাউলিং-এর মায়ের নাম কী?

- **Answer:** তাঁর মায়ের নাম অ্যান। → **is_hallucinated = No**
  *(Directly supported by the context.)*
- **Answer:** তাঁর মায়ের নাম মার্গারেট অ্যান। → **is_hallucinated = Yes**
  *(Adds "মার্গারেট", a name not present in the context, so it is a fabricated detail.)*
- **Answer:** তিনি ১৯৭৫ সালে জন্মগ্রহণ করেন। → **is_hallucinated = Yes**
  *(Wrong fact, and it also answers the wrong question; the context says 1965, and the question was
  about the mother's name.)*

> **Context:** পদ্মা সেতুর দৈর্ঘ্য ৬.১৫ কিলোমিটার।
> **Question:** পদ্মা সেতুর দৈর্ঘ্য কত?

- **Answer:** পদ্মা সেতুর দৈর্ঘ্য প্রায় ৬ কিলোমিটার। → **is_hallucinated = No**
  *(Correct paraphrase or rounding that preserves the meaning.)*
- **Answer:** পদ্মা সেতুর দৈর্ঘ্য ৯ কিলোমিটার। → **is_hallucinated = Yes**
  *(Contradicts the number in the context.)*

## 6. Common Pitfalls

- **"It sounds true, so it must be fine."** Judge against the **context**, not the internet. An added
  fact that happens to be true in the real world is still a hallucination if the passage does not
  support it.
- **Partial correctness.** If any part of the answer is fabricated or wrong, the whole answer is
  `Yes`, even if the rest is correct.
- **Extra harmless wording.** Polite framing, restating the question, or a fuller sentence is fine as
  long as no new unsupported fact is introduced.

## 7. Final Notes

- Label **every** row with `Yes` or `No`. Do not skip.
- If a row is genuinely ambiguous (for example, the context is unclear), give your best label and add
  a short note or highlight it for supervisor review.
- Work independently and contact the supervisor for any case this guideline does not cover.
