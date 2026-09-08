#!/usr/bin/env python3
"""Progress dashboard for the full_ecot_run E-CoT sweep.

Reads every judge's result CSVs directly (no need for the run to be live) and
prints a one-line-per-model summary: rows done/total, parse-error count, and
the yes/no/unknown verdict split. Also reports whether the 'ecot' tmux
session is alive and current GPU memory use.

Usage:
    python full_ecot_run/scripts/check_progress.py                # summary table
    python full_ecot_run/scripts/check_progress.py --verbose       # + per task/track breakdown
    python full_ecot_run/scripts/check_progress.py --model qwen2_5_32b
    python full_ecot_run/scripts/check_progress.py --watch         # + live rows/sec over 30s

BanglaLLaMA-13B is deliberately excluded from the sweep and is listed
separately at the bottom as a reminder, not counted in any total.
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS = ROOT / "full_ecot_run" / "results"

# (task, track_suffix, expected_row_count) -- suffix matches _ecot_core.out_path_for
TASK_TRACKS = [
    ("qa", "gt", 1000), ("qa", "hallu", 4000),
    ("summarization", "gt", 1000), ("summarization", "hallu", 3000),
    ("reasoning", "gt", 1000), ("reasoning", "hallu", 1000),
    ("codemix", "gt", 100), ("codemix", "hallu", 400),
]
NO_CODEMIX = [t for t in TASK_TRACKS if t[0] != "codemix"]

# slug -> (display name, applicable task/track list)
MODELS = [
    ("tigerllm_9b",     "TigerLLM-9B (nf4)",     TASK_TRACKS),
    ("titullm_3b",      "TituLLM-3B (v1.1)",     TASK_TRACKS),
    ("qwen2_5_32b",     "Qwen2.5-32B-Instruct",  NO_CODEMIX),
    ("deepseek_r1_14b", "DeepSeek-R1-14B",       NO_CODEMIX),
    ("gemma2_27b",      "Gemma2-27B",            NO_CODEMIX),
    ("llama3_1_8b",     "Llama3.1-8B",           NO_CODEMIX),
    ("mistral_nemo",    "Mistral-Nemo-12B",      TASK_TRACKS),
    ("gpt4_1_mini",     "GPT-4.1-mini",          NO_CODEMIX),
]
EXCLUDED = [("bangla_llama_13b", "BanglaLLaMA-13B  (excluded from the sweep, not run)")]


def count_rows(path: Path):
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            rows = list(csv.DictReader(f))
    except Exception as exc:
        return {"n": 0, "err": 0, "verdicts": Counter(), "read_error": str(exc)}
    err = sum(1 for r in rows if r.get("parse_error"))
    verdicts = Counter(r.get("is_hallucinated", "") for r in rows)
    return {"n": len(rows), "err": err, "verdicts": verdicts}


def bar(done: int, total: int, width: int = 20) -> str:
    if total == 0:
        return "?" * width
    filled = int(round(width * min(done, total) / total))
    return "#" * filled + "-" * (width - filled)


def sh(cmd: str) -> str:
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", help="only show this model slug")
    ap.add_argument("--verbose", action="store_true", help="show per task/track breakdown")
    ap.add_argument("--watch", action="store_true", help="also sample rows/sec on the most recently written CSV over 30s")
    args = ap.parse_args()

    models = MODELS if not args.model else [m for m in MODELS if m[0] == args.model]
    if not models:
        sys.exit(f"unknown model slug {args.model!r}; choices: {[m[0] for m in MODELS]}")

    grand_done = grand_total = 0
    print(f"{'model':24s} {'progress':22s} {'done/total':>14s} {'err':>6s} {'yes/no/unk':>16s}")
    print("-" * 88)
    for slug, name, applicable in models:
        d = RESULTS / slug
        done = total = err = 0
        verd: Counter = Counter()
        detail = []
        for task, tr, expected in applicable:
            p = d / f"{task}_{tr}_ecot.csv"
            r = count_rows(p)
            total += expected
            n = r["n"] if r else 0
            e = r["err"] if r else 0
            done += n
            err += e
            if r:
                verd.update(r["verdicts"])
            detail.append((task, tr, n, expected, e))
        pct = 100 * done / total if total else 0.0
        vs = f"{verd.get('yes', 0)}/{verd.get('no', 0)}/{verd.get('unknown', 0)}"
        print(f"{name:24s} [{bar(done, total)}] {pct:5.1f}%  {done:>6d}/{total:<6d} {err:>6d} {vs:>16s}")
        if args.verbose:
            for task, tr, n, expected, e in detail:
                flag = "" if n == expected else ("  <-- pending" if n < expected else "  <-- MISMATCH")
                print(f"    {task + '/' + tr:20s} {n:>5d}/{expected:<5d}  err={e}{flag}")
        grand_done += done
        grand_total += total

    print("-" * 88)
    pct = 100 * grand_done / grand_total if grand_total else 0.0
    print(f"{'TOTAL (excl. BanglaLLaMA)':24s} [{bar(grand_done, grand_total)}] {pct:5.1f}%  {grand_done:>6d}/{grand_total:<6d}")

    for _, name in EXCLUDED:
        print(f"\n(excluded, not counted) {name}")

    tmux_state = sh("tmux has-session -t ecot 2>/dev/null && echo alive || echo none")
    gpu = sh("nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader 2>/dev/null")
    print(f"\ntmux 'ecot' session: {tmux_state or 'unknown'}   |   GPU memory: {gpu or 'unknown'}")

    if args.watch:
        candidates = glob.glob(str(RESULTS / "*" / "*_ecot.csv"))
        if not candidates:
            print("\n(no result CSVs found to watch)")
            return
        latest = max(candidates, key=lambda p: os.path.getmtime(p))
        print(f"\nwatching {Path(latest).relative_to(ROOT)} for 30s ...")
        r1 = count_rows(Path(latest))
        n1, t1 = (r1["n"] if r1 else 0), time.time()
        time.sleep(30)
        r2 = count_rows(Path(latest))
        n2, t2 = (r2["n"] if r2 else 0), time.time()
        d, dt = n2 - n1, t2 - t1
        rate = dt / max(d, 1)
        print(f"  rows {n1} -> {n2}  (+{d}) in {dt:.0f}s  =>  {rate:.1f} s/row")


if __name__ == "__main__":
    main()
