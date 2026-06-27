#!/usr/bin/env python3
"""Sample 50 rows from each BenHalluEval task for the E-CoT pilot.

Track A = ground-truth correct candidates (`BenHalluEval Ground Truth Datasets/`)
Track B = hallucinated candidates           (`Hallucination Generated Answers/`)

Reproducible via random_state=42. Writes to pilot_50_samples/data/.
"""

import argparse
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "pilot_50_samples" / "data"

SEED = 42
N = 50

SOURCES = {
    "A": {  # ground-truth pilot (expected verdict = "no")
        "dir": ROOT / "BenHalluEval Ground Truth Datasets",
        "files": {
            "qa":            "benhallueval_qa_gt_1000.csv",
            "summarization": "benhallueval_summarization_gt_1000.csv",
            "reasoning":     "benhallueval_reasoning_gt_1000.csv",
        },
        "suffix": "gt",
    },
    "B": {  # hallucinated pilot (expected verdict = "yes")
        "dir": ROOT / "Hallucination Generated Answers",
        "files": {
            "qa":            "qa_4000.csv",
            "summarization": "summarization_3000.csv",
            "reasoning":     "reasoning_1000.csv",
        },
        "suffix": "hallu",
    },
}


def sample_track(track: str) -> None:
    cfg = SOURCES[track]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for task, fname in cfg["files"].items():
        src = cfg["dir"] / fname
        df = pd.read_csv(src, on_bad_lines="skip")
        sampled = df.sample(n=N, random_state=SEED).reset_index(drop=True)
        out = OUT_DIR / f"{task}_{cfg['suffix']}_{N}.csv"
        sampled.to_csv(out, index=False)
        print(f"[{track}/{task}] {src.name} ({len(df)} rows) -> {out.relative_to(ROOT)} ({len(sampled)} rows)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", choices=["A", "B", "both"], default="both",
                    help="Which track to sample. Default: both.")
    args = ap.parse_args()
    tracks = ["A", "B"] if args.track == "both" else [args.track]
    for tr in tracks:
        sample_track(tr)


if __name__ == "__main__":
    main()
