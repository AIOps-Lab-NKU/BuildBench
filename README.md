# Build-Bench Challenge website

Static preview website for the Build-Bench Challenge at the ICSE 2027
Competition Track.

Published website: <https://aiops-lab-nku.github.io/BuildBench/>

## Local preview

Open `index.html` directly, or serve the directory with any static file server.

For a local server preview from the project root:

```powershell
file-python -m http.server 8765 --directory site
```

Then open <http://127.0.0.1:8765/>.

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
