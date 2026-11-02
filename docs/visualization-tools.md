# Choosing free visualization software

Blender could help tell a future story about Colombia's terrain or another
genuinely three-dimensional dataset. For this atlas, the most useful addition
is Inkscape: it gives us editable vector figures and dependable image exports
while Python and Plotly continue to calculate and display the surveillance
values. QGIS is a good next tool when we need to inspect geography or prepare a
more elaborate map layout.

All six tools below have free, open-source cores. The recommendations are
project design judgments; the linked official sources document capabilities
and software terms. Sources were checked on **2 November 2026**.

## What each tool would contribute

| Tool | Free software and license | Where it helps this atlas | Recommendation and limit |
| --- | --- | --- | --- |
| **Inkscape** | Free; complete application binaries are GPL-3.0-or-later. Most source files are GPL-2.0-or-later, with compatible exceptions. [Official licensing](https://gitlab.com/inkscape/inkscape/-/raw/master/COPYING) | Editable SVG artwork, consistent annotation, and command-line PNG/PDF exports. [Export documentation](https://wiki.inkscape.org/wiki/Using_the_Command_Line) | Use for the publication figure and exports. Keep calculations in code; moving a label in a graphics editor should never change a number. |
| **QGIS** | Free; GPL-2.0-or-later. [Official project](https://github.com/qgis/QGIS#free-and-open-source) | Inspect boundary attributes and coordinate systems; join tables to geometry; save styles and map layouts; export SVG/PDF. [Capabilities](https://github.com/qgis/QGIS#features) | Useful for geographic review and future editable map projects. A manually edited project needs documented inputs and steps to remain reproducible. |
| **Blender** | Free; the application as a whole is GPLv3, with compatible licenses for individual files. [Official project](https://github.com/blender/blender#license) | Modeling, rendering, and animation could support a terrain explanation or spatial scene. [Capabilities](https://github.com/blender/blender) | Optional storytelling tool. Department case counts and rates are easier to compare in the atlas's two-dimensional views. |
| **ParaView** | Free; BSD 3-Clause, with separate compatible terms for third-party components. [Official license](https://www.paraview.org/license/) | Large scientific datasets, three-dimensional fields, and scripted rendering. [Project overview](https://www.paraview.org/about/) | Consider for a future simulation or volumetric dataset. It adds little to the current department-by-week tables. |
| **Plotly Python / Plotly.js** | Free; MIT. [Python terms](https://plotly.com/python/is-plotly-free/), [JavaScript license](https://github.com/plotly/plotly.js/blob/main/LICENSE) | Browser maps, time series, tooltips, and linked interactive views; Python can also generate Plotly figures. | Keep for interactive exploration. This atlas's browser charts use Plotly.js; choosing it does not require a Plotly account or paid hosting. |
| **Quarto** | Free; current Quarto is MIT. Versions 1.3 and earlier used GPLv2. [Official FAQ](https://quarto.org/docs/faq/index.html#is-quarto-free-to-use), [current project](https://github.com/quarto-dev/quarto-cli) | Publish narrative, code, methods, figures, and references together as a website or document. [Project overview](https://quarto.org/about.html) | Keep as the publishing layer. Quarto organizes the explanation; it does not verify the source data or the interpretation. |

Plotly's free graphing libraries and the free Dash framework are separate from
commercial products such as **Dash Enterprise**, Plotly Studio, and Plotly
Cloud. None of those commercial products is needed for this static atlas.
[Plotly explains the distinction](https://plotly.com/python/is-plotly-free/).
Similarly, QGIS's donation prompt is optional; the official download remains
free without a contribution. [QGIS download information](https://qgis.org/download/)
Paid support, hosted services, optional extensions, and subscriptions should be
evaluated separately from the core application license.

## Would a Blender version be better?

Start with the question the reader needs to answer. Here that is usually
“which department has the larger value?” or “how did reported cases change
over time?” Extruding departments into columns adds height and perspective to
an already irregular map. A tall department can hide a neighboring one, and
the apparent size changes with the camera. That is the design reason for
keeping the main comparison flat and pairing geography with explicit values
and time series.

Blender becomes more useful when the third dimension carries information of
its own. A future terrain scene could introduce Colombia's elevation and
geographic setting, provided that its elevation data, units, and source rights
are documented. Terrain by itself would not demonstrate an explanation for
dengue patterns. That would require additional evidence and analysis.

If we add such a scene, it should have a clear legend, restrained lighting,
documented camera settings, and a companion two-dimensional view. Decorative
depth should never imply extra measurement precision. No Blender-rendered
surveillance result is part of this release.

## How the tools fit together

The workflow begins with the data, then the visual encoding, then the export.
That order keeps the figure connected to an auditable calculation.

1. **Calculate in Python.** Read the pinned source snapshots, validate the
   geographic keys, and produce the summary values. Preserve absent
   observations as missing. The [methods](methods.md) and
   [data dictionary](data-dictionary.md) define what a value means.
2. **Build the map and chart geometry from those values.** Use stable scales,
   legible labels, and an explicit missing-data style. If geographic inspection
   is needed, open the same boundary data and summary table in QGIS and retain
   the join key and coordinate-system settings.
3. **Use Inkscape for vector presentation and exports.** SVG retains paths and
   text as editable objects. PNG provides a convenient preview; PDF is useful
   for sharing a figure at print quality. Keep the SVG and generating script
   together, and record any manual edits so a rebuild does not silently lose
   them.
4. **Publish through Quarto and Plotly.** Put the static figure beside the
   methods and keep the interactive views available for closer inspection.
   Check the rendered site at desktop and narrow widths, including missing
   states and downloads.

This workflow requires no paid map service. It also avoids an extra application
dependency for readers: they can open the published atlas in a browser.

## Reproducing an Inkscape export

The native installation was checked with `--version` on 2 November 2026:
**Inkscape 1.4.4** (`dcaf3e7`, 2026-05-05). Blender's installed executable also
responded successfully: **Blender 5.2.3 LTS**, built 2026-10-22. Those are the
versions verified on the authoring machine, not a claim about the newest
available releases. QGIS and ParaView are recommendations here, not tools
claimed to have generated the published figures.

For a standalone SVG, a basic export looks like this. `figure.svg` is an example
input filename; replace it with the figure you intend to export.

```powershell
# First, confirm which installed Inkscape your shell will run.
inkscape --version

# Keep the SVG as the editable source and export a 300 dpi raster copy.
inkscape figure.svg --export-type=png --export-dpi=300 --export-filename=figure.png

# Export the same drawing as a PDF for sharing or placing in a document.
inkscape figure.svg --export-type=pdf --export-filename=figure.pdf
```

On Windows, a portable installation may not be on `PATH`. In that case invoke
its `bin\inkscape.com` file with PowerShell's `&` operator and a quoted full
path. The `.com` entry point gives console output, which is useful when a build
script needs to check whether an export succeeded. The command-line export
options run without opening the editing interface.
[Inkscape command-line reference](https://wiki.inkscape.org/wiki/Using_the_Command_Line)

Software licenses do not replace the terms for the underlying observations,
boundaries, fonts, or imported assets. The atlas records its data permissions
separately in [DATA_LICENSE.md](../DATA_LICENSE.md). For the reasoning behind
its visual choices, continue to the [design notes](design.md); for unfamiliar
terms, use the [glossary](glossary.md).
