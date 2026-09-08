#!/usr/bin/env bash
# Lab PC orchestrator -- runs the E-CoT sweep for every judge except
# BanglaLLaMA-13B (explicitly excluded), in priority order:
#   1. TigerLLM      (nf4, HuggingFace transformers)  -- 02_run_tigerllm_9b.py
#   2. DeepSeek-R1-14B (Ollama)                        -- 02_run_deepseek_r1_14b.py
#   3. Qwen2.5-32B-Instruct (Ollama)                   -- 02_run_qwen2_5_32b.py
#   4. Gemma2-27B     (Ollama)                         -- 02_run_gemma2_27b.py
#   5. TituLLM-3B     (bf16, HuggingFace transformers) -- 02_run_titullm_3b.py
#
# As of 2026-08-18/19 a teammate pushed partial results via git: DeepSeek is
# already fully complete (11000/11000, kept here only as a fast no-op
# confirmation pass) and Gemma2 is partially done (qa + summarization/gt done,
# summarization/hallu partial, reasoning not started) -- both scripts resume
# from those pulled CSVs automatically.
#
# TituLLM is placed last deliberately: v1.1 is a base model that emits ~0%
# parseable E-CoT JSON at the configured 1536-token budget, so it is a ~65h
# low-yield run that should not block real, working judges. No model's
# configuration (precision, token budget, model id, task set) is changed
# here -- this file only sequences which already-existing, unmodified
# per-model script runs when.
#
# Every phase calls a script that resumes from its own CSVs, so re-running
# this whole file after a crash/reboot is always safe: completed phases
# report todo=0 and return immediately.
#
# Run inside tmux:
#   tmux new -s ecot
#   bash full_ecot_run/scripts/run_lab_orchestrator.sh
#   Ctrl-b d

set -euo pipefail
cd "$(dirname "$0")/../.."   # repo root

PY="${PY:-/media/bio/data/dataset_prep/.conda-tigerllm/bin/python}"
export HF_HOME="${HF_HOME:-/media/bio/data/visualload/hf}"
export HF_HUB_DISABLE_XET="${HF_HUB_DISABLE_XET:-1}"

LOG_DIR="full_ecot_run/results/_logs"
mkdir -p "$LOG_DIR"

echo "[setup] python: $PY"
"$PY" -c "import torch, transformers; print('  torch', torch.__version__, '| transformers', transformers.__version__, '| cuda', torch.cuda.is_available())"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader

echo ""
echo "================================================================"
echo " [1/5] TigerLLM  nf4  (~6.7 GB VRAM)   4 tasks x 2 tracks"
echo "================================================================"
ts=$(date +%Y%m%d_%H%M%S)
"$PY" -u full_ecot_run/scripts/02_run_tigerllm_9b.py \
  --task all --track both --precision nf4 \
  2>&1 | tee -a "$LOG_DIR/tigerllm_9b_nf4_${ts}.log"
echo "[done] TigerLLM finished at $(date)"

if ! curl -s -o /dev/null -w '' "http://localhost:11434/api/tags" 2>/dev/null; then
  echo "[!] Ollama not reachable at localhost:11434 -- attempting to start it"
  nohup ollama serve > "$LOG_DIR/ollama_serve.log" 2>&1 &
  sleep 5
fi

echo ""
echo "================================================================"
echo " [2/5] DeepSeek-R1-14B  (Ollama)   -- expected no-op, already complete"
echo "================================================================"
ts=$(date +%Y%m%d_%H%M%S)
"$PY" -u full_ecot_run/scripts/02_run_deepseek_r1_14b.py \
  --task all --track both \
  2>&1 | tee -a "$LOG_DIR/deepseek_r1_14b_${ts}.log"
echo "[done] DeepSeek-R1-14B confirmed complete at $(date)"

echo ""
echo "================================================================"
echo " [3/5] Qwen2.5-32B-Instruct  (Ollama)   3 tasks x 2 tracks"
echo "================================================================"
ts=$(date +%Y%m%d_%H%M%S)
"$PY" -u full_ecot_run/scripts/02_run_qwen2_5_32b.py \
  --task all --track both \
  2>&1 | tee -a "$LOG_DIR/qwen2_5_32b_${ts}.log"
echo "[done] Qwen2.5-32B finished at $(date)"

echo ""
echo "================================================================"
echo " [4/5] Gemma2-27B  (Ollama)   resuming pulled partial results"
echo "================================================================"
ts=$(date +%Y%m%d_%H%M%S)
"$PY" -u full_ecot_run/scripts/02_run_gemma2_27b.py \
  --task all --track both \
  2>&1 | tee -a "$LOG_DIR/gemma2_27b_${ts}.log"
echo "[done] Gemma2-27B finished at $(date)"

echo ""
echo "================================================================"
echo " [5/5] TituLLM-3B  bf16  (~6.4 GB VRAM)   4 tasks x 2 tracks"
echo "================================================================"
ts=$(date +%Y%m%d_%H%M%S)
"$PY" -u full_ecot_run/scripts/02_run_titullm_3b.py \
  --task all --track both \
  2>&1 | tee -a "$LOG_DIR/titullm_3b_${ts}.log"
echo "[done] TituLLM-3B finished at $(date)"

echo ""
echo "================================================================"
echo " ORCHESTRATOR COMPLETE"
echo "================================================================"
ls -lh full_ecot_run/results/tigerllm_9b/*.csv full_ecot_run/results/deepseek_r1_14b/*.csv \
       full_ecot_run/results/qwen2_5_32b/*.csv full_ecot_run/results/gemma2_27b/*.csv \
       full_ecot_run/results/titullm_3b/*.csv 2>/dev/null || true
