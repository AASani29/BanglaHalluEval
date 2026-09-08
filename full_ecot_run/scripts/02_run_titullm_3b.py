#!/usr/bin/env python3
"""Full-benchmark E-CoT run on TituLLM-3B (HuggingFace Transformers, bfloat16).

TituLLM is a HuggingFace model, not an Ollama model. Loaded once in bfloat16
(~6.4 GB) and run sequentially on a single GPU.

Uses hishab/titulm-llama-3.2-3b-v1.1 -- the same checkpoint as the baseline and
CoT runs in scripts/eval10_titullm.py, so E-CoT numbers are comparable to those
without a model substitution. That checkpoint is a base model and emits very
little parseable E-CoT JSON; see the KNOWN LIMITATION note in
_backend_titullm.py before interpreting the parse-error and "unknown" columns.

Usage:
    python full_ecot_run/scripts/02_run_titullm_3b.py --task all --track both

Outputs CSVs in full_ecot_run/results/titullm_3b/.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _ecot_core import ModelConfig, run_one
from _backend_titullm import make_call_fn

SLUG = "titullm_3b"
DISPLAY = "TituLLM-3B"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=["qa", "summarization", "reasoning", "codemix", "all"],
                    default="all")
    ap.add_argument("--track", choices=["A", "B", "both"], default="both")
    ap.add_argument("--no-resume", action="store_true")
    args = ap.parse_args()

    call_fn = make_call_fn(max_new_tokens=1536, temperature=0.0)
    model = ModelConfig(slug=SLUG, display_name=DISPLAY, call_fn=call_fn)
    tasks = (("qa", "summarization", "reasoning", "codemix")
             if args.task == "all" else (args.task,))
    tracks = ("A", "B") if args.track == "both" else (args.track,)
    for t in tasks:
        for tr in tracks:
            run_one(model, t, tr, resume=not args.no_resume)


if __name__ == "__main__":
    main()
