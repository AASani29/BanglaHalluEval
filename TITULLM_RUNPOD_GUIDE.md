# TituLLM-3B — RunPod Step-by-Step Guide

Runs **Baseline** + **CoT** hallucination-detection with **TituLLM-3B** (Hishab; `hishab/titulm-llama-3.2-3b-v1.1`) across both tracks (ground-truth + hallucinated).

- **Baseline covers all 4 tasks:** GQA, Summarization, Reasoning, **Codemixed** — **16,000 rows**.
- **CoT covers 3 tasks (paper convention):** GQA, Summarization, Reasoning. Codemixed intentionally stays baseline-only, matching how CoT was applied for every other judge in the benchmark. **11,000 rows**.
- **Grand total per full run:** **27,000 rows**.

---

## 1. Pod configuration (cheaper than the E-CoT run — 3B model needs less GPU)

### GPU: **RTX 4090 24 GB (Community Cloud)** or **RTX A5000 24 GB**
A 3B model in bfloat16 fits in ~7 GB of VRAM plus KV cache. You do NOT need an A6000.

| Option | ≈ $/hr | Fine? |
|---|---|---|
| **RTX 4090 24 GB** community | **~$0.34–0.50** | ✅ Recommended — cheapest fit |
| RTX A5000 24 GB | ~$0.35 | ✅ Also fine |
| RTX A6000 48 GB | ~$0.49–0.79 | ⚠️ Overkill; only pick if 4090 is out of stock |

### Template
- Image: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
- **Container disk: 40 GB** (TituLLM-3B download ~6 GB + tokenizer + logs + margin)
- Volume disk: 20 GB (holds the cloned repo + result CSVs)
- **SSH terminal access: ON**
- Jupyter: OFF, Encrypt volume: OFF

### Budget expectation on RTX 4090 @ $0.35/hr

| Phase | Tasks | Rows | Approx rate (3B, 4090) | Wall-clock | Cost |
|---|---|---|---|---|---|
| Setup + dep install + model download | — | — | — | ~15 min | $0.09 |
| **Baseline** (yes/no, 1-token output) | GQA + Summ + Reasoning + **Codemix** | 16,000 | ~3–5 rows/s | ~50–90 min | $0.29–0.53 |
| **CoT** (~500-token trace + yes/no) | GQA + Summ + Reasoning (no Codemix) | 11,000 | ~0.8–1.5 rows/s | ~2–3.8 h | $0.72–1.34 |
| Shutdown / sync | — | — | — | ~5 min | $0.03 |
| **Total** | | **27,000** | | **~3.25–5.25 h** | **~$1.15–$2.00** |

Comfortably fits inside the ~$3 you had remaining. If your budget is really tight, run **baseline only** first (~$0.40) then decide whether to launch CoT.

---

## 2. Pod setup checklist (~15 min, one-time)

### 2.1 Get onto the pod
Enable **Web terminal** from the pod's Connect tab (fastest) or SSH in. Then:

```bash
cd /workspace

# Clone the repo (use your PAT if private — same pattern as before)
git clone https://Shefwef:<YOUR_PAT>@github.com/AASani29/BanglaHalluEval.git
cd BanglaHalluEval
```

### 2.2 System deps (zstd for the base image; harmless if already present)
```bash
apt-get update && apt-get install -y zstd tmux
```

### 2.3 Python deps
```bash
pip install --upgrade pandas python-dotenv
# torch 2.4.1+cu124 is already in the base image — DO NOT reinstall.
pip install transformers accelerate
```

Sanity:
```bash
python -c "import torch, transformers; print('torch', torch.__version__, 'cuda', torch.cuda.is_available()); print('transformers', transformers.__version__)"
nvidia-smi | head -15
```

Expected: `cuda True` and an `RTX 4090` (or A5000/A6000) with ~24 GB memory.

### 2.4 Pre-download the model (~5 min, ~6 GB)
Kicks the model into HuggingFace's cache so the actual runs don't spend GPU time waiting.
```bash
python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
MID = 'hishab/titulm-llama-3.2-3b-v1.1'
print('pulling', MID)
AutoTokenizer.from_pretrained(MID)
AutoModelForCausalLM.from_pretrained(MID, torch_dtype=torch.bfloat16)
print('cached OK')
"
```

