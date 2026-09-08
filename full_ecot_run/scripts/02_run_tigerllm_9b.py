#!/usr/bin/env python3
"""Full-benchmark E-CoT run on TigerLLM-9B (HuggingFace Transformers).

TigerLLM is a Gemma3-architecture HuggingFace model (md-nishat-008/TigerLLM-9B-it),
not an Ollama model. Despite the "9B" name the checkpoint is 12.19B params
(Gemma3-12B shaped + SigLIP vision tower) = ~24.4 GB at bfloat16, so bf16 only
works on a 48 GB pod GPU. On a 24 GB card use the default nf4. Loaded once and
run sequentially; should NOT be co-located with the Ollama models.

Usage:
    # 24 GB lab GPU
    python full_ecot_run/scripts/02_run_tigerllm_9b.py --task all --track both
    # 48 GB pod GPU
    python full_ecot_run/scripts/02_run_tigerllm_9b.py --task all --track both --precision bf16

Outputs CSVs in full_ecot_run/results/tigerllm_9b/.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _ecot_core import ModelConfig, run_one
from _backend_tigerllm import make_call_fn

SLUG = "tigerllm_9b"
DISPLAY = "TigerLLM-9B-it"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=["qa", "summarization", "reasoning", "codemix", "all"],
                    default="all")
    ap.add_argument("--track", choices=["A", "B", "both"], default="both")
    ap.add_argument("--precision", choices=["bf16", "int8", "nf4"], default="nf4",
                    help="bf16 needs a 48 GB GPU (~24.4 GB weights); nf4 is the 24 GB default")
    ap.add_argument("--no-resume", action="store_true")
    args = ap.parse_args()

    call_fn = make_call_fn(max_new_tokens=1536, temperature=0.0, precision=args.precision)
    model = ModelConfig(slug=SLUG, display_name=DISPLAY, call_fn=call_fn)
    tasks  = (("qa", "summarization", "reasoning", "codemix")
              if args.task == "all" else (args.task,))
    tracks = ("A", "B") if args.track == "both" else (args.track,)
    for t in tasks:
        for tr in tracks:
            run_one(model, t, tr, resume=not args.no_resume)


if __name__ == "__main__":
    main()
