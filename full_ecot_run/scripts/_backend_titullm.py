"""TituLLM-3B backend (HuggingFace Transformers, bfloat16, single-GPU).

Loads hishab/titulm-llama-3.2-3b-v1.1 once and returns a callable that produces
JSON-shaped text. This is deliberately the SAME checkpoint used by the baseline
and CoT runs in scripts/eval10_titullm.py, so the E-CoT numbers sit beside those
without a model substitution.

~6.4 GB at bfloat16 -- fits any 12 GB+ card.

KNOWN LIMITATION (measured 2026-08-17 on this repo's prompts): v1.1 is a base
continued-pretrained model, not instruction-tuned. Its chat template carries no
role markers, and `<|end_of_text|>` is essentially never sampled, so generation
runs to `max_new_tokens` on every row and the output is free-form Bengali prose
rather than the E-CoT JSON object. Expect a very high parse-error rate and
correspondingly many "unknown" verdicts. eval10_titullm.py avoids this by
constraining decoding to the yes/no token ids, which free-form E-CoT cannot do.
`hishab/titulm-llama-3.2-3b-v2.0-Instruct-v1.0` does emit JSON, but is a
different model from the one used by the other TituLLM runs.

Because generation never stops early, `max_new_tokens` alone sets the per-row
cost -- it is the main runtime lever for this judge.

Requires: torch, transformers, accelerate.
"""

from __future__ import annotations

import sys
from typing import Callable

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MODEL_ID = "hishab/titulm-llama-3.2-3b-v1.1"


def make_call_fn(max_new_tokens: int = 1024, temperature: float = 0.0) -> Callable[[str, str], str]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[titullm] loading {MODEL_ID} in bfloat16 ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()

    device = next(model.parameters()).device
    # v1.1 ships a passthrough template (no role markers). Mirror the
    # `apply_chat` fallback in scripts/eval10_common.py rather than assuming.
    has_template = bool(getattr(tokenizer, "chat_template", None))
    if torch.cuda.is_available():
        used = torch.cuda.memory_allocated() / 1e9
        free = torch.cuda.mem_get_info()[0] / 1e9
        print(f"[titullm] ready on {device}  weights={used:.1f} GB  free={free:.1f} GB  "
              f"chat_template={has_template}  max_new_tokens={max_new_tokens}")
    else:
        print(f"[titullm] ready on {device}  chat_template={has_template}")

    do_sample = temperature > 0.0

    def call(prompt: str, task: str) -> str:
        if has_template:
            enc = tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                add_generation_prompt=True,
                return_tensors="pt",
                return_dict=True,
            ).to(device)
        else:
            enc = tokenizer(prompt, return_tensors="pt").to(device)
        input_len = enc["input_ids"].shape[-1]

        with torch.inference_mode():
            outputs = model.generate(
                **enc,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=temperature if do_sample else None,
                top_p=None,
                top_k=None,
                pad_token_id=tokenizer.pad_token_id,
            )
        generated = outputs[0][input_len:]
        return tokenizer.decode(generated, skip_special_tokens=True).strip()

    return call
