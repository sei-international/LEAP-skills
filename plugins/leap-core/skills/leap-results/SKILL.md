---
name: leap-results
description: Read, compare and present LEAP results through the LEAP MCP tools. Use when the user asks for a number, a trend, a comparison between scenarios or regions, an energy balance, emissions, costs, a chart or a table from a LEAP model, or wants a results view put on screen or exported. Covers which tool to use for which question (get_values versus show_in_leap and read_view), result variable names and filters, units and scales, when results are valid, and how to present numbers and charts honestly.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_branch, get_values, get_milestones, set_milestone, show_in_leap, read_view, view_image, export_view, save_favorite, search_help, help_contents
  tested-on: Freedonia (sample area), LEAP 2026.9.0.19
  status: draft for review
---

# Reading LEAP results

Results are the numbers LEAP calculates from the data: energy demand, outputs, capacity,
emissions, costs and many more. They exist only after a calculation and only for scenarios marked
for calculation, and they go out of date when data change.

## Step 0: Are the results valid?

`leap_status` → `resultsUpToDate`. If not, say so; `calculate` only when the user wants it (LEAP is
blocked while it runs). `get_values` never calculates and returns nothing for stale results.
`get_area` → `hasResults` per scenario; a scenario not included in results has none.

Current Accounts has no stored results. For base-year numbers, read the base year of a real
scenario. Years before the first scenario year are the same in every scenario.

## Step 1: Pick the tool

| The user wants | Use |
|---|---|
| A number or a series for one variable at one branch, one or more scenarios | `get_values` |
| The same by fuel, effect, time slice, vintage, cost category | `get_values` with `filter` |
| A table that brings dimensions together (branches × fuels, a balance, a cost-benefit summary) | `show_in_leap` to put the view on screen, then `read_view` |
| To see it in LEAP, or a saved chart | `show_in_leap` (with `favorite` for a saved chart) |
| A file to keep | `export_view` (csv, excel, png, svg) |
| A chart in the conversation | read the numbers with `get_values` or `read_view` and draw it yourself |

`view_image` is for you to check what is on screen; the user does not see it in the conversation.
Changing a view changes what the user sees in LEAP, so prefer `get_values` for single numbers.

## Step 2: Name the result variable correctly

Result variable names come from LEAP, not memory. Confirm with `search_help` (the help section
"Results Categories" has a topic per group of results; pick the hit whose title or section
matches, not the first one) or `get_branch`, which lists result variables at a branch. Ones used
most:

- Demand: `Final Energy Demand` (at any demand branch; summed below it), `Total Activity`,
  `Energy Intensity` results, and for stock branches `Stocks`, `Sales`.
- Transformation: `Requirements`, `Outputs by Output Fuel` (yearly generation; for a chart by
  process select the module's `Processes` branch with `legend` Branches, since at the module
  itself the legend shows only its children),
  `Inputs`, `Capacity`, `Reserve Margin`, `Imports`, `Exports`, `Module Balance`. The
  time-sliced results (`Energy Generation`, `Power Generation`, `Power Requirements`, curtailed
  energy and power, inputs time sliced, load shapes) need Time Slices on the X axis in a view;
  for generation by year use `Outputs by Output Fuel`.
- Percent results (`Reserve Margin`, `Planning Reserve Margin`, `Load Factor`, `Maximum
  Availability`, `Actual Availability`): read them with no `unit`; the answer's unit is `Percent`.
- Resources: `Primary Requirements`, `Indigenous Production`, `Reserves`.
- Environment: `Pollutant Loadings` (direct emissions at a branch; `filter` `Effect=...` for one
  gas) and the global warming potential totals, whose names are long and oddly spelled:
  `One_Hundred Year GWP Direct At Point of Emissions` (shown in LEAP as "100-Year GWP: Direct (At
  Point of Emissions)"), with `Twenty Year` and `Five_Hundred Year` versions, in CO2 equivalent.
  Demand branches also carry "Direct and Indirect ... Allocated to Demands" versions, which
  attribute supply-side emissions to the demands that cause them: a different question. Take
  these names from `get_branch`; the help describes the results but does not give the names.
