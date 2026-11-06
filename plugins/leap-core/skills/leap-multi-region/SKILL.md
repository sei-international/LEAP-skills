---
name: leap-multi-region
description: Work with a LEAP area that has several regions (provinces, states, countries) through the LEAP MCP tools. Use when the user mentions a region or regions, a multi-region or multi-country model, provinces or countries in one model, a region group, a Template region, a region that inherits from another region, transmission between regions, regional imports or exports, or wants a result for one region, for all regions together ("all regions total"), or by region group. Covers how a multi-region area is organized, finding the regions and which are calculated, reading and writing expressions in one region versus its parent, region groups, imports, exports and transmission lines between regions, reading results per region, summed or by group, the LCDS country mapping, performance, and common mistakes.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_branch, get_expression, get_values, set_expression, set_expressions, show_in_leap, read_view, api_get, api_set, api_call, api_describe, search_help, read_help_topic
  tested-on: "Africa 3.0 (55 regions), LEAP 2026.9.0.18, 2026-11-06 (read-only; results were out of date, so sums over regions were not read)"
  status: draft for review
---

# Multi-region areas

An area can have several regions: one country per region in a regional study, groups of
countries in a global one, states or provinces in a national one (help: General: Regions). Each
region is a separate data dimension: the same tree, with its own data in every region, and
results for one region or summed across regions. This skill follows the rules in
`leap-expressions` (section 9, inheritance) and `leap-results` (Step 2a, regions).

## 1. How a multi-region area is organized

