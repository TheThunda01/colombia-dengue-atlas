# Contributing

Use a focused branch and describe the concrete problem, changed behavior, and
validation. Read `AGENTS.md`, the source documentation, and `DATA_LICENSE.md`
before changing data or scientific labels. Keep code and data terms separate.

## Reproduce the baseline

```powershell
uv sync --frozen
uv run python scripts/build.py
uv run pytest
node --test tests/model.test.mjs
uv run python scripts/site.py preview
```

Use the preview address with
`uv run python scripts/browser_checks.py --url <preview-address>`.
Browser checks may require `uv run playwright install chromium`.
Inspect changed views at desktop and narrow widths. Exercise the affected
filters, reset, empty states, and downloads. Check actual rendered behavior;
do not substitute a screenshot of unrendered source for a browser inspection.

## Data and interpretation changes

Preserve original bytes, exact queries, retrieval/release dates, and SHA-256
fingerprints. Retrieve a prospective refresh into a new directory and inspect
its license and schema before replacing any pinned input. Follow
[the source-refresh procedure](docs/sources.md). Rebuild preparation with
`uv run python scripts/build.py --prepare` after obtaining the pinned DANE
inputs with `uv run python scripts/prepare_geography.py --download`.

Check department identifiers, district handling, duplicate keys, date/week
definitions, annual/event totals, and missing-versus-zero behavior. Confirm
that each denominator matches the case geography and year. Keep occurrence,
residence, notification, and symptom-onset definitions distinct. Do not combine
event categories or source snapshots without evidence that their definitions
and overlap are compatible.

Tests should address a failure that matters: a wrong denominator, dropped week
53, an absent observation changed to zero, doubled district totals, inconsistent
filter/export calculations, or a broken published path. Record which checks
ran and any limitations. Software checks cannot establish surveillance capture
or scientific validity by themselves.

## Publication and privacy

Only permitted public aggregate data belong here. Never commit person-level
surveillance records, credentials, environments, or unrelated private inputs.
Review the staged diff and generated assets before publication. A successful
local build is distinct from a successful Pages deployment: inspect the deployed
project URL, navigation, data loading, main controls, and downloads after release.

Source updates and scientific corrections should explain their effect on prior
results and preserve the earlier version in Git history. Keep the fixed analysis
window unless expanding it is an explicit, reviewed change with comparable data.