- Costs (only when costing is switched on in the area): `Social Costs` at the root branch for the
  whole system, split with a filter such as `Cost Category=Capital` (the system's capital costs);
  cost-benefit against a baseline.

## Step 2a: Pick the branch: results add up the tree

For most result variables, the branch you name in `get_values` sets the scope: the answer is the
total over that branch and every branch below it. So you rarely need to add things up yourself:

| The user wants | Read at |
|---|---|
| Total final energy demand for the whole model | the top `Demand` branch |
| Demand of one sector, or one end use | that sector or end-use branch |
| Total emissions of a pollutant for the whole area, all sectors and supply | the root branch: the area itself, addressed by the area's name (`get_branch` "Freedonia") |
| Emissions from demand only, or from one module | the `Demand` branch, or that module |
| Output of a whole module, or of one plant | the module, or the process |

The same holds for one part of a total: `get_values` at `Demand` with `filter` `Fuel=Electricity`
gives electricity demand summed over every demand branch.

Not every variable exists at every level. Final energy demand lives at the Demand branch and
below it, not at the root or in Transformation; outputs and capacity live in Transformation
modules and processes; primary requirements at Resources; emissions at the root and at most
branches beneath it. Ask rather than guess: `get_branch` on the branch lists its result variables
(its `variablesFor` field names the scenario the list is for: the one you gave, else the one
selected in LEAP; it also gives `fuel` for a branch that has one and `feedstockFuels` and
`auxiliaryFuels` for a process), and `api_get` with `Branches("name").Variables` gives the same
list in a script-friendly form. The root and the other top branches have negative ids, and a
module's Output Fuels branch is readable by id or full name like any other. If
the variable is not in the list, go down (or up) the tree to where it is, and say so.

Regions are a separate choice. Most results can be shown for one region, summed over all
regions, or summed over a region group defined in the area. `get_values` reads one region (the one
named, or the one LEAP is showing). For all regions or a group, put the view on screen with
`show_in_leap` and `select` `Regions=All` or the group's name, then `read_view`.

## Step 3: Read with the right filters and units

- `scenarios`: name them all in one call; the comparison comes back aligned by year. A scenario
  may inherit from several additional scenarios besides its parent (`api_get`
  `Scenarios("Mitigation").AdditionalScenarios` lists them); `get_area` shows only the parent, so
  name the measures behind a package scenario from that list.
- `filter`: `Fuel=Electricity`; up to three dimensions joined by `|`, for example
  `Fuel=Diesel|Effect=Carbon Dioxide`. The dimensions it takes: Fuel, Effect, Time Slice, Cost
  Category, Module Cost Category, Capacity Type, Vintage, Output Type, Input Type, Import
  Category, Export Category, Forex Category, Region and Scenario. `Branch=` and `Year=` are
  refused with advice (name the branch and years in their own parameters). Names must be the
  area's own (`list_fuels`, `api_get Effects`); an unknown item is refused with the list of names
  LEAP has. The cost categories are Demand Activity, Demand Cost of Saved Energy, Demand Other,
  Demand Vehicles, Demand Other Stocks, Capital, Fixed O&M, Variable O&M, Transformation Module,
  Fuel Production, Fuel Imports, Fuel Exports, Fuel Secondary Production, Unmet Fuel
  Requirements, Environmental Externalities, Non Energy Sector. Sector parts need not sum to the
  root: Demand plus Transformation emissions leave out Non Energy, so read the root for a total
  and the parts for shares.
- `unit`: name it, with a scale in front where helpful (`Thousand Tonnes of Oil Equivalent`,
  `Million Metric Tonnes`). Without it you get the area's default unit; read the `unit` field in
  the answer every time. For emissions the unit field says only the mass unit; the GWP results
  are CO2 equivalent (read_view's heading shows it). `show_in_leap` takes the unit without a
  scale word (`Metric Tonne`) and LEAP picks the scale.
- `first_year`, `last_year`: a range only. For a few scattered years, take the range that covers
  them or make one call per year.
- `region`: in a multi-region area, omit it for the region LEAP is showing; name it otherwise;
  totals across regions come from views, not `get_values`.

## Step 4: Present honestly

- Give the unit and scale with every number, and the scenario and year.
- Compare scenarios from the first scenario year on. State differences as absolute and percent.
- Round to what the model supports (three significant figures is usually plenty); say when a
  difference is small compared with the model's uncertainty.
- When a number looks wrong (negative demand, a jump, a factor of 1000), say so and look for the
  cause before presenting it. A policy scenario's line that steps down in single years is usually a
  measure starting (a plant coming on line, a standard taking effect), not an error; say so and
  offer to look at the branch.
- A short table beats a paragraph of numbers. Two or three years, two or three scenarios.
- For a chart in the conversation, draw it from the numbers; say which variable, unit, scenarios
  and years it shows.

## Putting a view on screen

`show_in_leap` with `view` Results, `branch`, `variable`, `x_axis` (Years, Scenarios, Fuels,
Branches, Regions, or a combined one such as `Years & Scenarios`), `legend`, `select`
(`Scenarios=Baseline, Mitigation; Fuels=All`), `unit`, and `chart_options` (`ChartType=Line`;
`Stacked=...` is accepted only when ChartType is Bar or HorizontalBar). The answer echoes the
selection; it may say `Scenarios: All` when the scenarios you named are all that have results.
Then `read_view` to confirm, and tell the user what is on screen. The tool checks every step
and a refusal says what was wrong; the chart redraws even when the user has Auto Refresh off,
and the scenario you asked for is kept when Scenarios is not on an axis.

- **One process, technology or non-energy branch.** When the result is not stacked, the chart
  pins to that branch alone and the answer's `branchShown` names it. For a stacked result the
  tool refuses and says to put Branches on the legend or X axis and `select`
  `Branches=<name>` instead.
- **Time-sliced results** (`Energy Generation`, `Power Generation`, `Power Requirements`,
  curtailed energy and power, inputs time sliced, load shapes) need `x_axis` Time Slices,
  `Years & Time Slices`, `Scenarios & Time Slices` or `Regions & Time Slices`. With Years alone
  the tool refuses and points to `Outputs by Output Fuel` for yearly generation.
- **Milestones** (a target year, a policy start) are drawn on charts whose X axis is years
  once `chart_options` `ShowMilestones=true` is given; `get_milestones` lists the area's and
  `set_milestone` adds one (see leap-milestones).

Two rules that save wrong numbers:

- **The view keeps earlier filters.** Whatever is not named in `select` stays as it was, so a
  fuel filter left from the previous chart silently shrinks the next one. Set every dimension
  that is not on an axis (`Fuels=All; Effects=All; Regions=All`, as the result has them), and for
  bar charts the years to show (`Years=2020, 2030, 2040, 2050`), and check the heading
  `read_view` returns ("All Fuels") before trusting the table.
- **Decimals and scale.** Set `chart_options` `NumDecimals=2` (or 1 with large scales) before
  `read_view` or an export; LEAP's default rounding drops a significant figure, and LEAP re-picks
  the scale when the years or items change, so read the unit from the heading every time. Tables
  with scenarios on an axis carry Total rows and columns that add scenarios and years; ignore
  them or turn them off with `TableRowTotal=false; TableColumnTotal=false`.

**Composite dimensions on the X axis.** The X axis, and only the X axis, can hold two
dimensions at once, which gives side-by-side charts that share one Y axis: one small chart per
item of the first dimension, with the second dimension along each chart's X axis. The legend
holds a third dimension. The combinations LEAP offers depend on the result; `show_in_leap`
accepts them as `x_axis` with an ampersand: `Years & Scenarios`, `Years & Branches`,
`Years & Regions`, `Years & Fuels`, `Years & Time Slices`, `Years & Effects`,
`Scenarios & Branches`, `Scenarios & Fuels`, `Scenarios & Regions`, `Scenarios & Time Slices`,
`Scenarios & Effects`, `Fuels & Branches`, `Fuels & Regions`, `Regions & Time Slices`.

- `first_dimension_first` says which of the two is the outer grouping: with `Years &
  Scenarios`, `"true"` gives one panel per year comparing the scenarios (good for a snapshot
  of 2030 and 2050 side by side), `"false"` one panel per scenario showing the years.
- `select` limits the items of either dimension (`Years=2030, 2050; Scenarios=Baseline,
  Mitigation`); for time slices and fuels the user can also filter by season, day type or fuel
  group in LEAP's own selection box.
- When the legend already holds one of the two dimensions, LEAP moves the legend to another.
- Typical uses: fuel mix by sector in two years (`x_axis` `Years & Branches`, `legend` Fuels,
  `select` `Years=2030, 2050`); generation by plant type across scenarios in one year
  (`Scenarios & Branches`); a dispatch curve by time slice for each scenario (`Scenarios &
  Time Slices`, `legend` Branches); per-region comparison (`Scenarios & Regions`).
- In LEAP the user finds the same thing under the button below the X axis, submenu Composite
  Dimensions, with a second button for the second dimension's items and a check box for the
  plotting order; the label button sets how the two names are written on the axis (first
  dimension across the top, or both on the X axis joined by a colon).
- `read_view` returns the table behind a composite chart with both dimensions in its rows and
  columns; it is the quickest way to confirm what is on screen.

Other views: `Energy Balance` with `year` and `unit`; `Sankey`; the summary views, named as the
area lists them (`Cost-Benefit`, `Decomposition`, `MACCs`, `Affordability`; there is no view
called "Summaries"). `read_view` returns their tables.

If the view needs results that are out of date, `show_in_leap` starts a calculation on its own.
So check `leap_status` first and, when results are stale, ask the user before showing a results
view, as you would before `calculate`. After a show that calculated, `leap_status` reports under
`lastShow` how it went.

`save_favorite` keeps the chart on screen under the Favorites menu (needs "edit anything" access).
`export_view` writes it to the user's Documents\LEAP Exports folder and tells you the path; give it
to the user.

`search_help` answers each topic with `link`, the web address to give the user, and `localFile`,
the local copy for your own reading, never for the user.

## Common mistakes

- Reading results that are out of date, or for a scenario that is not calculated.
- Guessing a result variable name or a fuel name.
- Forgetting the unit or scale in the answer.
- Comparing in years before the first scenario year.
- Using a view to read one number, and so changing what the user is looking at.
- Reporting a chart picture as if the user could see it in the conversation.
- Adding up regions or fuels yourself when a filter or a view would give the total LEAP computes.
- Adding up branches yourself instead of reading the parent branch, or asking for a variable at
  a level where it does not exist (final energy demand at the root).
- Asking for `Energy Generation` by year: it is time-sliced; use `Outputs by Output Fuel`.
- Giving a `unit` for a percent result, or `Branch=` and `Year=` in `filter`.

## Example

User: "How do CO2 emissions compare between Baseline and Mitigation in 2030 and 2050?"

1. `leap_status` → results up to date. `get_branch` on the root (the area's name) → the result
   variables there, among them `One_Hundred Year GWP Direct At Point of Emissions`.
2. `get_values` root branch, that variable, `scenarios` "Baseline, Mitigation",
   `first_year` 2030, `last_year` 2050, `unit` `Million Metric Tonnes`.
3. Table: 2030 and 2050, two scenarios, difference and percent.
4. `get_values` same with `filter` `Effect=Carbon Dioxide` if the user meant CO2 alone rather than
   all gases; say which you gave.
5. Offer `show_in_leap` Results, Years & Scenarios, to see it in LEAP.
