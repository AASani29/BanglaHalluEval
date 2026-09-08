#!/usr/bin/env bash
# Auto-resume the E-CoT lab orchestrator (Tiger -> Qwen -> TituLLM) after a reboot.
#
# Installed as a @reboot crontab entry. Cron gives a minimal environment, so
# PATH is set explicitly here rather than relied upon.
#
# Safe to run at any time: it is a no-op if the `ecot` tmux session already
# exists, and run_lab_orchestrator.sh resumes row-by-row from the results CSVs, so a
# double launch cannot duplicate or corrupt work.
#
# Remove with `crontab -e` (delete the @reboot line) once the run is finished.

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
REPO="/home/bio/Desktop/BanglaHalluEval"
SESSION="ecot"
LOG_DIR="$REPO/full_ecot_run/results/_logs"

mkdir -p "$LOG_DIR"
BOOT_LOG="$LOG_DIR/resume_on_boot.log"

echo "[$(date)] resume_on_boot invoked" >> "$BOOT_LOG"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "[$(date)] session '$SESSION' already running -- nothing to do" >> "$BOOT_LOG"
  exit 0
fi

cd "$REPO" || { echo "[$(date)] cannot cd to $REPO" >> "$BOOT_LOG"; exit 1; }

# Give the GPU/driver and any display manager time to settle after boot.
sleep 45

setsid tmux new-session -d -s "$SESSION" \
  "bash full_ecot_run/scripts/run_lab_orchestrator.sh 2>&1 | tee -a '$LOG_DIR/run_lab.log'; echo EXITED=\$?; sleep 86400" \
  < /dev/null

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "[$(date)] started session '$SESSION'" >> "$BOOT_LOG"
else
  echo "[$(date)] FAILED to start session '$SESSION'" >> "$BOOT_LOG"
fi
