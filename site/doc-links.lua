-- Shared Markdown stays readable on GitHub. Route its links to site equivalents
-- where available, and to the source repository for the detailed reference files.
local pages = {
  ["README.md"] = "index.html", ["methods.md"] = "methods.html",
  ["sources.md"] = "data.html", ["data-dictionary.md"] = "data.html#data-dictionary",
  ["glossary.md"] = "glossary.html", ["project-context.md"] = "reasoning.html",
  ["build-guide.md"] = "build-guide.html", ["visualization-tools.md"] = "tools.html"
}
function Link(link)
  if link.target:match("^%a[%w+.-]*:") or link.target:match("^#") then return link end
  local path, fragment = link.target:match("^([^#]+)(.*)$")
  if not path or not path:match("%.md$") then return link end
  local name = path:match("([^/]+)$")
  if pages[name] then
    link.target = pages[name] .. fragment
  else
    local repository_path
    if name == "DATA_LICENSE.md" or name == "RELEASE_REPORT.md" then
      repository_path = name
    elseif path:match("reports/") then
      repository_path = path:match("(reports/.*)$")
    else
      repository_path = "docs/" .. name
    end
    link.target = "https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/" .. repository_path .. fragment
  end
  return link
end

function Pandoc(doc)
  -- The include keeps its H1 for GitHub; Quarto already renders the page title.
  if doc.meta["strip-doc-title"] then
    for index, block in ipairs(doc.blocks) do
      if block.t == "Header" and block.level == 1 then
        table.remove(doc.blocks, index)
        break
      end
    end
  end
  return doc
end
