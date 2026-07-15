# Build-Bench Challenge website

Static preview website for the Build-Bench Challenge at the ICSE 2027
Competition Track.

Published website: <https://aiops-lab-nku.github.io/BuildBench/>

## Local preview

Open `index.html` directly, or serve the directory with any static file server.

## Content status

The site separates verified research results from planned competition
infrastructure and uses focused pages instead of one long landing page:

- `index.html` is the competition overview and navigation hub.
- `task.html` documents the task, case anatomy, research corpus, and planned splits.
- `submission.html` documents the single Agent submission model and draft API contract.
- `evaluation.html` separates proposal-derived metrics from team-approved rules.
- `rules.html`, `timeline.html`, and `faq.html` contain participant guidance.
- `leaderboard.html` shows paper-reported research baselines until public
  competition submissions open.

The Agent packaging format, API schema, resource and network policies, exact
metrics, final split counts, submission limits, and deadlines remain draft or
organizer-preview content. Confirm them against the released evaluator and
starter kit before removing the preview banners.

## Sources

- Competition proposal: organizer document
- Paper: <https://arxiv.org/abs/2511.00780>
- Research prototype: <https://github.com/zcyyc/Build-bench>
- ICSE 2027 Competition Track: <https://conf.researchr.org/track/icse-2027/icse-2027-competition-track>
