# Visual and teaching update — v1.1.0

Review date: 2 November 2026. Author: Brandon Huynh.

This update improves comparison and explanation while preserving the v1.0.0
INS/DANE snapshot. It adds a shared-scale annual map plate with Inkscape exports,
clearer interactive legends and selected-unit values, fixed event-specific rate
colors, accessible keyboard behavior, and a conversational annotated build guide.
The README retains the portfolio's seven-section outline and now supplies an
ordered reading path through reasoning, concepts, practical use, methods,
sources, implementation, and verification.

## Validation record

- **44 Python tests passed**, including 16 new cartographic tests for annual
  aggregates, denominators, null/zero semantics, common scale, artifact integrity,
  cross-platform line endings, and failure-safe export replacement.
- **15 Node tests passed**, including fixed event-scale bounds across full-year
  and partial-week selections, original-record reconciliation, and CSV agreement.
- **17 local Edge browser scenario groups passed**, with zero page errors and
  zero HTTP errors. Coverage includes filter/download agreement, no-data and
  empty states, fixed rate legends, persistent selected-unit availability,
  keyboard focus after selection and resizing, and mobile year-only ticks.
- All **nine rendered pages** passed **266 local-reference checks**; the five
  new pages are reachable from the site's navigation. Browser checks verified
  actual SVG/PNG/PDF bytes rather than accepting an HTML fallback with status 200.
- **92 local Markdown links** resolved. The README preserves the seven required
  portfolio sections. The build guide has 16 sections and 16 code/command blocks;
  excerpts were syntax-checked, and the Antioquia 2019 example was run using the
  shared browser model (4,980 cases; 6,518,070 residents; 76.4029843 per 100,000).
- The pinned original sources, surveillance panel, population table, and
  reference geometry have no diff from v1.0.0. Both events retain their existing
  counts and missingness rules.
- **Inkscape 1.4.4** actually exported the 3120 × 3552 PNG and vector PDF from the
  generated editable SVG. The 132-row CSV and complete export bundle verify
  against their recorded fingerprints. No Blender render, QGIS project, or
  ParaView output is claimed.

Evidence: [browser report](browser_visual_local.json),
[figure/export provenance](cartographic_plate.json),
[build report](build_validation.json), and [screenshots](../docs/screenshots/).
The preserved first-release evidence is in [RELEASE_REPORT.md](../RELEASE_REPORT.md).

## Visual and independent code review

The PNG was inspected for panel spacing, labels, the shared legend, no-data
hatching, source notes, and original island placement. Desktop and 390px mobile
screenshots were inspected for reading order and overflow. The guide's long-page
capture was checked against actual DOM content and viewport captures rather than
interpreted as a source of scientific evidence.

A separate AI code review found a breakpoint focus loss: a full page redraw
replaced focused map/ranking controls. The breakpoint handler now redraws only
the plots; browser checks verified focus in both resize directions. Review also
identified the risk of mixing new SVG with older exports and Windows/Linux line
ending differences. The verified-bundle path, staged native exports, and explicit
LF SVG output address those cases. Independent here means a separate AI review
and computational checks, not independent human epidemiological validation.

## Publication evidence

The pull request and main deployment must pass the hosted workflow before the
release is finalized. The [v1.1.0 release entry](https://github.com/TheThunda01/colombia-dengue-atlas/releases/tag/v1.1.0)
records the exact final commit, successful workflow, and live-site verification.
This source report records the local review; hosted results are associated with
that immutable release commit, avoiding a claim about a different code revision.

## Interpretation boundary

These checks address reproducibility, numeric consistency, artifact integrity,
links, and interface behavior. They do not establish complete surveillance
capture, clinical validity, causal relationships, or official incidence.
No source observations were imputed, revised, or replaced for this visual update.
