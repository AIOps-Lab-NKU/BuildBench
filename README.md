# Build-Bench Challenge website

Website, Agent submission service, and durable Full Evaluation MVP for the
Build-Bench Challenge at the ICSE 2027 Competition Track.

Published website: <https://aiops-lab-nku.github.io/BuildBench/>

## Local preview with submission API

From the website project root:

```powershell
python -m backend.server --host 127.0.0.1 --port 8765
```

On Ubuntu/WSL, the equivalent one-command launcher is:

```bash
./backend/run-server.sh
```

Then open <http://127.0.0.1:8765/>.

The backend expects the Starter Kit in the sibling directory
`../buildbench-starter-kit`. Override it when necessary:

```powershell
python -m backend.server `
  --host 127.0.0.1 `
  --port 8765 `
  --starter-kit "D:\path\to\buildbench-starter-kit"
```

Opening HTML files directly or using `python -m http.server` still previews
static content, but Agent upload and Hosted Smoke Test require
`backend.server`.

## Milestone C workflow

Create a submission with the Starter Kit:

```bash
./bb package --agent ./agents/my-agent
```

Open `my-submissions.html`, choose **Make new submission**, and select:

```text
dist/agent-submission.zip
```

The platform:

1. stores the immutable ZIP and SHA-256;
2. safely extracts it;
3. runs the Starter Kit's authoritative static checker;
4. marks a valid version `qualified`;
5. waits for the participant to request **Run Smoke Test**;
6. executes `bb test` asynchronously and displays the result.

Upload does not start a Hosted Smoke Test or Full Evaluation. After a version
passes the Hosted Smoke Test, the participant explicitly starts its one
official Full Evaluation. A separate Worker expands the hidden Case set into
durable CaseRuns, runs them concurrently, freezes the final score only after
all CaseRuns finish, and lets an administrator publish the completed result to
the versioned competition leaderboard.

Runtime data is written to `runtime-data/` and ignored by Git. Override the
location with:

```bash
export BB_WEB_DATA_ROOT=/path/to/private/runtime-data
```

The Smoke Test worker count defaults to two:

```bash
export BB_SMOKE_WORKERS=2
```

## API v0

```text
GET  /api/health
GET  /api/submissions
GET  /api/submissions/{id}
POST /api/submissions
POST /api/submissions/{id}/smoke-test
POST /api/submissions/{id}/full-evaluations
GET  /api/full-evaluations
GET  /api/full-evaluations/{id}
GET  /api/full-evaluations/{id}/events
GET  /api/full-evaluations/{id}/result
GET  /api/leaderboard

GET  /api/admin/full-evaluations/{id}
POST /api/admin/full-evaluations/{id}/recover
POST /api/admin/full-evaluations/{id}/publish
POST /api/admin/full-evaluations/{id}/revoke
```

`POST /api/submissions` accepts raw `application/zip` bytes and an optional
`X-Agent-Filename` header.

## Tests

```bash
python -m unittest discover -s backend/tests -v
node --check submissions.js
```

The server acceptance must also upload a real Milestone B ZIP and complete one
Hosted Smoke Test.

## Security status

Milestone C validates ZIP paths, sizes, symlinks, submission schema, entrypoint,
dependencies, and common credential patterns. The service should remain bound
to `127.0.0.1` during development.

The Agent runner is non-root, read-only, network-disabled, resource-limited,
and never receives the Docker Socket. Bearer-token identity, owner isolation,
administrator authorization, audit events, artifact retention, hidden-result
redaction, and versioned leaderboard publication are implemented.

Organizer-trusted demos may still use the direct Docker Validator path.
Untrusted Full Evaluation uses a one-Case, one-shot QEMU/KVM Worker selected
with `BB_VALIDATOR_ISOLATION=ephemeral_vm`. The launcher receives `/dev/kvm`,
but not the host Docker Socket, hidden Case store, outbound network, or a
reusable writable system disk. Inside the disposable guest, the Agent runs
non-root without network or Docker access; privileged package construction is
confined to that guest. Only allow-listed outputs are returned and the guest
overlay is destroyed after the Case.

Production remains fail closed unless
`BB_VALIDATOR_ISOLATION_ATTESTATION` matches the frozen Validator image, QEMU
launcher, guest image, and evaluation protocol. Rebuilding any of those
artifacts requires a new isolation smoke test, real-Case acceptance run, and
attestation. Both the API process and Full Evaluation Worker must load the
generated isolation environment before starting. The organizer must
additionally provide the frozen official Case-set version, digest and IDs,
authentication policy, and `BB_FULL_EVALUATION_ENABLED=1`; the isolation
acceptance file deliberately does not select or publish a competition dataset.

```bash
set -a
. /path/to/production-worker.env
set +a

