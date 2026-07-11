# Annotation Guidelines: Code-mixed Conversion Quality

## 1. Task Overview

This task checks the **quality of the code-mixed (Banglish) conversion itself**, before it is used
anywhere else. Each item started as an **original Bengali** QA passage, question, or answer, which was
then **converted** into Romanised code-mixed Bangla-English text. You judge how good that conversion is
on **two independent dimensions**:

1. **`meaning_preserved`** (Yes / No): does the code-mixed version carry the **same meaning** as the
   original Bengali?
2. **`naturalness_1to5`** (1 to 5): how **natural and fluent** does the code-mixed text read, as
   something a real bilingual Bangladeshi would actually write?

> These are two separate judgments. A conversion can preserve the meaning perfectly (Yes) yet read
> awkwardly (low naturalness), or read smoothly (high naturalness) while dropping or changing meaning
> (No). Judge each column on its own.

## 2. What You Will See

| Column | Meaning |
|--------|---------|
| Original Bengali text | The source (context, question, or answer) in Bengali script. |
| Code-mixed text | The Romanised Banglish conversion you must judge. |
| `meaning_preserved` | **You fill this in:** `Yes` or `No`. |
| `naturalness_1to5` | **You fill this in:** a single whole number 1, 2, 3, 4, or 5. |

## 3. Dimension 1: `meaning_preserved` (Yes / No)

**Definition.** The conversion preserves meaning when the code-mixed text says the **same thing** as
the original Bengali (the same facts, the same question, the same answer) with nothing important
added, dropped, or changed.

**Mark `meaning_preserved` = Yes if:**

- Every fact, name, number, and relationship from the original is present and unchanged.
- The question asks for the same thing; the answer gives the same thing.
- Only the script or spelling changed (Bengali to Romanised), not the content.

**Mark `meaning_preserved` = No if:**

- Any fact, name, number, or date is dropped, added, or changed.
- The question or answer now means something different.
- A word is mistranslated so the sense changes (e.g. "মা" rendered as "sister").
- Part of the original content is missing.

*Spelling and transliteration choices do not affect this column.* Only whether the **meaning** is the
same matters here.

## 4. Dimension 2: `naturalness_1to5` (1 to 5 scale)

**Definition.** Naturalness is how much the code-mixed text reads like genuine, everyday Banglish that
a bilingual Bangladeshi would actually write, rather than stiff, machine-like, or word-for-word text.

Rate **only the fluency and style**, independently of whether the meaning is correct.

| Score | Meaning | What it reads like |
|-------|---------|--------------------|
| **5** | Completely natural | Reads exactly like real Banglish; you would not guess it was converted. |
| **4** | Mostly natural | Fluent with a slight awkwardness or one stiff word choice. |
| **3** | Acceptable but mixed | Understandable, but noticeably clunky in places; some unnatural phrasing. |
| **2** | Largely unnatural | Word-for-word or machine-like; awkward ordering; hard to read smoothly. |
| **1** | Very unnatural | Broken, garbled, or barely readable as Banglish. |

Guidance:

- Judge how a **real bilingual speaker** would react, not a strict grammarian.
- Awkward word order, over-literal transliteration, and forced English substitutions **lower** the
  score.
- Minor spelling variation that people commonly use does **not** lower the score. Natural Banglish is
  spelled inconsistently.

## 5. Examples

> **Original Bengali:** ১৯৬৫ সালে জে. কে. রাউলিং ইংল্যান্ডে জন্মগ্রহণ করেন।

- **Conversion:** `1965 sale J. K. Rowling England-e jonmogrohon koren.`
  → `meaning_preserved = Yes`, `naturalness_1to5 = 5`
  *(Same meaning; reads like natural Banglish.)*
- **Conversion:** `1965 shongkhok bochore J. K. Rowling England namok deshe jonmo laav koren.`
  → `meaning_preserved = Yes`, `naturalness_1to5 = 2`
  *(Meaning is intact, but the phrasing is stiff and over-formal, not how people actually write.)*
- **Conversion:** `1975 sale J. K. Rowling America-te jonmogrohon koren.`
  → `meaning_preserved = No`, `naturalness_1to5 = 5`
  *(Reads naturally, but the year and the country were both changed, so the meaning is broken.)*
- **Conversion:** `J. K. Rowling born hoise ek jaygায় ek somoy.`
  → `meaning_preserved = No`, `naturalness_1to5 = 1`
  *(Drops the year and place, and the text is garbled, so it fails on both dimensions.)*

## 6. Common Pitfalls

- **Keep the two columns separate.** Do not lower naturalness because the meaning is wrong, and do not
  mark meaning `No` just because the style is awkward.
- **Don't punish normal Banglish spelling.** Inconsistent spelling is authentic and should not reduce
  either score.
- **Small omissions still break meaning.** A dropped number or name is enough for `meaning_preserved =
  No`, even if the sentence otherwise reads well.

## 7. Final Notes

- Fill **both** columns for **every** row: `meaning_preserved` as `Yes` or `No`, and `naturalness_1to5`
  as a whole number from 1 to 5. Do not skip.
- If you are genuinely torn between two adjacent naturalness scores, pick the lower one and add a short
  note or highlight it for supervisor review.
- Work independently and contact the supervisor for any case this guideline does not cover.
