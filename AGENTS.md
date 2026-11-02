# Colombia Dengue Surveillance Atlas

Work in this canonical clone. Preserve raw input bytes and record SHA-256 fingerprints.
Use `uv sync --frozen` and run Python through `uv run`; never change global packages.
Author: Brandon Huynh. Public repository: TheThunda01/colombia-dengue-atlas.

Only aggregate public data belong in this repository. Never add person-level records,
credentials, environments, or private inputs. Code license and data terms are separate.
Keep source absence distinct from reported zero. Do not invent uncertainty or infer
reporting completeness from presence of rows. Never difference cumulative reports
and label those differences incident cases. Verify geographic identifiers and district
rollups before joining populations. Rates per total population are not official
population-at-risk incidence.

Build commands and current source contract are in README.md and docs/methods.md.
Site interactions must work with static GitHub Pages and project-relative paths.
Run data tests, render the site, and inspect desktop and narrow layouts for release.
Record precisely which checks ran; software tests do not validate surveillance capture.
Refresh input data deliberately; never silently replace a pinned source snapshot.