python3 -m backend.server ...
python3 -m backend.evaluation_worker --until-idle
```

The accepted configuration is a project technical control and does not replace
an independent security audit.

The one-server authentication MVP reads bearer identities from
`BB_AUTH_TOKENS_JSON` or `BB_AUTH_TOKENS_FILE`; set `BB_AUTH_REQUIRED=1` to
reject unauthenticated API requests. Production deployments must terminate TLS
and may replace this token provider with an OIDC-aware reverse proxy.

Full Evaluation Workers run separately from the website:

```bash
./backend/run-evaluation-worker-supervised.sh
```

The website deployment must run this as a long-lived supervised process.
`--until-idle` is reserved for bounded acceptance scripts and local tests; it
must not be used for the interactive website queue. The Worker records a
process heartbeat in the shared evaluation database. `/api/health` reports
Full Evaluation unavailable when no compatible heartbeat has been observed
within `BB_WORKER_STALE_SECONDS` (15 seconds by default), and new evaluation
creation then fails with HTTP 503 instead of entering an unconsumed queue.
Set a stable, deployment-unique `BB_EVALUATION_WORKER_INSTANCE_ID` so a
supervisor restart updates the existing heartbeat record instead of briefly
advertising duplicate capacity.

Retention cleanup is dry-run by default:

```bash
python3 -m backend.retention \
  --database /private/evaluations.sqlite3 \
  --output-root /private/full-evaluations \
  --retention-days 30
```

## Languages

Every page supports English and Simplified Chinese through the `EN | 中文`
control in the header. English remains the static HTML and no-JavaScript
fallback. Chinese is applied by `i18n.js` using the page dictionary under
`i18n/`.

The selected language is stored locally and represented by `?lang=zh` in
shareable Chinese URLs. Internal page links preserve the parameter, including
when the site is opened directly from the filesystem.

When English copy changes, update the exact matching key in the corresponding
page dictionary. Keep product names, model names, architecture identifiers,
code, API fields, and formulas untranslated unless the displayed terminology
itself changes.

## Content status

The site separates verified research results from planned competition
infrastructure and uses focused pages instead of one long landing page:

- `index.html` is the competition overview and navigation hub.
- `task.html` distinguishes the 268-case paper corpus from 200 additional
  candidates that are still under validation.
- `submission.html` documents the immutable Agent ZIP, managed runtime,
  workspace contract, local test loop, and platform-generated canonical diff.
- `evaluation.html` uses Build Success Rate as the single primary ranking
  metric while keeping denominator and tie-break details visibly draft.
- `rules.html`, `timeline.html`, and `faq.html` contain participant guidance.
- `leaderboard.html` keeps paper-reported research baselines separate from
  administrator-published, version-compatible Full Evaluation results.

The Agent packaging format, exact ZIP schemas, resource and network policies,
denominator semantics, tie-breaker, final split counts, submission limits, and
deadlines remain draft or organizer-preview content. Confirm them against the
released evaluator and starter kit before removing the preview banners.

## Sources

- Competition proposal: organizer document
- Paper: <https://arxiv.org/abs/2511.00780>
- Research prototype: <https://github.com/zcyyc/Build-bench>
- ICSE 2027 Competition Track: <https://conf.researchr.org/track/icse-2027/icse-2027-competition-track>
