# Annotation Guidelines: Mathematical Reasoning Hallucination

## 1. Task Overview

You are given a Bengali **mathematical word problem** (from the SOMADHAN dataset), a step-by-step
**reasoning chain** that solves it, and the **final answer** produced by that chain. Your job is to
decide whether the reasoning chain is **hallucinated**, meaning whether it contains any incorrect
step, fabricated assumption, or wrong conclusion.

You will assign exactly one label per row:

- **`is_hallucinated` = Yes**: the reasoning chain contains an error or fabrication.
- **`is_hallucinated` = No**: every step is correct and the final answer follows and is right.

You are **not** told whether an item is meant to be correct or wrong. Judge only what you see.

## 2. What You Will See

| Column | Meaning |
|--------|---------|
| `question` | The Bengali math word problem. |
| `hallucinated_chain` (reasoning chain) | The step-by-step solution you must judge. |
| `answer` / final answer | The final result the chain arrives at. |
| `is_hallucinated` | **You fill this in:** `Yes` or `No`. |

> **Important:** You must evaluate the **whole chain**, not just the final answer. A chain can reach a
> number that looks reasonable while containing a wrong step, and a chain with a correct final number
> can still be hallucinated if it got there through a flawed step. Check every step.

## 3. Definition

A reasoning chain is **hallucinated** if **any** of the following is true:

| Error type | What it looks like |
|------------|--------------------|
| **Arithmetic slip** | A single calculation is wrong (e.g. ২৫ × ৮ written as ১৮০ instead of ২০০). |
| **Formula misapplication** | The wrong operation is used (divides instead of multiplies, adds instead of subtracts), often with wording that tries to justify it. |
| **Variable confusion** | Two quantities are swapped (e.g. uses the manager's rate where the worker's rate belongs). |
| **Invalid deduction** | A conclusion is drawn that does not logically follow from the previous step. |
| **Hallucinated intermediate fact** | An assumption is introduced that is **nowhere** in the problem (e.g. "workers get 2 days off" when the problem never says so). |
| **Semantic drift** | The chain quietly changes what the problem is asking (e.g. the problem asks for wages **plus** tax, but the chain answers wages alone). |

If none of these occurs and the final answer is correct, the chain is **not** hallucinated.

## 4. Labeling Rules

**Mark `is_hallucinated` = Yes if:**

- Any arithmetic step is computed incorrectly.
- Any step uses a wrong operation or a wrong or swapped quantity.
- The chain assumes a fact that is not stated in the problem.
- A step's conclusion does not follow from what came before.
- The chain answers a different question than the one asked (drift).
- The final answer is wrong, **or** it is right but reached through a flawed step.

**Mark `is_hallucinated` = No if:**

- Every arithmetic step is correct.
- Every operation and every quantity used matches the problem.
- No fact is used that the problem does not provide.
- Each step follows logically from the previous one.
- The final answer correctly answers exactly what was asked.

## 5. How to Check a Chain (recommended procedure)

1. Read the problem and note **what is being asked** and **what numbers or quantities** are given.
2. Go step by step. For each step, verify: *Is the arithmetic right? Is the right operation used? Are
   the right quantities used? Does this follow from the last step? Is every fact from the problem?*
3. Confirm the final answer both **matches the chain** and **answers the actual question**.
4. The **first** violation you find is enough to mark `Yes`. You do not have to catalogue them all.

## 6. Examples

> **Problem:** একজন শ্রমিক ২৫ দিন কাজ করেন, প্রতিদিন ৮ ঘণ্টা। মোট কত ঘণ্টা কাজ করলেন?

- **Chain:** ২৫ দিন × ৮ ঘণ্টা/দিন = ২০০ ঘণ্টা। উত্তর: ২০০ ঘণ্টা। → **is_hallucinated = No**
  *(Correct operation, correct arithmetic, answers what was asked.)*
- **Chain:** ২৫ দিন × ৮ ঘণ্টা/দিন = ১৮০ ঘণ্টা। উত্তর: ১৮০ ঘণ্টা। → **is_hallucinated = Yes**
  *(Arithmetic slip: ২৫ × ৮ = ২০০, not ১৮০.)*
- **Chain:** মোট ঘণ্টা বের করতে দিনকে ঘণ্টা দিয়ে ভাগ করি: ২৫ ÷ ৮ = ৩.১২৫ ঘণ্টা। → **is_hallucinated = Yes**
  *(Formula misapplication: division instead of multiplication.)*
- **Chain:** প্রশ্নে বলা আছে শ্রমিক মাসে ২ দিন ছুটি নেন, তাই কার্যকর দিন = ২৫ − ২ = ২৩; ২৩ × ৮ = ১৮৪ ঘণ্টা। →
  **is_hallucinated = Yes**
  *(Hallucinated intermediate fact: the "2 days off" assumption appears nowhere in the problem.)*

## 7. Common Pitfalls

- **Do not judge by the final number alone.** A correct-looking answer can hide a wrong step, and a
  wrong step makes the chain hallucinated even if the number is right.
- **Plausible-sounding Bengali is not proof.** Some errors are written to *sound* justified ("তাই ভাগ
  করি…"). Check the math, not the fluency.
- **Read what is actually asked.** If the problem wants the total but the chain answers a sub-part,
  that is semantic drift, so mark `Yes`.

## 8. Final Notes

- Label **every** row with `Yes` or `No`. Do not skip.
- If a step is genuinely ambiguous (e.g. the problem itself is under-specified), give your best label
  and add a short note or highlight it for supervisor review.
- Work independently and contact the supervisor for any case this guideline does not cover.
