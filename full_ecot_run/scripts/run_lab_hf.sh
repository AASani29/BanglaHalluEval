#!/usr/bin/env bash
# Lab PC (single RTX 3090, 24 GB) — E-CoT on the 4 tasks x both tracks for the
# two HuggingFace judges: TigerLLM (nf4) then TituLLM-3B (bf16).
#
# Run inside tmux so it survives a disconnect:
#   tmux new -s ecot
#   bash full_ecot_run/scripts/run_lab_hf.sh
#   Ctrl-b d   (detach)
#   tmux attach -t ecot
#
# Only one model is resident at a time — they are NOT co-located on the GPU.
# Both scripts resume from their CSVs, so re-running after an interruption is safe.
#
# Why nf4 for TigerLLM: md-nishat-008/TigerLLM-9B-it is really 12.19B params
# (Gemma3-12B shaped + SigLIP vision tower) = ~24.4 GB at bf16, which does not
# fit a 24 GB card. On a 48 GB pod GPU pass --precision bf16 instead.

set -euo pipefail
cd "$(dirname "$0")/../.."   # repo root

# Env that has transformers>=4.50 (Gemma3 support) + bitsandbytes.
PY="${PY:-/media/bio/data/dataset_prep/.conda-tigerllm/bin/python}"
# TigerLLM's 23 GB snapshot lives in the home cache and is symlinked into this hub.
export HF_HOME="${HF_HOME:-/media/bio/data/visualload/hf}"

LOG_DIR="full_ecot_run/results/_logs"
mkdir -p "$LOG_DIR"

echo "[setup] python: $PY"
"$PY" -c "import torch, transformers; print('  torch', torch.__version__, '| transformers', transformers.__version__, '| cuda', torch.cuda.is_available())"

# Ollama holds VRAM; free it before loading HuggingFace weights.
if pgrep -f "ollama serve" >/dev/null 2>&1; then
  echo "[setup] stopping ollama to free VRAM ..."
  pkill -f "ollama serve" || true
  sleep 5
fi
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader

echo ""
echo "================================================================"
echo " [1/2] TigerLLM  nf4  (~6.7 GB VRAM)   4 tasks x 2 tracks"
echo "================================================================"
ts=$(date +%Y%m%d_%H%M%S)
"$PY" -u full_ecot_run/scripts/02_run_tigerllm_9b.py \
  --task all --track both --precision nf4 \
  2>&1 | tee -a "$LOG_DIR/tigerllm_9b_nf4_${ts}.log"
echo "[done] TigerLLM finished at $(date)"

echo ""
echo "================================================================"
echo " [2/2] TituLLM-3B  bf16  (~6.4 GB VRAM)   4 tasks x 2 tracks"
echo "================================================================"
ts=$(date +%Y%m%d_%H%M%S)
"$PY" -u full_ecot_run/scripts/02_run_titullm_3b.py \
  --task all --track both \
  2>&1 | tee -a "$LOG_DIR/titullm_3b_${ts}.log"
echo "[done] TituLLM-3B finished at $(date)"

echo ""
echo "================================================================"
echo " COMPLETE"
echo "================================================================"
ls -lh full_ecot_run/results/tigerllm_9b/*.csv full_ecot_run/results/titullm_3b/*.csv 2>/dev/null || true