If the model ID is wrong (rare), the error will name the actual candidates. Adjust to the correct Hishab ID and re-run.

### 2.5 Sanity-run — 5 rows on one task
Confirms the pipeline is wired correctly before you commit hours of compute:
```bash
python scripts/evaluate_titullm_3b.py --task gqa_gt --limit 5
head -10 scripts/results_titullm_3b/gqa_gt_labeled.csv
```

You should see 5 rows with `is_hallucinated` column populated (mostly `no` since it's ground-truth data).

---

## 3. The actual run — inside `tmux` (walk away friendly)

```bash
tmux new -s titullm
# inside tmux:
bash scripts/run_titullm_3b_full.sh
```

This wrapper does two phases sequentially:

1. **Phase 1 — Baseline** on **8** (task, track) combinations: GQA + Summ + Reasoning + Codemix, each × {GT, hallu}. ~50–90 min.
2. **Phase 2 — CoT** on **6** (task, track) combinations: GQA + Summ + Reasoning, each × {GT, hallu}. Codemix is intentionally excluded to match the paper's CoT scope. ~2–3.8 h.

Per-phase log files land in `scripts/results_titullm_3b_logs/`.

**Detach with `Ctrl-b d`** once you see progress lines like:
```
[titullm_3b] gqa_gt  total=1000  done=0  pending=1000
  [titullm_3b] gqa_gt  20/1000  rate=4.20/s  eta=3.9min  last=no
  [titullm_3b] gqa_gt  40/1000  rate=4.30/s  eta=3.7min  last=no
```

Now safe to close the browser, sleep the laptop, whatever.

### Reattaching later
```bash
tmux attach -t titullm
```

Or peek without attaching:
```bash
ls scripts/results_titullm_3b/         # baseline outputs
ls scripts/results_titullm_3b_cot/     # CoT outputs
wc -l scripts/results_titullm_3b/*.csv scripts/results_titullm_3b_cot/*.csv 2>/dev/null
tail -20 $(ls -t scripts/results_titullm_3b_logs/*.log | head -1)
```

### If a run interrupts
Both `evaluate_titullm_3b.py` and `evaluate_cot_titullm_3b.py` **resume by default** — they read the existing output CSV and skip any `id`/`source_id`/`question_id` already labeled. Just re-run the same command:
```bash
bash scripts/run_titullm_3b_full.sh
```

---

## 4. Push results + terminate (once both phases finish)

### 4.1 Verify both phases produced the expected number of files
```bash
ls scripts/results_titullm_3b/ | wc -l         # expect 8 (baseline: 4 tasks x 2 tracks)
ls scripts/results_titullm_3b_cot/ | wc -l     # expect 6 (CoT: 3 tasks x 2 tracks, no codemix)
```

Row counts should match input sizes (1000 / 3000 / 4000 per file, minus header).

Expected filenames:

| Phase | Folder | Files |
|---|---|---|
| Baseline (8 files) | `scripts/results_titullm_3b/` | `gqa_gt_labeled.csv`, `gqa_hallu_labeled.csv`, `summ_gt_labeled.csv`, `summ_hallu_labeled.csv`, `reason_gt_labeled.csv`, `reason_hallu_labeled.csv`, `codemix_gt_labeled.csv`, `codemix_hallu_labeled.csv` |
| CoT (6 files) | `scripts/results_titullm_3b_cot/` | `gqa_gt_cot.csv`, `gqa_hallu_cot.csv`, `summ_gt_cot.csv`, `summ_hallu_cot.csv`, `reason_gt_cot.csv`, `reason_hallu_cot.csv` |

### 4.2 Commit + push from the pod

```bash
cd /workspace/BanglaHalluEval
git config user.email "shefayatadib@iut-dhaka.edu"
git config user.name  "Shefwef"

git add scripts/results_titullm_3b/
git add scripts/results_titullm_3b_cot/
git add -f scripts/results_titullm_3b_logs/    # force-add if .gitignore excludes logs

git commit -m "results(titullm_3b): baseline (4 tasks) + CoT (3 tasks) x 2 tracks

Model: hishab/titulm-llama-3.2-3b-v1.1
Baseline (scripts/results_titullm_3b/):  8 CSVs
  GQA, Summarization, Reasoning, Codemix, each x GT and hallu.
CoT (scripts/results_titullm_3b_cot/):  6 CSVs
  GQA, Summarization, Reasoning, each x GT and hallu.
  (Codemix intentionally not covered by CoT, matching the paper's CoT
  scope for every other judge in the benchmark.)
Logs: scripts/results_titullm_3b_logs/"

# If push authentication fails, refresh the PAT in the remote URL:
# git remote set-url origin https://Shefwef:<NEW_PAT>@github.com/AASani29/BanglaHalluEval.git

git push origin main
```

### 4.3 Terminate the pod
RunPod dashboard → your pod → **⋯** → **Terminate** → confirm. Billing ends immediately.

**Do NOT click Stop.** Stop wipes container disk on your tier, which erases the cached model — costs you ~$0.30 in downloads next time.

---

## 5. When you come back — score locally (free)

The two new output folders slot naturally into the existing extractor scripts. From your laptop:

```bash
git pull origin main

# Compute per-task/per-track yes/no counts + A-err / B-err / BHS for each phase
# You may need to extend scripts/extract_baseline_metrics.py + extract_cot_metrics.py
# to know about the titullm_3b file paths — mirror the tigerllm_9b entries.
```

The output CSV column layout is identical to TigerLLM's outputs, so the existing metrics-extractor logic works if you register the new file paths.

---

## 6. Common pitfalls (learned from the E-CoT RunPod run)

| Pitfall | Symptom | Fix |
|---|---|---|
| Container disk too small | `no space left on device` mid-run | Set container disk ≥ 40 GB at deploy time (do NOT resize a running pod — Stop→Edit spawns a duplicate pod on some tiers) |
| Two pods running | Cost row shows 2× expected | Terminate the empty ghost pod immediately from dashboard |
| PAT expired / read-only | `Password authentication is not supported` on push | Regenerate a **classic** token with **`repo`** scope, re-set the origin URL |
| `zstd` missing | Ollama installer error (only matters if you also install Ollama) | `apt-get install -y zstd` — but you don't need Ollama for TituLLM (it's HuggingFace-only) |
| Not inside tmux | Run dies when you close the browser | Confirm the **green status bar** at bottom of terminal before detaching |
| CUDA OOM | `torch.cuda.OutOfMemoryError` | Very unlikely at 3B/bf16 on a 24 GB card, but if it happens: reduce `max_new_tokens` in the CoT script from 512 → 256 |