- **Same tree in every region.** Branches, variables, scenarios, fuels and units are shared.
  Only the expressions differ. (A branch can be hidden in some regions with Tree: Select
  Visible Branches; a hidden branch is left out of that region's calculation.)
- **One expression per branch, variable, scenario and region.** A cell is addressed by all four.
  Every tool that reads or writes an expression takes `region`; without it you get the region
  LEAP is showing (`get_area` → `selectedInLEAP`).
- **A region may inherit from a parent region** (Regions screen, column "Inherit Expressions
  from Region"). The child then needs data only where it differs from the parent. At every
  step of the scenario search LEAP looks in the active region first, then in its parent:
  Mitigation (B), Mitigation (A), Baseline (B), Baseline (A), Current Accounts (B), Current
  Accounts (A), default (help: Expression Search Example Four).
- **The "Template" pattern.** Many areas have a region named Template (or similar) that is not
  a place: every real region inherits from it and it is not calculated. Shared data go in the
  Template; a real region holds only its own numbers. The help's own example uses this pattern.
- **Calculated or not.** The Regions screen's "Calculated" column says which regions are
  calculated and shown in results. In the tools this is `get_area` → `includedInResults` and
  `api_get` `Regions("name").ResultsShown`.

## 2. Find the regions first

1. `leap_status` → is LEAP ready, is the area multi-region, are results up to date.
2. `get_area` → the list of regions with `includedInResults` and `selectedInLEAP`. Say how many
   regions there are, which one LEAP is showing, and which are not calculated. A region with
   `includedInResults` false has no results, whatever `hasResults` says for the scenario.
3. For the inheritance of one region: `api_get` `Regions("name").InheritsFromRegion` gives the
   parent region (a region that inherits from no other gives itself). Also `Abbreviation`,
   `Index`, `ID`, `Group(1)` (its group in the first region group set), `Active`.
4. `api_get` `Regions` lists only ids and names. `InheritsFromRegion` and `ResultsShown` need
   one `api_get` per region (55 calls in a large area). Sample two or three regions and the
   Template rather than reading all of them, unless the user wants the full list. Report what
   you read as a short list: region, parent, calculated.
5. The root branch is not addressable by the area's name in every area ("Africa" failed for
   Africa 3.0). Use id -1, which `get_branches` with depth 1 shows, or the exact name
   `get_branches` gives.

Tell the user before changing anything that touches every region (a Template edit, a new
region, a change to which regions are calculated: the last marks results out of date).

## 3. Reading an expression in one region versus its parent

- `get_expression` and `get_branch` (with `scenario` and `region`) return only `inherited`
  true or false; nothing names the scenario or region an expression was found in. To tell a
  region's own value from an inherited one:
  1. Read the cell in **Current Accounts** in the child region. `inherited` false means the
     child's own value; `inherited` true means it comes from the parent region, since Current
     Accounts has no parent scenario and only the region can supply it.
  2. In a **scenario**, `inherited` true may come from the parent scenario or from the parent
     region. Compare with the Current Accounts answer and with the parent region's cell in that
     scenario to tell which.
- Quirk: variables shown as `<Calculated>` read `inherited` false in Current Accounts and true
  in scenarios. Do not report them as the region's own data.
- `get_branch` with `scenario` and `region` lists every variable of a branch in that region.
- `get_values` with `region` gives the numbers by year for that region only.
- Ask for the region explicitly whenever the user names one. The region LEAP is showing may
  be the Template, whose numbers mean nothing on their own.

## 4. Writing: which region gets the change

| The user wants | Write to |
|---|---|
| A change in one province or country only | that region (`set_expression` with `region`) |
| A change in every region that does not set its own value | the parent (Template) region |
| A change in every region without exception | the parent, then check each child for its own value (section 5) |
| A new scenario's measure in several regions | `set_expressions` with one row per region |

Rules:
- Name `region` in every `set_expression` and `set_expressions` call in a multi-region area.
  Never rely on the region LEAP happens to be showing.
- `set_expression` writes the cell for that region and scenario only. Current Accounts versus
  scenario follows `leap-expressions` section 2.
- Before writing to the parent, say which regions will pick the change up: every region whose
  `InheritsFromRegion` is that parent and whose own cell is blank in that scenario (and in the
  scenarios between it and Current Accounts).
- After writing, `get_expression` in one child region and confirm `inherited` is true (or
  false, if the child is what you wrote), using the method in section 3.

## 5. The trap: a stray value in a child hides the parent's change

A cell entered in a child region hides the parent's value in that scenario and in every
scenario that inherits from it. The usual story: the user edits the Template and one region
does not move. Check the child with `get_expression` for that scenario and region; if
`inherited` is false there (and in Current Accounts, per section 3), that is why. Example (from LEAP's own testing): Africa 3.0, Benin,
Agenda 2063, Activity Level of a calibration branch held a stray 0.6787 entered by mistake,
so Benin ignored every Template change to that cell in that scenario.

To let the child inherit again, the child's cell must be **blank**, not a copy of the parent's
expression. Whether `set_expression` with an empty expression clears the cell through the tools
is **unverified** (an earlier API test could not clear an override that way); when in doubt, tell
the user which cell to clear in LEAP (Analysis view, that region and scenario, delete the
expression) and check afterwards with `get_expression`.

Also check scenarios: a value in the child's *Baseline* hides the Template's *Current Accounts*
for every scenario under Baseline, in that region only.

## 6. Region groups

Region groups exist for reporting: results summed over a group in the Results and Energy
Balance views. An area has up to four **sets** of groups (Region Group Set Names screen), each
set a different way of grouping the same regions (continents in one set, income levels in
another). A region belongs to one group in each set.

- `api_get` `NumRegionGroupSets` (how many sets), `RegionGroupSets(1)` (the groups of set 1;
  each has `Name`, `ID`, `Order`), `Regions("name").Group(1).Name` (a region's group in set 1).
- To add a group: `api_call` `RegionGroupSets(1).Add("West Africa")` (returns nothing; the group
  is then there by name). To put a region in it: `api_set` `Regions("Benin").GroupID(1)` to the
  group's `ID`. Only with the user's agreement; the area then needs saving.
- Groups cannot be deleted while a region uses them.
- Region groups do not affect calculation or inheritance; they only sum results.

## 7. Imports, exports and flows between regions

Three different mechanisms; say which the area uses. `get_expression` at the root branch
(branch "-1"), variable `Regional Trade Allowed`, tells you whether trade between regions is on
at all for a scenario (Yes/No, no year variation; visible only in multi-region areas).

**A. Trade by fractions (simulation and partial optimization scenarios).** Two variables at
the Resources branches: `In-Area Import Fraction` (what share of a region's imports comes from
other regions of the area; the rest comes from outside the area) and `In-Area Export Fraction`
(which regions supply that in-area trade; sums to 100% across regions per fuel). The fuel must be
marked "Traded Among Regions" in the Fuels screen. Low data needs; no named region-to-region
links. These two variables are hidden until `Regional Trade Allowed` is Yes: their absence at a
Resources branch means trade between regions is off, not that data are missing. Imports and
exports at the Resources branches are then trade with the world outside the model.

**B. Regional imports by named source (simulation and partial optimization).** At an output
fuel of a Transformation module, `Has Regional Imports` = Yes (editable only in the first
region and in Current Accounts) adds branches "Imports from [Region]", one per other region,
each with `Regional Import Fraction`: the share of that module's requirement for the fuel
imported from that region (0-100%, summing to at most 100%). Use when specific links matter.
The help says: do not use A and B in the same model.

**C. Transmission lines and nodes (full energy system optimization with NEMO only).** Nodes
sit in regions (`api_get` `TransmissionNodes`: `Name`, `Region`, `Fuel`, `Latitude`,
`Longitude`); candidate lines join two nodes that carry the same fuel (`TransmissionLines`:
`Name`, `FromNode`, `ToNode`, `Fuel`, `Distance`, `Enabled`). Both collections are empty while
the Transmission Networks setting (Settings: Optimization) is No. A module's Properties connect
the fuel's lines to it; then the tree under that module gains `Transmission Nodes` (variable
`Nodal Distribution`, shares summing to 100% per region) and `Transmission Lines` (`Transmission
Capacity`, a plain number, not Step or Interp; `Construction Year` 0 means a candidate line the
optimization may build; `Losses`, `Transmission Availability`, costs, `Lifetime`), plus
`Simulation Type` at the Transmission Lines category (`NetworkSimulation(Pipeline)` or
`DCOPF`). These variables show only in ESO scenarios, not in Current Accounts. Energy may flow
either way; results are positive from the From node to the To node.

Ordinary `Import Target` and `Export Target` at a module are trade with the world outside the
area, not between regions. Under ESO with `Regional Trade Allowed` = Yes and no transmission
lines, the optimizer itself chooses the trade between regions per fuel (the `Regional Trade
Allowed` variable at each Resource branch turns it on per fuel).

**Which results show flows.** Transmission results (Results view, category Transmission):
`Transmission Capacity Added`, `Transmission Energy Flow` and `Transmission Power Flow` (per time
slice), `Transmission Annual Energy Flows` (net annual flow per line). Read them at the line
branches under the module; take the exact variable names from `get_branch`, since the help's
topic titles and result names differ slightly (**unverified** which spelling `get_values`
accepts). For mechanisms A and B the flows appear in each region's `Imports` and `Exports`
results and in the Energy Balance rows Imports and Exports; a per-source breakdown for B at the
"Imports from [Region]" branches is **unverified**.

## 8. Reading results: one region, all regions, a group

| The user wants | Do |
|---|---|
| One region | `get_values` with `region` (omit it for the region LEAP is showing) |
| Several regions side by side | one `get_values` per region, or `show_in_leap` with `x_axis` or `legend` `Regions` and `select` `Regions=All`, then `read_view` |
| The total over all regions | `show_in_leap` with `select` `Regions=All` (the view sums), then `read_view` |
| The total over a region group | `show_in_leap` with `select` `Regions=<group name>`, then `read_view` |
| An energy balance for a region or all regions | `show_in_leap` `view` Energy Balance with `region` (or all regions), then `read_view` |

Rules:
- The all-regions and group sums need up-to-date results. If `leap_status` says results are
  out of date, do not open the Results view: `show_in_leap` would start a calculation. Ask the
  user first.
- Never add regions up yourself; the view's sum is LEAP's. `get_values` reads one region.
- Only calculated regions have results. A region with `includedInResults` false shows nothing;
  a Template region is normally one of these. Say so when the user asks for it.
- Say the region (or "all regions" or the group) with every number, beside unit, scenario and
  year, as `leap-results` Step 4 requires.
- Results by region in a view change what the user sees in LEAP; prefer `get_values` for a
  single number in a single region.
- Changing the shown region (`api_set` `Regions("name").Active` true) changes the user's screen
  in the Analysis, Results, Energy Balance and Sankey views; name `region` in the call instead.
- Maps: when the area is linked to a GIS shape file, results can be shown as a map by region
  (a chart type of the Results view); reading a map through `read_view` is **unverified**.
- When `search_help` returns a link that is a file path rather than a web address, give the
  user the topic's title instead of the link.

## 9. Countries and the LEAP Cloud Data Server

In an area whose scale is Multinational or Global (Settings: Scope), the Regions screen matches
each region to a country: typing a region name offers known country names, and the Abbreviation
becomes the ISO two-letter code. `api_get` `Regions("name").Abbreviation`, `CountryID`,
`Code2`, `Code3`, `CountryCode`, `IsDeveloping`, `Latitude`, `Longitude` read the match. The
match is used by the Time-Series Wizard: an LCDS link in a mapped region does not ask for the
country, so the same LCDS expression in the Template pulls each region's own national series.
The `leap-lcds` skill covers the expression itself. In a national-scale area the country is set
once on the Settings: Scope screen instead.

## 10. Performance

- Calculation time grows with the number of calculated regions: each region is calculated for
  each scenario. With 50 regions and 3 scenarios, expect a long calculation; warn the user and
  calculate only when asked. Excluding regions (Calculated column) is the user's decision, and
  changing it marks results out of date.
- Parallel calculation (an area setting) shares regions and scenarios among processors. When
  `Regional Trade Allowed` is Yes in any calculated scenario, the regions depend on one another,
  so all regions of a scenario are calculated together in one piece of work (help: Regional
  Trade Allowed). Transmission modeling adds the NEMO optimization on top.
- `RegionValue`, `RegionValueOf`, `RegionGrowth` and `RegionIndicator` in expressions read other
  regions' values; many of them link regions and can slow calculation (**unverified** how much).

## Common mistakes

- Reading or writing without `region`, so the change lands in the region LEAP is showing,
  often the Template.
- Editing the Template and reporting the change as made in every region without checking for a
  child's own value (section 5).
- Writing the parent's expression into the child as a "fix": that is an override, not
  inheritance; the next Template change will not reach it.
- Asking `get_values` for a Template or other region with `includedInResults` false.
- Adding regions up in the conversation instead of a view with `Regions=All` or a group.
- Treating `Import Target` or `Export Target` as trade between regions.
- Expecting transmission variables in Current Accounts or in a simulation scenario; they exist
  only in energy system optimization scenarios with Transmission Networks on.
- Putting `Transmission Capacity` in as Step or Interp (the help says a plain number).
- Mixing the fraction method and the regional-import method in one model.
- Changing which regions are calculated, or the active region, without telling the user.

## Example (illustrative; the write and the sums were not run against the area)

Area like Africa 3.0: 55 regions, one of them Template, from which the others inherit; all 54
country regions are marked for calculation and the Template is not; scenarios Baseline, SLCP
Mitigation, Agenda 2063. User: "Raise Kenya's household electricity intensity 10% in Agenda
2063 and show total demand for East Africa."

1. `leap_status` → ready; check whether results are up to date. If they are not, the group
   total in step 7 needs a calculation first: ask the user before opening the Results view.
   `get_area` → 55 regions, Template not `includedInResults`, Kenya calculated, LEAP is
   showing Template (`selectedInLEAP`).
2. `api_get` `Regions("Kenya").InheritsFromRegion` → Template. `Regions("Kenya").Group(1).Name`
   → East Africa (region group set 1).
3. `get_expression` branch Demand\Households\Electricity, variable Final Energy Intensity,
   region Kenya, first in Current Accounts (`inherited` true, so the value is the Template's),
   then in Agenda 2063 (`inherited` true again, and the parent region's cell matches). So Kenya
   has no value of its own anywhere.
4. Agree the change with the user, then `set_expression` same cell, `region` Kenya, scenario
   Agenda 2063, expression the Current Accounts value times 1.1 (or a reference to it, per
   `leap-expressions`). `get_expression` again → `inherited` false in Kenya, Agenda 2063.
   Other regions untouched (still `inherited` true).
5. `calculate` when the user says so; `leap_status` until done.
6. `get_values` Demand, Final Energy Demand, scenario Agenda 2063, region Kenya, with and
   without `filter` `Fuel=Electricity`, unit named.
7. `show_in_leap` Results, branch Demand, Final Energy Demand, `x_axis` Years, `legend`
   Scenarios, `select` `Regions=East Africa; Scenarios=Baseline, Agenda 2063`; `read_view`.
   Report the group total with unit, years and "summed over the East Africa region group".
