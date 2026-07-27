#!/usr/bin/env bash
set -euo pipefail

COMPETITION_ROOT="${BB_COMPETITION_ROOT:-$HOME/buildbench_competition}"
WEBSITE_ROOT="${BB_WEBSITE_ROOT:-$COMPETITION_ROOT/buildbench-website}"
STARTER_ROOT="${BB_STARTER_KIT_ROOT:-$COMPETITION_ROOT/buildbench-starter-kit}"
VALIDATOR_ROOT="${BB_VALIDATOR_ROOT:-$COMPETITION_ROOT/docker-validator}"
SOURCE_CASE="${BB_FE4_SOURCE_CASE:-$COMPETITION_ROOT/workspaces/linyihang/fe3-pilot/case}"
AGENT_ZIP="${BB_FE4_AGENT_ZIP:-$STARTER_ROOT/dist/milestone-b-first.zip}"
AGENT_IMAGE="${BB_AGENT_RUNTIME_IMAGE_DIGEST:-$(cat "$COMPETITION_ROOT/workspaces/linyihang/fe3-pilot/agent-image.txt")}"
VALIDATOR_IMAGE="${BB_VALIDATOR_IMAGE_DIGEST:-$(docker image inspect buildbench-validator-runtime:v0 --format '{{.Id}}')}"
PORT="${BB_FE4_PILOT_PORT:-8874}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ROOT="$COMPETITION_ROOT/workspaces/linyihang/fe4-pilot/$STAMP"
CASE_ROOT="$RUN_ROOT/case-store"
DATA_ROOT="$RUN_ROOT/runtime-data"
OUTPUT_ROOT="$RUN_ROOT/evaluation-output"
DATABASE="$DATA_ROOT/evaluations.sqlite3"
BASE_URL="http://127.0.0.1:$PORT"
SERVER_PID=""

cleanup() {
  if [[ -n "$SERVER_PID" ]]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

for required in \
  "$WEBSITE_ROOT/backend/server.py" \
  "$STARTER_ROOT/bb" \
  "$VALIDATOR_ROOT/bin/build-case-docker" \
  "$SOURCE_CASE/manifest.json" \
  "$AGENT_ZIP"; do
  [[ -e "$required" ]] || {
    echo "missing trusted pilot input: $required" >&2
    exit 2
  }
done

mkdir -p "$CASE_ROOT" "$DATA_ROOT" "$OUTPUT_ROOT"
CASE_IDS=(
  "hello-fe4-a"
  "hello-fe4-b"
  "hello-fe4-c"
)
for case_id in "${CASE_IDS[@]}"; do
  cp -a "$SOURCE_CASE" "$CASE_ROOT/$case_id"
  python3 -c '
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["case_id"] = sys.argv[2]
path.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
' "$CASE_ROOT/$case_id/manifest.json" "$case_id"
done

export BB_FULL_EVALUATION_ENABLED=1
export BB_ALLOW_UNSAFE_VALIDATOR=1
export BB_CASE_SET_CASES="$(IFS=,; echo "${CASE_IDS[*]}")"
export BB_CASE_SET_VERSION="fe4-trusted-pilot-$STAMP"
export BB_AGENT_RUNTIME_IMAGE_DIGEST="$AGENT_IMAGE"
export BB_VALIDATOR_IMAGE_DIGEST="$VALIDATOR_IMAGE"
export BB_EVALUATION_FEEDBACK_POLICY="public_validation"
export BB_WEB_DATA_ROOT="$DATA_ROOT"
export BB_EVALUATION_DB="$DATABASE"
export BB_STARTER_KIT_ROOT="$STARTER_ROOT"

cd "$WEBSITE_ROOT"
python3 -m backend.server \
  --host 127.0.0.1 \
  --port "$PORT" \
  --website-root "$WEBSITE_ROOT" \
  --starter-kit "$STARTER_ROOT" \
  --data-root "$DATA_ROOT" \
  --smoke-workers 1 \
  --evaluation-db "$DATABASE" \
  >"$RUN_ROOT/web.log" 2>&1 &
SERVER_PID="$!"

for _ in $(seq 1 30); do
  if curl --fail --silent "$BASE_URL/api/health" >"$RUN_ROOT/health.json"; then
    break
  fi
  sleep 1
done
curl --fail --silent "$BASE_URL/api/health" >/dev/null

curl --fail --silent \
  -H "Content-Type: application/zip" \
  -H "X-Agent-Filename: agent-submission.zip" \
  --data-binary "@$AGENT_ZIP" \
  "$BASE_URL/api/submissions" \
  >"$RUN_ROOT/submission.json"
SUBMISSION_ID="$(
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' \
    "$RUN_ROOT/submission.json"
)"

