"""TigerLLM backend (HuggingFace Transformers, single-GPU).

Loads md-nishat-008/TigerLLM-9B-it once and returns a callable that produces
JSON-shaped text.

NOTE on size: despite the "9B" in the repo name, the config is Gemma3-12B
shaped (48 layers, hidden 3840) and the checkpoint carries a SigLIP vision
tower, totalling 12.19B parameters. That is ~24.4 GB at bfloat16, which does
NOT fit a 24 GB card -- accelerate silently offloads layers to CPU and
generation slows to a crawl. Pick precision to match the GPU:

    bf16  ~24.4 GB   48 GB pod GPUs only (A40 / A6000 / L40S)
    int8  ~12.2 GB   fits 24 GB, ~2-3x slower than nf4
    nf4   ~6.7 GB    fits 24 GB comfortably, the local-lab default

Requires: torch, transformers>=4.50 (Gemma3 support), accelerate.
int8/nf4 additionally require bitsandbytes.
"""

from __future__ import annotations

import sys
from typing import Callable

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MODEL_ID = "md-nishat-008/TigerLLM-9B-it"

PRECISIONS = ("bf16", "int8", "nf4")


def make_call_fn(max_new_tokens: int = 1024, temperature: float = 0.0,
                 precision: str = "nf4") -> Callable[[str, str], str]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if precision not in PRECISIONS:
        raise ValueError(f"precision must be one of {PRECISIONS}, got {precision!r}")

    load_kwargs = {"device_map": "auto", "dtype": torch.bfloat16}
    if precision != "bf16":
        from transformers import BitsAndBytesConfig
        if precision == "nf4":
            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
        else:
            load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)

    print(f"[tigerllm] loading {MODEL_ID} ({precision}) ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, **load_kwargs)
    model.eval()

    device = next(model.parameters()).device
    if torch.cuda.is_available():
        used = torch.cuda.memory_allocated() / 1e9
        free = torch.cuda.mem_get_info()[0] / 1e9
        print(f"[tigerllm] ready on {device}  weights={used:.1f} GB  free={free:.1f} GB")
    else:
        print(f"[tigerllm] ready on {device}")

    do_sample = temperature > 0.0

    def call(prompt: str, task: str) -> str:
        # Use the chat template so the JSON-shaped response training kicks in.
        messages = [{"role": "user", "content": prompt}]
        enc = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        ).to(device)
        input_len = enc["input_ids"].shape[-1]

        with torch.inference_mode():
            outputs = model.generate(
                **enc,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=temperature if do_sample else None,
                top_p=None,
                top_k=None,
                pad_token_id=tokenizer.eos_token_id,
            )
        generated = outputs[0][input_len:]
        return tokenizer.decode(generated, skip_special_tokens=True).strip()

    return call
