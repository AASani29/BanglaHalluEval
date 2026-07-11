# Annotation Guidelines: Summarization Hallucination

## 1. Task Overview

You are given a Bengali source **document** and a **summary** of that document. Your job is to decide,
for each item, whether the summary is **hallucinated**, meaning whether it says anything that the
document does not support or that contradicts the document.

You will assign exactly one label per row:

- **`is_hallucinated` = Yes**: the summary is hallucinated (unfaithful to the document).
- **`is_hallucinated` = No**: the summary is faithful to the document.

You are **not** told whether an item is meant to be faithful or hallucinated. Judge only what you see.

## 2. What You Will See

| Column | Meaning |
|--------|---------|
| `document` | The Bengali source document. This is the only ground truth. |
| `summary` | The summary you must judge. |
| `is_hallucinated` | **You fill this in:** `Yes` or `No`. |

## 3. Definition

A summary is **faithful** when every claim it makes can be traced back to the document. A summary is
**hallucinated** when it introduces content the document does not support. There are two patterns:

- **Intrinsic hallucination.** The summary **contradicts** the document. It misstates a fact that is
  in the document (wrong number, wrong name, wrong cause and effect, wrong direction of a change).
- **Extrinsic hallucination.** The summary **adds** information that is **not in** the document at all
  (a fabricated detail, statistic, name, or conclusion).

A good summary may **leave out** details. That is normal and is **not** a hallucination. The problem
is only *adding* or *contradicting*, never *omitting*.

## 4. Labeling Rules

**Mark `is_hallucinated` = Yes if the summary:**

- States a fact that contradicts the document (intrinsic).
- Introduces a detail, number, name, quote, cause, or conclusion that is not in the document
  (extrinsic).
- Overstates or reverses something in the document (e.g. document says "may reduce", summary says
  "eliminates"; document says prices *rose*, summary says they *fell*).

**Mark `is_hallucinated` = No if the summary:**

- Contains only claims that are stated in or directly entailed by the document.
- Is shorter than the document and omits details but adds nothing and contradicts nothing.
- Paraphrases or compresses the document while keeping the facts intact.

## 5. Examples

> **Document:** গত অর্থবছরে দেশের চা রপ্তানি ১২ শতাংশ বৃদ্ধি পেয়েছে। রপ্তানির প্রধান গন্তব্য ছিল যুক্তরাজ্য।

- **Summary:** গত অর্থবছরে চা রপ্তানি বেড়েছে, এবং প্রধান গন্তব্য ছিল যুক্তরাজ্য। → **is_hallucinated = No**
  *(Faithful compression; it omits the exact figure but adds and contradicts nothing.)*
- **Summary:** গত অর্থবছরে চা রপ্তানি ১২ শতাংশ কমেছে। → **is_hallucinated = Yes** (intrinsic)
  *(Reverses the direction of the change; the document says it rose.)*
- **Summary:** গত অর্থবছরে চা রপ্তানি ১২ শতাংশ বৃদ্ধি পেয়েছে এবং সরকার নতুন কর ছাড় ঘোষণা করেছে। →
  **is_hallucinated = Yes** (extrinsic)
  *(The tax-break clause appears nowhere in the document, so it is a fabricated addition.)*

> **Document:** নতুন ওষুধটি পরীক্ষায় কিছু রোগীর উপসর্গ কমাতে সাহায্য করতে পারে বলে গবেষকরা জানিয়েছেন।

- **Summary:** গবেষকরা জানিয়েছেন নতুন ওষুধটি কিছু রোগীর উপসর্গ কমাতে সাহায্য করতে পারে। →
  **is_hallucinated = No**
- **Summary:** নতুন ওষুধটি সব রোগীকে সম্পূর্ণ সুস্থ করে তোলে। → **is_hallucinated = Yes**
  *(Overstates "may help some patients" into "cures all patients", which is unsupported and
  contradictory.)*

## 6. Common Pitfalls

- **Omission is not hallucination.** A summary that drops details is fine. Only mark `Yes` for added
  or contradicted content.
- **Watch the modifiers.** "may / some / partly" versus "will / all / completely" changes meaning.
  Strengthening a hedged claim into a certain one is a hallucination.
- **Plausible is not supported.** A fabricated statistic or name is still a hallucination even if it
  sounds reasonable. Check that it is actually in the document.

## 7. Final Notes

- Label **every** row with `Yes` or `No`. Do not skip.
- If a summary is borderline (e.g. a claim that is *arguably* implied), give your best label and add a
  short note or highlight it for supervisor review.
- Work independently and contact the supervisor for any case this guideline does not cover.
