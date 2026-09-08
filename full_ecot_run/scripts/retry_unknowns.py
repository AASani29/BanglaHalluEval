#!/usr/bin/env python3
"""One-shot recovery pass for 'unknown'-verdict rows on already-completed judges.

TituLLM-3B (v1.1) is excluded on purpose: it is a base model structurally
incapable of the E-CoT JSON format (see _backend_titullm.py) -- retrying it
would just waste GPU time re-confirming the same failure. BanglaLLaMA-13B is
excluded per the "never run it" instruction. GPT-4.1-mini is run on a
different device and out of scope here.

For the other six judges, a small fraction of rows landed as 'unknown' from
transient parse failures (truncation, a stray formatting slip) despite the
original 3-retry loop in _ecot_core.run_one. This script gives each such row
exactly one more attempt, using the SAME model / precision / token budget as
that judge's own 02_run_<slug>.py script (no configuration changes). A row is
only overwritten in place if the retry actually parses; rows that fail again
are left completely untouched, including their original raw_response.

Usage:
    python full_ecot_run/scripts/retry_unknowns.py --model qwen2_5_32b
    python full_ecot_run/scripts/retry_unknowns.py --model all
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _ecot_core import TASKS, build_prompt, load_prompt, parse_json, make_output_row

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS = ROOT / "full_ecot_run" / "results"

# Token budgets copied verbatim from each judge's own 02_run_<slug>.py --
# retries must use identical generation settings to the original run.
MODEL_SPECS = {
    "qwen2_5_32b": dict(
        kind="ollama", model="qwen2.5:32b-instruct",
        num_predict={"qa": 1024, "summarization": 1536, "reasoning": 1536},
        num_ctx={"qa": 4096, "summarization": 4096, "reasoning": 6144},
        tasks=["qa", "summarization", "reasoning"],
    ),
    "deepseek_r1_14b": dict(
        kind="ollama", model="deepseek-r1:14b",
        num_predict={"qa": 4096, "summarization": 4096, "reasoning": 6144},
        num_ctx={"qa": 8192, "summarization": 8192, "reasoning": 12288},
        tasks=["qa", "summarization", "reasoning"],
    ),
    "gemma2_27b": dict(
        kind="ollama", model="gemma2:27b",
        num_predict={"qa": 1024, "summarization": 1536, "reasoning": 1536},
        num_ctx={"qa": 4096, "summarization": 4096, "reasoning": 8192},
        tasks=["qa", "summarization", "reasoning"],
    ),
    "llama3_1_8b": dict(
        kind="ollama", model="llama3.1:8b",
        num_predict={"qa": 1024, "summarization": 1536, "reasoning": 1536},
        num_ctx={"qa": 4096, "summarization": 4096, "reasoning": 6144},
        tasks=["qa", "summarization", "reasoning"],
    ),
    "mistral_nemo": dict(
        kind="ollama", model="mistral-nemo:latest",
        num_predict={"qa": 1024, "summarization": 1536, "reasoning": 1536, "codemix": 1024},
        num_ctx={"qa": 4096, "summarization": 4096, "reasoning": 6144, "codemix": 4096},
        tasks=["qa", "summarization", "reasoning", "codemix"],
    ),
    "tigerllm_9b": dict(
        kind="tigerllm",
        tasks=["qa", "summarization", "reasoning", "codemix"],
    ),
}


def out_paths_for(tasks):
    for task in tasks:
        suffix = "codemix" if task == "codemix" else task
        yield task, "A", f"{suffix}_gt_ecot.csv"
        yield task, "B", f"{suffix}_hallu_ecot.csv"


def make_backend(spec):
    if spec["kind"] == "ollama":
        from _backend_ollama import make_call_fn
        np_map, nc_map = spec["num_predict"], spec["num_ctx"]
        return make_call_fn(spec["model"], lambda t: np_map[t], lambda t: nc_map[t])
    from _backend_tigerllm import make_call_fn
    return make_call_fn(max_new_tokens=1536, temperature=0.0, precision="nf4")


def retry_model(slug: str, spec: dict) -> tuple[int, int]:
    print(f"\n=== {slug} ===")
    call_fn = None  # lazy: only load/connect once we know there's work to do
    total_unknown = total_recovered = 0

    for task, track, fname in out_paths_for(spec["tasks"]):
        p = RESULTS / slug / fname
        if not p.exists():
            continue
        with open(p, encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)

        unknown_idx = [i for i, r in enumerate(rows) if r.get("is_hallucinated") == "unknown"]
        if not unknown_idx:
            continue
        if call_fn is None:
            call_fn = make_backend(spec)

        template = load_prompt(task)
        recovered = 0
        for i in unknown_idx:
            row = rows[i]
            try:
                prompt = build_prompt(task, track, pd.Series(row), template)
            except Exception:
                continue
            raw = call_fn(prompt, task)
            parsed, err = parse_json(raw or "")
            if parsed is None:
                continue
            row.update(make_output_row(task, raw, parsed, err, row.get("id_key", "")))
            recovered += 1

        print(f"  {fname:28s} unknown={len(unknown_idx):5d}  recovered={recovered:5d}")
        total_unknown += len(unknown_idx)
        total_recovered += recovered

        if recovered > 0:
            tmp = p.with_suffix(".csv.tmp")
            with open(tmp, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(rows)
            tmp.replace(p)

    print(f"  -> {slug} total: unknown={total_unknown}  recovered={total_recovered}")
    return total_unknown, total_recovered


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="all", choices=list(MODEL_SPECS) + ["all"])
    args = ap.parse_args()
    slugs = list(MODEL_SPECS) if args.model == "all" else [args.model]

    grand_unknown = grand_recovered = 0
    for slug in slugs:
        u, r = retry_model(slug, MODEL_SPECS[slug])
        grand_unknown += u
        grand_recovered += r

    print(f"\n=== GRAND TOTAL: unknown={grand_unknown}  recovered={grand_recovered} ===")


if __name__ == "__main__":
    main()
