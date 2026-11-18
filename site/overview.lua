-- Reuse the explorer's projected boundaries and the weekly panel bundled with the site.
local snapshot
local function data()
  if not snapshot then
    local path = pandoc.path.join({quarto.project.directory, "data", "atlas.json"})
    local file = assert(io.open(path, "r"))
    snapshot = pandoc.json.decode(file:read("*a"))
    file:close()
  end
  return snapshot
end

local function locator()
  local parts = {[1] = [[<figure class="overview-map"><svg viewBox="28 -5 530 560" role="img" aria-labelledby="overview-map-title overview-map-desc">
<title id="overview-map-title">Antioquia and Bogotá in Colombia</title>
<desc id="overview-map-desc">The locator map highlights Antioquia in western Colombia and hatches Bogotá to its southeast. Other departments provide geographic context.</desc>
<defs><pattern id="overview-hatch" patternUnits="userSpaceOnUse" width="4" height="4"><rect width="4" height="4" fill="#fff3da"/><path d="M-1,1 1,-1 M0,4 4,0 M3,5 5,3" stroke="#704615" stroke-width="1.3"/></pattern></defs>
<g stroke="#fcfcf7" stroke-width="0.95" stroke-linejoin="round" fill-rule="evenodd">]]}
  local locations = {}
  for _, place in ipairs(data().departments) do
    local fill = "#ccd9d4"
    if place.code == "05" then fill = "#247276" end
    if place.code == "11" then fill = "url(#overview-hatch)" end
    parts[#parts+1] = string.format('<path fill="%s" d="%s"/>', fill, place.path)
    locations[place.code] = place
  end
  local a, b = locations["05"], locations["11"]
  parts[#parts+1] = string.format([[</g>
<g fill="none" stroke="#233f44" stroke-width="1.8">
<path d="M%.2f,%.2f L203,165 H114"/><path d="M%.2f,%.2f L344,269 H394"/></g>
<circle cx="%.2f" cy="%.2f" r="3.7" fill="#fff" stroke="#224f53" stroke-width="2"/>
<circle cx="%.2f" cy="%.2f" r="10" fill="none" stroke="#84591c" stroke-width="2"/>
<g class="overview-map-label"><text x="98" y="151">Antioquia</text><text x="356" y="255">Bogotá D.C.</text></g>
</svg><figcaption>Places in the 2019 comparison. Hatching marks Bogotá’s missing records. Boundaries come from DANE’s 2025 reference map.</figcaption></figure>]],
    a.x, a.y, b.x, b.y, a.x, a.y, b.x, b.y)
  return pandoc.RawBlock("html", table.concat(parts, "\n"))
end

local function integer(value)
  return tostring(math.floor(value)):reverse():gsub("(%d%d%d)", "%1,"):reverse():gsub("^,", "")
end

local function measures(code)
  local expected, present, cases = 0, 0, 0
  for _, row in ipairs(data().rows) do
    if row.department_code == code and row.year == 2019 and row.event_code == "210" and row.week <= 52 then
      expected = expected + 1
      if type(row.cases) == "number" then
        present = present + 1
        cases = cases + row.cases
      end
    end
  end
  assert(expected == 52, "Incomplete 2019 weekly panel for department " .. code)
  local population = assert(data().population[code .. "-2019"])
  return {
    string.format("%d of %d", present, expected),
    present > 0 and integer(cases) or "Unavailable",
    integer(population),
    present > 0 and string.format("%.1f", cases * 100000 / population) or "Unavailable",
  }
end

local function comparison()
  local antioquia, bogota = measures("05"), measures("11")
  local rows = {}
  for index, label in ipairs({"Weeks with records", "Recorded cases", "Total residents", "Cases per 100,000 residents"}) do
    rows[#rows+1] = string.format('<tr><th scope="row">%s</th><td>%s</td><td>%s</td></tr>',
      label, antioquia[index], bogota[index])
  end
  return pandoc.RawBlock("html", [[<div class="overview-table-wrap"><table class="overview-table">
<caption>Dengue reports and resident population, weeks 1–52 of 2019</caption>
<thead><tr><th scope="col">Measure</th><th scope="col">Antioquia</th><th scope="col">Bogotá D.C.</th></tr></thead><tbody>]]
    .. table.concat(rows) .. "</tbody></table></div>")
end

function Div(el)
  if el.identifier == "overview-map" then return locator() end
  if el.identifier == "overview-comparison" then return comparison() end
end
