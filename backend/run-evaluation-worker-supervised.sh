#!/usr/bin/env bash
set -euo pipefail

RESTART_DELAY="${BB_WORKER_RESTART_DELAY_SECONDS:-5}"

if [[ "$RESTART_DELAY" =~ ^[0-9]+$ ]] && (( RESTART_DELAY > 0 )); then
  :
else
  echo "BB_WORKER_RESTART_DELAY_SECONDS must be a positive integer" >&2
  exit 2
fi

while true; do
  set +e
  python3 -m backend.evaluation_worker "$@"
  status=$?
  set -e

  if [[ $status -eq 130 || $status -eq 143 ]]; then
    exit "$status"
  fi

  printf '%s Evaluation Worker exited with status %s; restarting in %ss\n' \
    "$(date --iso-8601=seconds)" "$status" "$RESTART_DELAY" >&2
  sleep "$RESTART_DELAY"
done
