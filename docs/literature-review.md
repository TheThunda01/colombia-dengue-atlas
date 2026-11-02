# Focused source-feasibility review

This first-release review asked whether official public resources support reproducible departmental dengue comparisons over several complete years. It is a practical dataset assessment, **not a systematic literature review**, PRESS review, or exhaustive review of dengue epidemiology.

## Sources and design consequences

**INS/Sivigila.** The licensed national open-data dataset supplies municipality/year/epidemiological-week/event aggregates through a documented API. Actual 2019–2022 downloads support a consistent department panel and preserve original bytes. The routine workbook investigation found different totals, so those versions were not mixed. Event categories remain separate; metadata does not resolve the underlying onset-versus-notification date assignment. See [INS assessment](ins-source.md).

**DANE.** A single revised department population series supplies year-specific total-population denominators. Official reference geometry supports a code-based join and a display map. Neither a total-population denominator nor a current reference boundary reconstructs population-at-risk incidence or historical geography. See [DANE assessment](dane-source.md).

**PAHO.** The legacy dengue page omits Colombia from its subnational menu, but the newer ARBO country profile includes departmental views. Representative extracts contain national weekly and annual indicators plus a current departmental map. Thus absence from the old menu is not evidence of absence of subnational data. Unresolved historical filters, denominator semantics, and revision alignment prevented combining these observations with INS. See [PAHO assessment](paho-source-assessment.md).

## Result and remaining questions

The supported first-release design uses INS aggregates, DANE population, and DANE display boundaries. It supports descriptive recorded-case comparisons with explicit missingness. Resolving source date semantics, adding newer comparable years, and evaluating a documented at-risk denominator are future evidence tasks. The [search log](search-log.json) records the PAHO investigator's actual queries and inspected URLs; other retrieval evidence remains in the source manifests.
