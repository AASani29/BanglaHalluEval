# Annotation Guidelines: Code-mixed (Banglish) QA Hallucination

## 1. Task Overview

This task is the same idea as the QA task, but the text is **code-mixed**: Romanised Bengali mixed
with English (often called *Banglish*), for example
`"1965 saler 31 July England-er Yate shohore jonmogrohon koren J.K. Rowling..."`.

You are given a code-mixed **context** passage, a code-mixed **question**, and a **model answer**.
Your job is to decide whether the answer is **hallucinated** relative to the context and question.

You will assign exactly one label per row:

- **`is_hallucinated` = Yes**: the answer is hallucinated.
- **`is_hallucinated` = No**: the answer is faithful and correct.

You are **not** told whether an item is meant to be correct or wrong. Judge only what you see.

## 2. What You Will See

| Column | Meaning |
|--------|---------|
| `codemix_context` (context) | The code-mixed source passage. This is the only ground truth. |
| `codemix_question` (question) | The code-mixed question. |
| `answer` (model answer) | The answer you must judge. |
| `is_hallucinated` | **You fill this in:** `Yes` or `No`. |

## 3. Definition

Exactly as in the QA task, an answer is **hallucinated** when it is **factually incorrect** or **not
supported by the context**. The two patterns are:

- **Factualness error.** A wrong fact (wrong name, number, date, place, or relationship compared to
  the context).
- **Comprehension error.** The answer misreads the question or the context: it answers a different
  question, or confuses two entities.

Judge everything **relative to the code-mixed context**, regardless of the script or spelling used.

## 4. Reading Code-mixed Text

- **Spelling varies.** The same word may be written many ways (`shohor` / `sohor`, `koren` / `koren`).
  Spelling differences are **not** hallucinations. Judge the **meaning**.
- **Mixed script is normal.** English words, numbers, and names inside Bengali sentences are expected.
- Focus on **what the answer claims**, not on how it is transliterated.

## 5. Labeling Rules

**Mark `is_hallucinated` = Yes if the answer:**

- Contradicts a fact in the context (context says one value, answer says another).
- Adds a specific detail (name, number, date, place) not present in or inferable from the context.
- Answers a different question than the one asked, or confuses two people or things.
- Is partly correct but contains **any** fabricated or wrong piece of information.

**Mark `is_hallucinated` = No if the answer:**

- Is fully supported by the context and correctly answers the question.
- Is a reworded or re-transliterated version of the correct answer with the same meaning.
- Correctly says the information is unavailable, **when the context genuinely lacks it**.

## 6. Examples

> **Context:** `"1965 saler 31 July England-er Yate shohore J.K. Rowling jonmogrohon koren. Tar mayer nam Anni."`
> **Question:** `J. K. Rowling-er mayer nam ki?`

- **Answer:** `Tar mayer nam Anni.` → **is_hallucinated = No**
  *(Directly supported by the context.)*
- **Answer:** `J. K. Rowling-er mayer nam chhilo Margaret Anne.` → **is_hallucinated = Yes**
  *(Adds "Margaret Anne", a name not in the context, so it is a fabricated detail.)*
- **Answer:** `Tini 1975 sale jonmogrohon koren.` → **is_hallucinated = Yes**
  *(Wrong fact and wrong question; the context says 1965 and the question was about the mother's
  name.)*

> **Context:** `"Padma Bridge-er length 6.15 kilometer."`
> **Question:** `Padma Bridge koto lomba?`

- **Answer:** `Padma Bridge prai 6 km lomba.` → **is_hallucinated = No**
  *(Correct paraphrase or rounding, same meaning.)*
- **Answer:** `Padma Bridge 9 km lomba.` → **is_hallucinated = Yes**
  *(Contradicts the number in the context.)*

## 7. Common Pitfalls

- **Do not penalise spelling or transliteration.** `sohor` versus `shohor` is not a hallucination.
  Only the **facts** matter.
- **Plausible is not supported.** An added fact that sounds right is still a hallucination if the
  context does not support it.
- **Partial correctness means Yes.** Any fabricated or wrong piece makes the whole answer `Yes`.

## 8. Final Notes

- Label **every** row with `Yes` or `No`. Do not skip.
- If the code-mixed text is hard to parse or genuinely ambiguous, give your best label and add a short
  note or highlight it for supervisor review.
- Work independently and contact the supervisor for any case this guideline does not cover.