curl --fail --silent \
  -X POST \
  "$BASE_URL/api/submissions/$SUBMISSION_ID/smoke-test" \
  >"$RUN_ROOT/smoke-request.json"

for _ in $(seq 1 180); do
  curl --fail --silent \
    "$BASE_URL/api/submissions/$SUBMISSION_ID" \
    >"$RUN_ROOT/submission-current.json"
  STATUS="$(
    python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' \
      "$RUN_ROOT/submission-current.json"
  )"
  case "$STATUS" in
    smoke_passed)
      break
      ;;
    failed|check_failed|infrastructure_error)
      echo "Hosted Smoke Test failed: $STATUS" >&2
      exit 1
      ;;
  esac
  sleep 2
done
[[ "$STATUS" == "smoke_passed" ]] || {
  echo "Hosted Smoke Test did not finish before the pilot deadline" >&2
  exit 1
}

curl --fail --silent \
  -X POST \
  -H "Content-Length: 0" \
  -H "Idempotency-Key: fe4-pilot-$STAMP" \
  "$BASE_URL/api/submissions/$SUBMISSION_ID/full-evaluations" \
  >"$RUN_ROOT/evaluation-created.json"
EVALUATION_ID="$(
  python3 -c '
import json
import sys
print(json.load(open(sys.argv[1]))["evaluation_id"])
' "$RUN_ROOT/evaluation-created.json"
)"

python3 -m backend.evaluation_worker \
  --database "$DATABASE" \
  --submission-root "$DATA_ROOT" \
  --case-set-root "$CASE_ROOT" \
  --output-root "$OUTPUT_ROOT" \
  --starter-kit "$STARTER_ROOT" \
  --validator-command "$VALIDATOR_ROOT/bin/build-case-docker" \
  --cleanup-image ubuntu:24.04 \
  --concurrency 3 \
  --lease-seconds 120 \
  --heartbeat-seconds 30 \
  --poll-seconds 1 \
  --agent-timeout 700 \
  --build-timeout 600 \
  --build-attempt-limit 1 \
  --infra-retry-limit 1 \
  --retry-backoff-seconds 1 \
  --trusted-development \
  --until-idle \
  >"$RUN_ROOT/worker.log" 2>&1

curl --fail --silent \
  "$BASE_URL/api/full-evaluations/$EVALUATION_ID" \
  >"$RUN_ROOT/evaluation-final.json"
curl --fail --silent \
  "$BASE_URL/api/full-evaluations/$EVALUATION_ID/result" \
  >"$RUN_ROOT/evaluation-result.json"

python3 -c '
import json
import pathlib
import sys

detail = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
result = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
assert detail["status"] == "completed", detail
assert detail["progress"]["completed"] == 3, detail
assert detail["progress"]["total"] == 3, detail
assert result["successful_cases"] == 3, result
assert result["evaluated_cases"] == 3, result
assert result["score"] == 1.0, result
' "$RUN_ROOT/evaluation-final.json" "$RUN_ROOT/evaluation-result.json"

ln -sfn "$RUN_ROOT" \
  "$COMPETITION_ROOT/workspaces/linyihang/fe4-pilot/latest"
printf 'FE-4 trusted pilot completed.\n'
printf 'Run:        %s\n' "$RUN_ROOT"
printf 'Submission: %s\n' "$SUBMISSION_ID"
printf 'Evaluation: %s\n' "$EVALUATION_ID"
printf 'Result:     %s\n' "$RUN_ROOT/evaluation-result.json"