---

## 7. Quick reference — commands cheat sheet

```bash
# Setup (once per new pod)
apt-get update && apt-get install -y zstd tmux
pip install transformers accelerate

# Sanity — 5 rows
python scripts/evaluate_titullm_3b.py --task gqa_gt --limit 5

# Full run (baseline + CoT) inside tmux
tmux new -s titullm
bash scripts/run_titullm_3b_full.sh
# Ctrl-b d to detach

# Reattach
tmux attach -t titullm

# Progress
wc -l scripts/results_titullm_3b/*.csv scripts/results_titullm_3b_cot/*.csv 2>/dev/null

# Push + shutdown
git add scripts/results_titullm_3b* && git commit -m "..." && git push origin main
# Then Terminate the pod from the dashboard
```

---

## 8. TL;DR

1. Deploy a **RTX 4090 24 GB Community Cloud** pod with **40 GB container disk**, SSH ON.
2. `apt-get install -y zstd tmux && pip install transformers accelerate`.
3. Clone repo, pre-download TituLLM-3B, sanity-run 5 rows.
4. `tmux new -s titullm && bash scripts/run_titullm_3b_full.sh`, detach with Ctrl-b d.
5. Come back in ~3.5–5.5 hours. `scripts/results_titullm_3b/` should have 8 CSVs (all 4 tasks × 2 tracks); `scripts/results_titullm_3b_cot/` should have 6 CSVs (3 tasks × 2 tracks, no Codemix — matches paper's CoT scope).
6. Push, then Terminate the pod.

Expected cost: **~$1.15–$2.00** on a $3 remaining budget. Comfortable.
