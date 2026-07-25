# Build-Bench Challenge website

Website and Milestone C submission-service MVP for the Build-Bench Challenge
at the ICSE 2027 Competition Track.

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

Upload does not start a Hosted Smoke Test or full evaluation. Full evaluation,
hidden cases, scoring, authentication, and leaderboard updates are outside the
Milestone C MVP.

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

These checks do not make the current privileged Docker Validator safe for
arbitrary public Agent uploads. Production launch still requires
authentication, per-team authorization and quotas, hardened worker or VM
isolation, secrets management, and private hidden-Case storage.

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
- `submission.html` documents the single Agent model and the working
  `case.zip` / `result.zip` I/O envelopes.
- `evaluation.html` uses Build Success Rate as the single primary ranking
  metric while keeping denominator and tie-break details visibly draft.
- `rules.html`, `timeline.html`, and `faq.html` contain participant guidance.
- `leaderboard.html` shows paper-reported research baselines until public
  competition submissions open.

The Agent packaging format, exact ZIP schemas, resource and network policies,
denominator semantics, tie-breaker, final split counts, submission limits, and
deadlines remain draft or organizer-preview content. Confirm them against the
released evaluator and starter kit before removing the preview banners.

## Sources

- Competition proposal: organizer document
- Paper: <https://arxiv.org/abs/2511.00780>
- Research prototype: <https://github.com/zcyyc/Build-bench>
- ICSE 2027 Competition Track: <https://conf.researchr.org/track/icse-2027/icse-2027-competition-track>
